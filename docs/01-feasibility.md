## Feasible auth patterns (pick one)

### A) Delegated user consent (what you already wrote)

* Client signs in (MFA/Conditional Access applies as per their tenant).
* You use **MSAL delegated flow** (device code is simplest for a prototype; auth code + PKCE for web).
* You store tokens securely (Key Vault) and run collection during the session.
  This matches your "MSAL device-code + refresh token stored in Key Vault" concept. 

**Pros:** fastest onboarding, "their credentials," minimal admin work
**Cons:** refresh tokens and Conditional Access can get tricky; some tenants restrict user consent.

### B) Service principal they create (recommended for enterprise clients)

* Client creates an **App Registration / Service Principal in their tenant**
* Grants your requested **Application permissions** (or uses workload identity)
* Assigns **RBAC roles** (Reader + Cost Management Reader etc.) at subscription scope
* They give you only the app identity (client ID), and you authenticate as the app

**Pros:** cleaner governance, no user refresh token handling, easy to rotate/disable
**Cons:** requires someone with permission to create/consent the app

### C) Azure Lighthouse (best for MSP-like, multi-client ops)

* Client delegates subscription access to your tenant with built-in roles
* You access with your own identities, but it is still **their controlled delegation**

**Pros:** scales well, clean offboarding, strong ops model
**Cons:** heavier setup; some orgs won't allow it

---

## Validating credentials & permissions (very feasible)

You can validate in three layers before extracting anything:

### 1) Identity validation

* Acquire token via MSAL
* Call `GET https://management.azure.com/subscriptions?api-version=...`

  * If it returns the target subscription, you know the token is valid for ARM.

### 2) RBAC/role validation (subscription scope)

* Call ARM "role assignments" or "access checks":

  * List role assignments at `/subscriptions/{subId}/providers/Microsoft.Authorization/roleAssignments`
  * Or use an access-check style call (varies by API surface)
* Confirm the user/app has at least:

  * **Reader** at subscription scope (or management group scope)
  * **Cost Management Reader**
  * **Log Analytics Reader** (only if you query LA workspaces)
    This aligns with the roles you listed. 

### 3) Capability-by-capability probe

Run quick "can I read this?" probes per API:

* Resource Graph query (inventory)
* Cost Management query/export read
* Advisor recommendations
* Policy Insights (policy states)
* Network resources listing (NSG, Public IP, VNet, Private DNS)
* (Optional) Activity Logs read if you use it

If any probe fails -> report "missing permission X" and stop.

---

## Extracting "all the data": what is realistically extractable read-only

With the roles you listed, you can reliably pull the exact collection set you described:  

### Inventory (all resources)

* **Azure Resource Graph** (fast, scalable) for resources/tags/SKUs/regions
* ARM list calls for detail where needed

### Cost (last 91 days daily)

* **Cost Management Query API** (daily granularity)
* Or read from **Cost exports / FinOps Hub** landing zone if configured (your plan already assumes this option for scale). 

### Advisor recommendations

* Advisor API is readable with Reader in many cases; you also planned this explicitly. 

### Policy compliance

* **Policy Insights**: policy state summaries, compliance counts

### Network topology signals

* NSGs, Public IPs, VNets/peerings, Private DNS zones (ARM read)

### Logs signals (if you truly need "last modified" / "idle")

* This is the one area where feasibility depends on what you mean by "logs":

  * If you only need "resource metadata," ARM might be enough.
  * If you need workspace query results, you need **Log Analytics Reader** plus workspace access.

---

## The real constraints (what can block you)

1. **User consent disabled** in the client tenant

   * Then delegated flow won't work; you need admin-consented app or service principal.

2. **Conditional Access policies** can break refresh tokens or device code flows

   * Web auth code + PKCE is usually more compatible than device code for enterprises.

3. **Cost data access** can be restricted

   * Some orgs keep billing scopes separate. You may need Cost Management Reader at the right scope (subscription vs billing).

4. **Rate limits / scale**

   * Cost Management APIs can throttle on large subs -- you already noted pagination + ADF/FinOps hub ingestion as mitigation. 

---

## Recommended "enterprise-safe" implementation path

If your goal is **commercial viability** and smooth onboarding:

1. Support **two onboarding modes**:

   * "Quick Scan" = delegated sign-in (if allowed)
   * "Enterprise" = client-created service principal + RBAC roles

2. Build a **Permissions Check** endpoint:

   * returns a checklist (Pass/Fail) per data source and the exact missing role

3. Enforce **least privilege** and scope boundaries:

   * subscriptionId partitioning and middleware enforcement (you already planned this). 

4. Use **short-lived collection sessions** + explicit retention/deletion

   * especially if you store any tokens

---
