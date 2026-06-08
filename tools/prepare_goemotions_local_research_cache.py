#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.transcript_nlp_local_research_common import GOEMOTIONS_LABELS, utc_now, write_json  # noqa: E402


DATASET_ID = "google-research-datasets/go_emotions"
HF_API_URL = f"https://huggingface.co/api/datasets/{DATASET_ID}"
HF_ROWS_URL = "https://datasets-server.huggingface.co/rows"
CONFIG = "simplified"
SPLITS = ("train", "validation", "test")
LICENSE_ID = "apache-2.0"


def _read_json_url(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{url} did not return a JSON object")
    return payload


def _card_license(payload: dict[str, Any]) -> list[str]:
    card = payload.get("cardData") if isinstance(payload.get("cardData"), dict) else {}
    value = card.get("license")
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value]
    if value:
        return [str(value).strip().lower()]
    return [str(tag).split("license:", 1)[1].lower() for tag in payload.get("tags", []) if str(tag).startswith("license:")]


def _simplified_info(payload: dict[str, Any]) -> dict[str, Any]:
    card = payload.get("cardData") if isinstance(payload.get("cardData"), dict) else {}
    infos = card.get("dataset_info") if isinstance(card.get("dataset_info"), list) else []
    for info in infos:
        if isinstance(info, dict) and info.get("config_name") == CONFIG:
            return info
    raise ValueError("GoEmotions metadata did not include the simplified config")


def validate_goemotions_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    licenses = _card_license(payload)
    if LICENSE_ID not in licenses:
        raise ValueError(f"GoEmotions license must include {LICENSE_ID}; found {licenses}")
    info = _simplified_info(payload)
    splits = {str(split.get("name")): int(split.get("num_examples", 0)) for split in info.get("splits", []) if isinstance(split, dict)}
    missing_splits = [split for split in SPLITS if split not in splits]
    if missing_splits:
        raise ValueError(f"GoEmotions simplified config missing split(s): {missing_splits}")
    feature_labels = None
    for feature in info.get("features", []):
        if isinstance(feature, dict) and feature.get("name") == "labels":
            sequence = feature.get("sequence") if isinstance(feature.get("sequence"), dict) else {}
            class_label = sequence.get("class_label") if isinstance(sequence.get("class_label"), dict) else {}
            names = class_label.get("names") if isinstance(class_label.get("names"), dict) else {}
            feature_labels = {int(key): str(value) for key, value in names.items()}
    if feature_labels != GOEMOTIONS_LABELS:
        raise ValueError("GoEmotions simplified label metadata did not match the expected 28-label mapping")
    return {"license": LICENSE_ID, "splits": splits, "labels": feature_labels}


def _rows_url(split: str, offset: int, length: int) -> str:
    query = urllib.parse.urlencode(
        {
            "dataset": DATASET_ID,
            "config": CONFIG,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )
    return f"{HF_ROWS_URL}?{query}"


def download_split_rows(split: str, out_path: Path, *, max_rows: int | None = None, page_size: int = 100) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    offset = 0
    with out_path.open("w", encoding="utf-8") as handle:
        while True:
            length = min(page_size, max_rows - row_count) if max_rows is not None else page_size
            if length <= 0:
                break
            payload = _read_json_url(_rows_url(split, offset, length))
            rows = payload.get("rows")
            if not isinstance(rows, list) or not rows:
                break
            for wrapper in rows:
                row = wrapper.get("row") if isinstance(wrapper, dict) else None
                if not isinstance(row, dict):
                    continue
                handle.write(json.dumps(row, sort_keys=True) + "\n")
                row_count += 1
                if max_rows is not None and row_count >= max_rows:
                    break
            if max_rows is not None and row_count >= max_rows:
                break
            if len(rows) < length:
                break
            offset += len(rows)
    return row_count


def build_manifest(cache_out: Path, split_counts: dict[str, int], metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": "goemotions",
        "source_tier": "goemotions_local_research_apache2",
        "dataset_id": DATASET_ID,
        "dataset_url": f"https://huggingface.co/datasets/{DATASET_ID}",
        "upstream_license_url": "https://github.com/google-research/google-research/blob/master/LICENSE",
        "license_id": LICENSE_ID,
        "license_metadata_confirmed": True,
        "config": CONFIG,
        "splits": split_counts,
        "label_names": {str(key): value for key, value in sorted(GOEMOTIONS_LABELS.items())},
        "cache_files": {split: str((cache_out / f"{split}.jsonl").resolve()) for split in split_counts},
        "raw_rows_committed": False,
        "row_commit_allowed": False,
        "commercial_training_allowed": False,
        "research_training_allowed": True,
        "production_use_allowed": False,
        "model_quality_claims_allowed": False,
        "contains_public_dataset_text": True,
        "contains_personal_data_risk": True,
        "aggregate_report_only": True,
        "content_warning": "GoEmotions contains Reddit-derived public comments. Labels are weak signals, not emotion truth.",
        "metadata_snapshot": {
            "license": metadata["license"],
            "split_examples": metadata["splits"],
        },
        "created_at": utc_now(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a local-only GoEmotions research cache after Apache-2.0 metadata confirmation.")
    parser.add_argument("--cache-out", required=True)
    parser.add_argument("--manifest-out", required=True)
    parser.add_argument("--metadata-json", help="Optional local metadata JSON for tests/offline verification.")
    parser.add_argument("--max-rows-per-split", type=int, help="Optional local smoke-test limit. Omit for full simplified splits.")
    args = parser.parse_args(argv)

    try:
        if args.metadata_json:
            metadata_payload = json.loads(Path(args.metadata_json).read_text(encoding="utf-8"))
        else:
            metadata_payload = _read_json_url(HF_API_URL)
        metadata = validate_goemotions_metadata(metadata_payload)
        cache_out = Path(args.cache_out)
        split_counts: dict[str, int] = {}
        for split in SPLITS:
            split_counts[split] = download_split_rows(
                split,
                cache_out / f"{split}.jsonl",
                max_rows=args.max_rows_per_split,
            )
        manifest = build_manifest(cache_out, split_counts, metadata)
        write_json(Path(args.manifest_out), manifest)
    except Exception as exc:
        print(f"GoEmotions local research cache preparation failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "prepared_goemotions_local_research_cache",
                "cache_out": str(Path(args.cache_out)),
                "manifest_out": str(Path(args.manifest_out)),
                "split_counts": split_counts,
                "raw_rows_committed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
