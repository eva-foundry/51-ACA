"""
51-ACA shared agent tools package.

Tool modules implement the named tool interfaces referenced by agent YAMLs in agents/.

  update_data_model  -- write scan/finding state to Cosmos (all 4 agents)
  trigger_aca_job    -- trigger an Azure Container App Job (collection/analysis/delivery)
  poll_scan_status   -- poll Cosmos until target status reached or timeout
  observability      -- opencensus-based operation tracer wired to AppInsights
"""
