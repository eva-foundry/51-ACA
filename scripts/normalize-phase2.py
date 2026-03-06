#!/usr/bin/env python3
"""
Phase 2: NORMALIZE - Reconcile and validate harvested data
    1. Reconcile WBS + Evidence + ADO data
    2. Validate consistency and detect conflicts
    3. Calculate metrics (coverage, evidence rate, MTI)
    4. Produce reconciliation.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set

class NORMALIZE:
    """Phase 2: Reconcile harvested data and validate consistency"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.eva_dir = project_root / ".eva"
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Load harvest outputs
        self.wbs_harvest = self._load_json(self.eva_dir / "session31-harvest-wbs.json")
        self.evidence_harvest = self._load_json(self.eva_dir / "session31-harvest-evidence.json")
        self.ado_harvest = self._load_json(self.eva_dir / "session31-harvest-ado.json")
        self.veritas_plan = self._load_json(self.eva_dir / "veritas-plan.json")
        
        # Output structure
        self.reconciliation = {
            "reconciliation_date": self.timestamp,
            "project_id": "51-ACA",
            "sources": ["veritas-plan.json", "session31-harvest-evidence.json", "ado-id-map.json"],
            "records": [],
            "statistics": {
                "total_stories": 0,
                "stories_with_evidence": 0,
                "evidence_coverage_%": 0,
                "consistency_score": 0,
                "conflicts_detected": 0,
                "conflicts": []
            }
        }
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Safely load JSON file"""
        try:
            if not filepath.exists():
                print(f"⚠️  Not found: {filepath.name}")
                return {}
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading {filepath.name}: {e}")
            return {}
    
    def run(self) -> bool:
        """Execute full Phase 2 NORMALIZE"""
        print("\n" + "=" * 70)
        print("PHASE 2: NORMALIZE - Reconcile and validate consistency")
        print("=" * 70)
        
        # Phase 2a: Reconcile story data
        print("\n🔄 PHASE 2A: Reconcile WBS + Evidence")
        print("=" * 70)
        self._reconcile_stories()
        
        # Phase 2b: Validate consistency
        print("\n✅ PHASE 2B: Validate consistency")
        print("=" * 70)
        self._validate_consistency()
        
        # Phase 2c: Calculate metrics
        print("\n📊 PHASE 2C: Calculate metrics")
        print("=" * 70)
        self._calculate_metrics()
        
        # Save output
        print("\n💾 Saving reconciliation data")
        print("=" * 70)
        success = self._save_reconciliation()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ PHASE 2 NORMALIZE COMPLETE")
            print("=" * 70)
            print(f"\nReconciliation summary:")
            print(f"  Total stories: {self.reconciliation['statistics']['total_stories']}")
            print(f"  Stories with evidence: {self.reconciliation['statistics']['stories_with_evidence']}")
            print(f"  Coverage: {self.reconciliation['statistics']['evidence_coverage_%']:.1f}%")
            print(f"  Consistency score: {self.reconciliation['statistics']['consistency_score']:.2f}")
            print(f"  Conflicts: {self.reconciliation['statistics']['conflicts_detected']}")
            print(f"\nNext: Run Phase 3 (LOAD)")
            print("  python scripts/load-phase3.py")
        
        return success
    
    def _reconcile_stories(self) -> None:
        """Reconcile stories from veritas-plan.json with evidence"""
        
        # Get stories from veritas-plan (canonical source)
        stories_from_veritas = {}
        if self.veritas_plan and "stories" in self.veritas_plan:
            for story in self.veritas_plan["stories"]:
                story_id = story.get("story_id")
                stories_from_veritas[story_id] = {
                    "story_id": story_id,
                    "title": story.get("title", ""),
                    "epic_id": story.get("epic_id", ""),
                    "feature_id": story.get("feature_id", ""),
                    "status": story.get("status", "UNKNOWN"),
                    "milestone": story.get("milestone", "")
                }
        
        # If veritas-plan is empty, use WBS harvest
        if not stories_from_veritas and self.wbs_harvest.get("stories"):
            for story in self.wbs_harvest["stories"]:
                story_id = story.get("story_id")
                stories_from_veritas[story_id] = story
        
        # Index evidence by story_id
        evidence_by_story = {}
        if self.evidence_harvest and "evidence_records" in self.evidence_harvest:
            for record in self.evidence_harvest["evidence_records"]:
                sid = record.get("story_id")
                if sid not in evidence_by_story:
                    evidence_by_story[sid] = []
                evidence_by_story[sid].append(record)
        
        # Reconcile each story
        for story_id, story_data in stories_from_veritas.items():
            evidence_records = evidence_by_story.get(story_id, [])
            
            reconciliation_record = {
                "story_id": story_id,
                "wbs_status": story_data.get("status"),
                "title": story_data.get("title"),
                "epic_id": story_data.get("epic_id"),
                "feature_id": story_data.get("feature_id"),
                "evidence_count": len(evidence_records),
                "evidence_types": self._aggregate_evidence_types(evidence_records),
                "has_evidence": len(evidence_records) > 0,
                "evidence_confidence": self._calculate_evidence_confidence(evidence_records),
                "consistency_score": 1.0 if evidence_records else 0.5,
                "verified": len(evidence_records) > 0
            }
            
            self.reconciliation["records"].append(reconciliation_record)
        
        print(f"✅ Reconciled {len(stories_from_veritas)} stories with evidence")
        print(f"   Stories with evidence: {sum(1 for r in self.reconciliation['records'] if r['has_evidence'])}")
    
    def _aggregate_evidence_types(self, records: List[Dict]) -> Dict[str, int]:
        """Count evidence by type"""
        type_count = {}
        for record in records:
            etype = record.get("evidence_type", "unknown")
            type_count[etype] = type_count.get(etype, 0) + 1
        return type_count
    
    def _calculate_evidence_confidence( self, records: List[Dict]) -> float:
        """Calculate confidence level based on evidence weight"""
        if not records:
            return 0.0
        
        # Weight by evidence type
        weights = {
            "code": 0.30,      # Code commit = 30%
            "test": 0.25,      # Test result = 25%
            "deployment": 0.20, # Deployment = 20%
            "receipt": 0.15,   # Receipt file = 15%
            "doc": 0.10        # Documentation = 10%
        }
        
        confidence = 0.0
        for record in records:
            etype = record.get("evidence_type", "unknown")
            weight = weights.get(etype, 0.05)
            confidence += min(weight, 1.0)  # Cap at 1.0 per evidence type
        
        # Cap total confidence at 100%
        return min(confidence / len(records), 1.0) if records else 0.0
    
    def _validate_consistency(self) -> None:
        """Validate data consistency across sources"""
        conflicts = []
        
        # Check 1: WBS status vs Evidence (if story has evidence, shouldn't be PLANNED)
        for record in self.reconciliation["records"]:
            if record["has_evidence"] and record["wbs_status"] == "PLANNED":
                conflict = {
                    "story_id": record["story_id"],
                    "conflict_type": "STATUS_EVIDENCE_MISMATCH",
                    "description": "Story marked PLANNED but has evidence",
                    "severity": "LOW"
                }
                conflicts.append(conflict)
        
        # Check 2: Evidence count consistency
        for record in self.reconciliation["records"]:
            if len(record["evidence_types"]) > 5:
                # More than 5 evidence types is unusual
                conflict = {
                    "story_id": record["story_id"],
                    "conflict_type": "UNUSUAL_EVIDENCE_COUNT",
                    "description": f"Story has {len(record['evidence_types'])} evidence types",
                    "severity": "INFO"
                }
                conflicts.append(conflict)
        
        self.reconciliation["statistics"]["conflicts_detected"] = len(conflicts)
        self.reconciliation["statistics"]["conflicts"] = conflicts
        
        print(f"✅ Consistency validation complete")
        print(f"   Conflicts detected: {len(conflicts)}")
        if conflicts:
            for c in conflicts[:5]:
                print(f"   - {c['story_id']}: {c['conflict_type']} ({c['severity']})")
            if len(conflicts) > 5:
                print(f"   ... and {len(conflicts) - 5} more")
    
    def _calculate_metrics(self) -> None:
        """Calculate overall metrics for reconciliation"""
        total = len(self.reconciliation["records"])
        with_evidence = sum(1 for r in self.reconciliation["records"] if r["has_evidence"])
        
        # Overall consistency score
        consistency_scores = [r.get("consistency_score", 0) for r in self.reconciliation["records"]]
        overall_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
        
        # Coverage
        coverage_pct = (with_evidence / total * 100) if total > 0 else 0
        
        self.reconciliation["statistics"]["total_stories"] = total
        self.reconciliation["statistics"]["stories_with_evidence"] = with_evidence
        self.reconciliation["statistics"]["evidence_coverage_%"] = coverage_pct
        self.reconciliation["statistics"]["consistency_score"] = overall_consistency
        
        # MTI calculation (multi-turn intelligence score)
        mti_components = {
            "coverage": coverage_pct / 100,  # 0-1
            "evidence_rate": (with_evidence / total) if total > 0 else 0,  # 0-1
            "consistency": overall_consistency  # 0-1
        }
        mti_score = (
            mti_components["coverage"] * 0.50 +
            mti_components["evidence_rate"] * 0.20 +
            mti_components["consistency"] * 0.30
        ) * 100  # Convert to 0-100
        
        self.reconciliation["statistics"]["mti_score"] = round(mti_score, 1)
        
        print(f"✅ Metrics calculated:")
        print(f"   Total stories: {total}")
        print(f"   With evidence: {with_evidence}")
        print(f"   Coverage: {coverage_pct:.1f}%")
        print(f"   Consistency: {overall_consistency:.2f}")
        print(f"   MTI score: {mti_score:.1f}")
    
    def _save_reconciliation(self) -> bool:
        """Save reconciliation data"""
        output_file = self.eva_dir / "session31-reconciliation.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.reconciliation, f, indent=2)
            print(f"✅ Saved: {output_file.name}")
            return True
        except Exception as e:
            print(f"❌ Error saving reconciliation: {e}")
            return False


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    normalizer = NORMALIZE(project_root)
    
    if not normalizer.run():
        sys.exit(1)
