import React from "react";

function getRoles(): string[] {
  // Production TODO: parse Entra claims from auth state.
  const raw = localStorage.getItem("aca_debug_roles") || "ACA_Admin";
  return raw.split(",").map((s) => s.trim()).filter(Boolean);
}

export function RequireRole({ anyOf, children }: { anyOf: string[]; children: React.ReactNode }) {
  const roles = getRoles();
  const ok = roles.some((r) => anyOf.includes(r));
  if (!ok) {
    return (
      <div>
        <h2>Access denied</h2>
        <p>Missing required role. Required one of: {anyOf.join(", ")}</p>
      </div>
    );
  }
  return <>{children}</>;
}
