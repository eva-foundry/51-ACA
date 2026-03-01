## Sprint 2 -- Analysis Rules

**Project**: 51-ACA (Azure Cost Advisor)
**Duration**: 2026-02-28 to 2026-03-10
**Stories**: 15
**ADO Iteration**: 51-aca\Sprint 2

---

### Goal

Implement Epic 3 analysis rules -- 12 saving opportunity detectors + infrastructure fixes (GB-02 auto-trigger, GB-03 pagination).

---

### Work Items

This sprint executes 15 work items from ADO iteration `51-aca\Sprint 2`:

1. **WI 2978** - [ACA-03-001] Load all 12 rules and run in sequence
2. **WI 2979** - [ACA-03-002] Rule 01 -- Dev Box autostop
3. **WI 2980** - [ACA-03-003] Rule 02 -- VM shutdown schedule  
4. **WI 2981** - [ACA-03-004] Rule 03 -- Disk unused detection
5. **WI 2982** - [ACA-03-005] Rule 04 -- Storage tier optimization
6. **WI 2984** - [ACA-03-007] Rule 06 -- Public IP unused
7. **WI 2985** - [ACA-03-008] Rule 07 -- Reserved instance coverage
8. **WI 2986** - [ACA-03-009] Rule 08 -- App Service plan rightsizing
9. **WI 2987** - [ACA-03-010] Rule 09 -- SQL elastic pool optimization
10. **WI 2988** - [ACA-03-011] Rule 10 -- AKS node autoscaling
11. **WI 2989** - [ACA-03-012] Rule 11 -- Cosmos RU autoscale
12. **WI 2990** - [ACA-03-013] Rule 12 -- Network egress reduction
13. **WI 2991** - [ACA-03-014] GB-02 -- Analysis auto-trigger
14. **WI 2992** - [ACA-03-015] GB-03 -- Resource Graph pagination
15. **WI 2993** - [ACA-03-016] Rule output aggregation + findings writer

---

### Execution

Sprint Agent workflow (`.github/workflows/sprint-agent.yml`) will execute all stories automatically:
- D->P->D->C->A cycle per story
- Progress comments posted here
- PRs created with AB#N tags
- Final sprint summary on completion

**Monitor**: https://github.com/eva-foundry/51-ACA/actions

**ADO Board**: https://dev.azure.com/marcopresta/51-aca/_sprints/taskboard/51-aca/51-aca/Sprint%202

---

**Status**: READY TO LAUNCH 🚀

