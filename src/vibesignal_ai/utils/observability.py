"""Runtime, cost, and pipeline-status logging helpers."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Iterator


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def estimate_tokens_from_text(text: str) -> int:
    """Cheap token estimate using a character heuristic."""
    normalized = str(text or "")
    if not normalized:
        return 0
    return max(1, round(len(normalized) / 4))


def estimate_cost_usd(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    pricing: dict[str, Any] | None,
) -> float | None:
    """Estimate LLM cost from tokens and per-1k pricing."""
    if not pricing:
        return None
    input_rate = pricing.get("input_per_1k_usd")
    output_rate = pricing.get("output_per_1k_usd")
    if input_rate is None or output_rate is None:
        return None
    input_value = float(input_tokens or 0) / 1000.0 * float(input_rate)
    output_value = float(output_tokens or 0) / 1000.0 * float(output_rate)
    return round(input_value + output_value, 6)


@dataclass
class StageRecord:
    stage_name: str
    status: str
    started_at: str
    completed_at: str | None = None
    wall_clock_seconds: float | None = None
    device: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    batch_size: int | None = None
    max_context_length: int | None = None
    cache_status: str | None = None
    cache_notes: str | None = None
    estimated_input_tokens: int | None = None
    estimated_output_tokens: int | None = None
    estimated_cost_usd: float | None = None
    notes: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class PipelineRecorder:
    route_name: str
    execution_mode: str
    stages: list[StageRecord] = field(default_factory=list)
    started_at: str = field(default_factory=_now_iso)
    run_notes: list[str] = field(default_factory=list)
    output_artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @contextmanager
    def stage(self, stage_name: str, **metadata: Any) -> Iterator[StageRecord]:
        record = StageRecord(
            stage_name=stage_name,
            status="running",
            started_at=_now_iso(),
            device=metadata.get("device"),
            model_name=metadata.get("model_name"),
            model_version=metadata.get("model_version"),
            batch_size=metadata.get("batch_size"),
            max_context_length=metadata.get("max_context_length"),
            cache_status=metadata.get("cache_status"),
            cache_notes=metadata.get("cache_notes"),
        )
        token_pricing = metadata.get("pricing")
        timer_start = time.perf_counter()
        try:
            yield record
        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)
            raise
        else:
            if record.status == "running":
                record.status = "completed"
        finally:
            record.completed_at = _now_iso()
            record.wall_clock_seconds = round(time.perf_counter() - timer_start, 6)
            record.estimated_cost_usd = estimate_cost_usd(
                input_tokens=record.estimated_input_tokens,
                output_tokens=record.estimated_output_tokens,
                pricing=token_pricing,
            )
            self.stages.append(record)

    def record_status(self, stage_name: str, *, status: str, notes: list[str] | None = None, **metadata: Any) -> None:
        record = StageRecord(
            stage_name=stage_name,
            status=status,
            started_at=_now_iso(),
            completed_at=_now_iso(),
            wall_clock_seconds=0.0,
            device=metadata.get("device"),
            model_name=metadata.get("model_name"),
            model_version=metadata.get("model_version"),
            batch_size=metadata.get("batch_size"),
            max_context_length=metadata.get("max_context_length"),
            cache_status=metadata.get("cache_status"),
            cache_notes=metadata.get("cache_notes"),
            notes=list(notes or []),
        )
        self.stages.append(record)

    def add_artifact(self, name: str, path: str | Path) -> None:
        self.output_artifacts[name] = str(path)


def _runtime_payload(recorder: PipelineRecorder) -> dict[str, Any]:
    total = sum(float(stage.wall_clock_seconds or 0.0) for stage in recorder.stages)
    return {
        "schema_version": "1.0.0",
        "route_name": recorder.route_name,
        "execution_mode": recorder.execution_mode,
        "started_at": recorder.started_at,
        "completed_at": _now_iso(),
        "total_wall_clock_seconds": round(total, 6),
        "metadata": recorder.metadata,
        "stages": [asdict(stage) for stage in recorder.stages],
    }


def _cost_payload(recorder: PipelineRecorder) -> dict[str, Any]:
    priced = [stage for stage in recorder.stages if stage.estimated_cost_usd is not None]
    total_cost = round(sum(float(stage.estimated_cost_usd or 0.0) for stage in priced), 6)
    return {
        "schema_version": "1.0.0",
        "route_name": recorder.route_name,
        "execution_mode": recorder.execution_mode,
        "estimated_total_cost_usd": total_cost,
        "priced_stage_count": len(priced),
        "stages": [
            {
                "stage_name": stage.stage_name,
                "model_name": stage.model_name,
                "estimated_input_tokens": stage.estimated_input_tokens,
                "estimated_output_tokens": stage.estimated_output_tokens,
                "estimated_cost_usd": stage.estimated_cost_usd,
            }
            for stage in recorder.stages
        ],
        "notes": [
            "Costs are estimates only.",
            "Non-LLM stages default to null cost unless a pricing formula is provided.",
        ],
    }


def _status_payload(recorder: PipelineRecorder) -> dict[str, Any]:
    overall_status = "completed"
    if any(stage.status == "failed" for stage in recorder.stages):
        overall_status = "failed"
    elif any(stage.status == "skipped" for stage in recorder.stages):
        overall_status = "completed_with_skips"
    cache_hits = sum(1 for stage in recorder.stages if stage.cache_status == "hit")
    cache_misses = sum(1 for stage in recorder.stages if stage.cache_status == "miss")
    return {
        "schema_version": "1.0.0",
        "route_name": recorder.route_name,
        "execution_mode": recorder.execution_mode,
        "overall_status": overall_status,
        "stage_statuses": {stage.stage_name: stage.status for stage in recorder.stages},
        "cache_summary": {
            "hit_count": cache_hits,
            "miss_count": cache_misses,
        },
        "output_artifacts": recorder.output_artifacts,
        "run_notes": recorder.run_notes,
        "metadata": recorder.metadata,
    }


def write_observability_artifacts(
    out_dir: str | Path,
    recorder: PipelineRecorder,
) -> dict[str, Path]:
    """Write runtime, cost, and pipeline status artifacts for a run."""
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_path = output_dir / "runtime_metrics.json"
    cost_path = output_dir / "cost_metrics.json"
    status_path = output_dir / "pipeline_status.json"
    runtime_path.write_text(json.dumps(_runtime_payload(recorder), indent=2), encoding="utf-8")
    cost_path.write_text(json.dumps(_cost_payload(recorder), indent=2), encoding="utf-8")
    status_path.write_text(json.dumps(_status_payload(recorder), indent=2), encoding="utf-8")
    recorder.add_artifact("runtime_metrics", runtime_path)
    recorder.add_artifact("cost_metrics", cost_path)
    recorder.add_artifact("pipeline_status", status_path)
    return {
        "runtime_metrics": runtime_path,
        "cost_metrics": cost_path,
        "pipeline_status": status_path,
    }
