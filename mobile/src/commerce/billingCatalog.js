import { BILLING_PRODUCTS, STORE_METADATA } from "./config.js";
import { getMonetizationReadiness } from "./monetizationReadiness.js";

export function listBillingProducts() {
  return BILLING_PRODUCTS.map((product) => ({ ...product }));
}

export function getBillingProduct(platform) {
  const normalizedPlatform = String(platform || "").trim().toLowerCase();
  const product = BILLING_PRODUCTS.find((item) => item.platform === normalizedPlatform) || null;
  return product ? { ...product } : null;
}

export function getStoreMetadata() {
  return {
    ...STORE_METADATA,
    monetizationReadiness: getMonetizationReadiness(),
    subscriptionDisclosure: { ...STORE_METADATA.subscriptionDisclosure },
  };
}
