import { createAppleStoreKitAdapter } from "./appleStoreKitAdapter.js";
import { createBillingService } from "./billingService.js";
import { createMonetizationService } from "./monetizationService.js";

let sharedMonetizationService = null;

export function getSharedMonetizationService() {
  if (sharedMonetizationService) {
    return sharedMonetizationService;
  }

  const billingService = createBillingService({
    iosAdapter: createAppleStoreKitAdapter(),
  });
  sharedMonetizationService = createMonetizationService({
    platform: "ios",
    billingService,
  });
  return sharedMonetizationService;
}
