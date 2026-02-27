## Story

<!-- Story ID (e.g. ACA-SCANS-001) and one-line description -->

Story: <!-- ACA-XXXX-000 -->
Epic:  <!-- Epic N -- Name -->

## What changed

<!-- Bullet list of files modified and why -->

-
-

## Acceptance criteria

<!-- Copy from the issue. Check each box only when you have verified it passes. -->

- [ ]
- [ ]

## Test evidence

<!-- Output of: pytest services/ -x -q -->

```
paste pytest output here
```

## Checklist

- [ ] `pytest services/ -x -q` exits 0
- [ ] No .env or secrets committed
- [ ] All Cosmos queries include `partition_key=subscriptionId`
- [ ] Tenant isolation respected (no cross-partition queries outside admin endpoints)
- [ ] Tier gating untouched (gate_findings not bypassed)
- [ ] No Unicode or emoji in any modified file
- [ ] AGENTS.md rules followed
