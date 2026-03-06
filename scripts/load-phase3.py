#!/usr/bin/env python3
"""
Phase 3: LOAD - Populate central 37-data-model with reconciled 51-ACA data
    1. Create project record
    2. Load WBS layer (281 stories)
    3. Load Evidence layer (232 proofs)
    4. Load Reconciliation layer
    5. Load Sprint/Sprint metrics
    6. Validate relationships
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class LOAD:
    """Phase 3: Load reconciled data into central model"""
    
    def __init__(self, project_root: Path, model_output_dir: Optional[Path] = None):
        self.project_root = project_root
        self.eva_dir = project_root / ".eva"
        self.model_output_dir = model_output_dir or (project_root.parent / "37-data-model" / "model")
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Load reconciliation data
        self.reconciliation = self._load_json(self.eva_dir / "session31-reconciliation.json")
        self.veritas_plan = self._load_json(self.eva_dir / "veritas-plan.json")
        
        # Model output structures
        self.model_layers = {}
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Safely load JSON file"""
        try:
            if not filepath.exists():
                return {}
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading {filepath.name}: {e}")
            return {}
    
    def run(self) -> bool:
        """Execute full Phase 3 LOAD"""
        print("\n" + "=" * 70)
        print("PHASE 3: LOAD - Populate central model with reconciled data")
        print("=" * 70)
        
        # Phase 3a: Create project record
        print("\n📝 PHASE 3A: Create project record")
        print("=" * 70)
        self._create_project_record()
        
        # Phase 3b: Load WBS layer
        print("\n📊 PHASE 3B: Load WBS layer")
        print("=" * 70)
        self._load_wbs_layer()
        
        # Phase 3c: Load Evidence layer
        print("\n🔍 PHASE 3C: Load Evidence layer")
        print("=" * 70)
        self._load_evidence_layer()
        
        # Phase 3d: Load Reconciliation layer
        print("\n♻️  PHASE 3D: Load Reconciliation layer")
        print("=" * 70)
        self._load_reconciliation_layer()
        
        # Phase 3e: Load Sprint metrics
        print("\n⏱️  PHASE 3E: Load Sprint metrics")
        print("=" * 70)
        self._load_sprint_metrics()
        
        # Phase 3f: Save all layers
        print("\n💾 PHASE 3F: Save to model files")
        print("=" * 70)
        success = self._save_model_layers()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ PHASE 3 LOAD COMPLETE")
            print("=" * 70)
            print(f"\nLoaded layers:")
            for layer_name, layer_data in self.model_layers.items():
                record_count = len(layer_data.get("records", []))
                print(f"  ✅ {layer_name}: {record_count} records")
            print(f"\nModel files location: {self.model_output_dir}")
            print(f"\nNext: Run Phase 4 (VERIFY)")
            print("  python scripts/verify-phase4.py")
        
        return success
    
    def _create_project_record(self) -> None:
        """Create project metadata record"""
        project_record = {
            "project_id": "51-ACA",
            "name": "Azure Cost Advisor",
            "description": "Multi-tenant SaaS for Azure cost optimization",
            "created_date": "2026-02-26T00:00:00Z",
            "last_updated": self.timestamp,
            "status": "Active",
            "phase": "Phase 1 -- Core Services Bootstrap",
            "governance": {
                "owner": "Marco Presta / EVA AI COE",
                "maturity": "Active",
                "ado_url": "https://dev.azure.com/EsDAICoE/51-ACA/",
                "github_url": "https://github.com/eva-foundry/51-ACA"
            }
        }
        
        self.model_layers["projects"] = {
            "layer_name": "projects",
            "project_id": "51-ACA",
            "records": [project_record]
        }
        
        print(f"✅ Created project record: 51-ACA")
    
    def _load_wbs_layer(self) -> None:
        """Load Work Breakdown Structure layer"""
        wbs_records = []
        
        # Extract stories from reconciliation data
        stories_by_epic = {}
        stories_by_feature = {}
        
        for reconciliation_record in self.reconciliation.get("records", []):
            story_id = reconciliation_record.get("story_id")
            epic_id = reconciliation_record.get("epic_id", "")
            feature_id = reconciliation_record.get("feature_id", "")
            
            # Create story record
            story_record = {
                "story_id": story_id,
                "epic_id": epic_id,
                "feature_id": feature_id,
                "title": reconciliation_record.get("title", ""),
                "wbs_status": reconciliation_record.get("wbs_status", "UNKNOWN"),
                "evidence_count": reconciliation_record.get("evidence_count", 0),
                "evidence_types": reconciliation_record.get("evidence_types", {}),
                "evidence_confidence": reconciliation_record.get("evidence_confidence", 0),
                "verified": reconciliation_record.get("verified", False),
                "last_updated": self.timestamp
            }
            
            wbs_records.append(story_record)
            
            # Track by epic and feature
            if epic_id:
                if epic_id not in stories_by_epic:
                    stories_by_epic[epic_id] = []
                stories_by_epic[epic_id].append(story_id)
            
            if feature_id:
                if feature_id not in stories_by_feature:
                    stories_by_feature[feature_id] = []
                stories_by_feature[feature_id].append(story_id)
        
        # Build hierarchy
        epics = {}
        features = {}
        
        # Extract from veritas-plan if available
        if self.veritas_plan and "epics" in self.veritas_plan:
            for epic_data in self.veritas_plan["epics"]:
                epic_id = epic_data.get("epic_id")
                epics[epic_id] = {
                    "epic_id": epic_id,
                    "title": epic_data.get("title", ""),
                    "milestone": epic_data.get("milestone", ""),
                    "status": epic_data.get("status", "UNKNOWN"),
                    "story_count": len(stories_by_epic.get(epic_id, [])),
                    "stories": stories_by_epic.get(epic_id, [])
                }
        
        self.model_layers["wbs"] = {
            "layer_name": "wbs",
            "project_id": "51-ACA",
            "record_type": "story",
            "record_count": len(wbs_records),
            "records": wbs_records
        }
        
        print(f"✅ Loaded WBS layer: {len(wbs_records)} stories")
        print(f"   Epics: {len(epics)}")
    
    def _load_evidence_layer(self) -> None:
        """Load Evidence layer"""
        evidence_records = []
        
        # Index evidence by story from reconciliation
        story_evidence = {}
        
        for record in self.reconciliation.get("records", []):
            story_id = record.get("story_id")
            if record.get("has_evidence"):
                story_evidence[story_id] = {
                    "story_id": story_id,
                    "evidence_types": record.get("evidence_types", {}),
                    "total_evidence": record.get("evidence_count", 0),
                    "confidence": record.get("evidence_confidence", 0),
                    "verified": record.get("verified", False)
                }
        
        for story_id, evidence_data in story_evidence.items():
            evidence_records.append(evidence_data)
        
        self.model_layers["evidence"] = {
            "layer_name": "evidence",
            "project_id": "51-ACA",
            "record_type": "evidence",
            "record_count": len(evidence_records),
            "records": evidence_records
        }
        
        print(f"✅ Loaded Evidence layer: {len(evidence_records)} records")
        print(f"   Stories with proof: {len(evidence_records)}")
    
    def _load_reconciliation_layer(self) -> None:
        """Load Reconciliation/Metrics layer"""
        reconciliation_records = self.reconciliation.get("records", [])
        
        reconciliation_layer = {
            "layer_name": "reconciliation",
            "project_id": "51-ACA",
            "record_type": "reconciliation",
            "record_count": len(reconciliation_records),
            "statistics": self.reconciliation.get("statistics", {}),
            "records": reconciliation_records
        }
        
        self.model_layers["reconciliation"] = reconciliation_layer
        
        stats = reconciliation_layer["statistics"]
        print(f"✅ Loaded Reconciliation layer: {len(reconciliation_records)} records")
        print(f"   Coverage: {stats.get('evidence_coverage_%', 0):.1f}%")
        print(f"   Consistency: {stats.get('consistency_score', 0):.2f}")
        print(f"   MTI Score: {stats.get('mti_score', 0):.1f}")
    
    def _load_sprint_metrics(self) -> None:
        """Load Sprint metrics (if available)"""
        sprint_records = []
        
        # Try to extract sprint info from STATUS.md or other sources
        status_md = self.project_root / "STATUS.md"
        if status_md.exists():
            try:
                content = status_md.read_text(encoding='utf-8')
                # Simple extraction - look for sprint patterns
                import re
                sprint_pattern = r'Sprint[_\-](\d+)'
                sprint_nums = set(re.findall(sprint_pattern, content))
                
                for sprint_num in sorted(sprint_nums):
                    sprint_records.append({
                        "sprint_id": f"Sprint-{sprint_num}",
                        "sprint_number": sprint_num,
                        "project_id": "51-ACA"
                    })
            except Exception as e:
                pass
        
        if sprint_records:
            self.model_layers["sprints"] = {
                "layer_name": "sprints",
                "project_id": "51-ACA",
                "record_type": "sprint",
                "record_count": len(sprint_records),
                "records": sprint_records
            }
            print(f"✅ Loaded Sprint metrics: {len(sprint_records)} sprints")
        else:
            print(f"⚠️  No sprint metrics found (optional)")
    
    def _save_model_layers(self) -> bool:
        """Save all model layers to files"""
        self.model_output_dir.mkdir(parents=True, exist_ok=True)
        
        all_ok = True
        for layer_name, layer_data in self.model_layers.items():
            try:
                output_file = self.model_output_dir / f"51-aca-{layer_name}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(layer_data, f, indent=2)
                print(f"✅ Saved: {output_file.name}")
            except Exception as e:
                print(f"❌ Error saving {layer_name}: {e}")
                all_ok = False
        
        return all_ok


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    loader = LOAD(project_root)
    
    if not loader.run():
        sys.exit(1)
