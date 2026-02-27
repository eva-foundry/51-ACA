// ACA role constants -- must match Entra ID group names exactly
export const ROLE_ADMIN   = "ACA_Admin";
export const ROLE_SUPPORT = "ACA_Support";
export const ROLE_FINOPS  = "ACA_FinOps";

// All admin surface roles
export const ADMIN_ROLES = [ROLE_ADMIN, ROLE_SUPPORT, ROLE_FINOPS] as const;

// Roles that can perform destructive actions (grant/lock/reconcile)
export const DESTRUCTIVE_ROLES = [ROLE_ADMIN, ROLE_SUPPORT] as const;

// Only ACA_Admin can initiate Stripe reconcile
export const RECONCILE_ROLES = [ROLE_ADMIN] as const;

export type AcaRole =
  | typeof ROLE_ADMIN
  | typeof ROLE_SUPPORT
  | typeof ROLE_FINOPS;
