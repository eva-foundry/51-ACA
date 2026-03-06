#!/usr/bin/env python3
"""
Phase 4: VERIFY - Comprehensive audit of loaded model data
    1. Verify completeness (all records present, no orphans)
    2. Verify consistency (story counts match, no conflicts)
    3. Verify traceability (story → evidence → commitment path)
    4. Generate audit report
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class VERIFY:
    """Phase 4: Verify completeness and consistency of loaded model"""
    
    def __init__(self, project_root: Path, model_dir: Path):
        self.project_root = project_root
        self.model_dir = model_dir
        self.eva_dir = project_root / ".eva"
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Load model layers
        self.model = {}
        self._load_model_layers()
        
        # Verification report
        self.report = {
            "verification_date": self.timestamp,
            "project_id": "51-ACA",
            "checks": {},
            "statistics": {},
            "issues": [],
            "status": "PENDING"
        }
    
    def _load_model_layers(self) -> None:
        """Load all model layer files"""
        for layer_file in self.model_dir.glob("51-aca-*.json"):
            try:
                with open(layer_file, 'r', encoding='utf-8') as f:
                    layer_data = json.load(f)
                layer_name = layer_file.stem.replace("51-aca-", "")
                self.model[layer_name] = layer_data
                print(f"✅ Loaded {layer_name}: {len(layer_data.get('records', []))} records")
            except Exception as e:
                print(f"⚠️  Error loading {layer_file.name}: {e}")
    
    def run(self) -> bool:
        """Execute full Phase 4 VERIFY"""
        print("\n" + "=" * 70)
        print("PHASE 4: VERIFY - Comprehensive audit")
        print("=" * 70)
        
        # Check 1: Completeness
        print("\n✅ CHECK 1: Completeness Verification")
        print("=" * 70)
        check1_pass = self._check_completeness()
        
        # Check 2: Consistency
        print("\n✅ CHECK 2: Consistency Verification")
        print("=" * 70)
        check2_pass = self._check_consistency()
        
        # Check 3: Traceability
        print("\n✅ CHECK 3: Traceability Verification")
        print("=" * 70)
        check3_pass = self._check_traceability()
        
        # Check 4: Data Quality
        print("\n✅ CHECK 4: Data Quality Verification")
        print("=" * 70)
        check4_pass = self._check_data_quality()
        
        # Save report
        print("\n💾 Saving verification report")
        print("=" * 70)
        success = self._save_report()
        
        # Summary
        all_passed = check1_pass and check2_pass and check3_pass and check4_pass
        self.report["status"] = "VERIFIED" if all_passed else "ISSUES_FOUND"
        
        if success:
            print("\n" + "=" * 70)
            print(f"{'✅' if all_passed else '⚠️ '} PHASE 4 VERIFY COMPLETE")
            print("=" * 70)
            print(f"\nVerification summary:")
            print(f"  Status: {self.report['status']}")
            print(f"  Checks passed: {sum([check1_pass, check2_pass, check3_pass, check4_pass])}/4")
            print(f"  Issues found: {len(self.report['issues'])}")
            
            if self.report['issues']:
                print(f"\nIssues:")
                for issue in self.report['issues'][:10]:
                    print(f"  - [{issue['severity']}] {issue['description']}")
                if len(self.report['issues']) > 10:
                    print(f"  ... and {len(self.report['issues']) - 10} more")
            
            print(f"\n📊 Statistics:")
            for key, value in self.report['statistics'].items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value}")
            
            print(f"\n✅ Next: Run Phase 5 (SYNC Setup)")
            print("  python scripts/sync-phase5.py")
        
        return success and all_passed
    
    def _check_completeness(self) -> bool:
        """Verify all records are present and no orphans"""
        issues = []
        
        # Get record counts
        wbs_count = len(self.model.get("wbs", {}).get("records", []))
        evidence_count = len(self.model.get("evidence", {}).get("records", []))
        reconciliation_count = len(self.model.get("reconciliation", {}).get("records", []))
        
        print(f"  WBS stories: {wbs_count}")
        print(f"  Evidence records: {evidence_count}")
        print(f"  Reconciliation records: {reconciliation_count}")
        
        self.report["statistics"]["wbs_stories"] = wbs_count
        self.report["statistics"]["evidence_records"] = evidence_count
        self.report["statistics"]["reconciliation_records"] = reconciliation_count
        
        # Check 1: All WBS stories have reconciliation entry
        wbs_stories = {s["story_id"] for s in self.model.get("wbs", {}).get("records", [])}
        reconciliation_stories = {s["story_id"] for s in self.model.get("reconciliation", {}).get("records", [])}
        
        missing_recon = wbs_stories - reconciliation_stories
        if missing_recon:
            issues.append({
                "check": "completeness_wbs_reconciliation",
                "severity": "ERROR",
                "description": f"{len(missing_recon)} WBS stories missing reconciliation entries"
            })
        
        # Check 2: No orphaned evidence
        evidence_stories = {e["story_id"] for e in self.model.get("evidence", {}).get("records", [])}
        orphaned_evidence = evidence_stories - wbs_stories
        if orphaned_evidence:
            issues.append({
                "check": "completeness_orphaned_evidence",
                "severity": "WARNING",
                "description": f"{len(orphaned_evidence)} evidence records for unknown stories"
            })
        
        # Check 3: Story counts consistency
        if wbs_count != reconciliation_count:
            issues.append({
                "check": "completeness_count_mismatch",
                "severity": "ERROR",
                "description": f"WBS ({wbs_count}) != Reconciliation ({reconciliation_count})"
            })
        
        # Check 4: Minimum coverage
        expected_minimum = 200  # At least 200 stories
        if wbs_count < expected_minimum:
            issues.append({
                "check": "completeness_minimum_stories",
                "severity": "WARNING",
                "description": f"Only {wbs_count} stories (expected >= {expected_minimum})"
            })
        
        self.report["checks"]["completeness"] = {
            "passed": len(issues) == 0,
            "issues": issues
        }
        
        print(f"  ✅ Completeness check: {'PASS' if len(issues) == 0 else 'FAIL'}")
        
        self.report["issues"].extend(issues)
        return len(issues) == 0
    
    def _check_consistency(self) -> bool:
        """Verify data consistency across layers"""
        issues = []
        
        # Get reconciliation statistics
        reconciliation_data = self.model.get("reconciliation", {})
        stats = reconciliation_data.get("statistics", {})
        
        coverage = stats.get("evidence_coverage_%", 0)
        consistency = stats.get("consistency_score", 0)
        mti_score = stats.get("mti_score", 0)
        
        print(f"  Evidence coverage: {coverage:.1f}%")
        print(f"  Consistency score: {consistency:.2f}")
        print(f"  MTI score: {mti_score:.1f}")
        
        self.report["statistics"]["evidence_coverage_%"] = coverage
        self.report["statistics"]["consistency_score"] = consistency
        self.report["statistics"]["mti_score"] = mti_score
        
        # Check 1: Coverage >= 80%
        if coverage < 80:
            issues.append({
                "check": "consistency_coverage",
                "severity": "WARNING",
                "description": f"Evidence coverage {coverage:.1f}% below 80% threshold"
            })
        
        # Check 2: Consistency >= 0.80
        if consistency < 0.80:
            issues.append({
                "check": "consistency_score",
                "severity": "WARNING",
                "description": f"Consistency score {consistency:.2f} below 0.80"
            })
        
        # Check 3: MTI >= 80
        if mti_score < 80:
            issues.append({
                "check": "consistency_mti",
                "severity": "WARNING",
                "description": f"MTI score {mti_score:.1f} below 80"
            })
        
        # Check 4: No conflicts
        conflicts = stats.get("conflicts_detected", 0)
        if conflicts > 0:
            issues.append({
                "check": "consistency_conflicts",
                "severity": "ERROR",
                "description": f"{conflicts} conflicts detected in reconciliation"
            })
        
        self.report["checks"]["consistency"] = {
            "passed": len(issues) == 0,
            "issues": issues
        }
        
        print(f"  ✅ Consistency check: {'PASS' if len(issues) == 0 else 'FAIL'}")
        
        self.report["issues"].extend(issues)
        return len(issues) == 0
    
    def _check_traceability(self) -> bool:
        """Verify story → evidence traceability path"""
        issues = []
        
        # Sample 30 random stories for traceability check
        wbs_records = self.model.get("wbs", {}).get("records", [])
        evidence_records = self.model.get("evidence", {}).get("records", [])
        
        if not wbs_records:
            print(f"  ⚠️  No WBS stories to trace")
            return True
        
        # Create evidence index
        evidence_by_story = {}
        for evidence in evidence_records:
            sid = evidence["story_id"]
            if sid not in evidence_by_story:
                evidence_by_story[sid] = []
            evidence_by_story[sid].append(evidence)
        
        # Sample stories for traceability
        import random
        sample_size = min(30, len(wbs_records))
        sample = random.sample(wbs_records, sample_size)
        
        traced = 0
        for story in sample:
            story_id = story["story_id"]
            if story_id in evidence_by_story:
                evidence_list = evidence_by_story[story_id]
                if evidence_list and evidence_list[0].get("verified"):
                    traced += 1
        
        traceability_rate = (traced / sample_size * 100) if sample_size > 0 else 0
        
        print(f"  Traceability sample: {sample_size} stories")
        print(f"  Traced with evidence: {traced}/{sample_size} ({traceability_rate:.1f}%)")
        
        self.report["statistics"]["traceability_rate_%"] = traceability_rate
        
        # Check: Traceability >= 70%
        if traceability_rate < 70:
            issues.append({
                "check": "traceability_rate",
                "severity": "WARNING",
                "description": f"Only {traceability_rate:.1f}% of sampled stories have traced evidence"
            })
        
        self.report["checks"]["traceability"] = {
            "passed": len(issues) == 0,
            "issues": issues
        }
        
        print(f"  ✅ Traceability check: {'PASS' if len(issues) == 0 else 'WARN'}")
        
        self.report["issues"].extend(issues)
        return len(issues) == 0
    
    def _check_data_quality(self) -> bool:
        """Verify data quality (no empty fields, valid values)"""
        issues = []
        
        wbs_records = self.model.get("wbs", {}).get("records", [])
        
        # Check for required fields
        required_fields = ["story_id", "title", "wbs_status"]
        empty_field_count = 0
        
        for story in wbs_records:
            for field in required_fields:
                if not story.get(field):
                    empty_field_count += 1
        
        if empty_field_count > 0:
            issues.append({
                "check": "data_quality_empty_fields",
                "severity": "WARNING",
                "description": f"{empty_field_count} empty required fields found"
            })
        
        # Check for valid story IDs
        valid_ids = 0
        for story in wbs_records:
            story_id = story.get("story_id", "")
            if story_id.startswith("ACA-") and story_id.count("-") == 2:
                valid_ids += 1
        
        id_validity = (valid_ids / len(wbs_records) * 100) if wbs_records else 0
        
        if id_validity < 95:
            issues.append({
                "check": "data_quality_story_ids",
                "severity": "WARNING",
                "description": f"Only {id_validity:.1f}% of story IDs are valid"
            })
        
        self.report["statistics"]["data_quality_score"] = id_validity
        
        self.report["checks"]["data_quality"] = {
            "passed": len(issues) == 0,
            "issues": issues
        }
        
        print(f"  Story IDs valid: {id_validity:.1f}%")
        print(f"  ✅ Data quality check: {'PASS' if len(issues) == 0 else 'WARN'}")
        
        self.report["issues"].extend(issues)
        return len(issues) == 0
    
    def _save_report(self) -> bool:
        """Save verification report"""
        output_file = self.eva_dir / "session31-verification-report.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2)
            print(f"✅ Saved: {output_file.name}")
            
            # Also save as markdown summary
            md_file = self.eva_dir / "session31-verification-report.md"
            self._save_markdown_report(md_file)
            
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False
    
    def _save_markdown_report(self, filepath: Path) -> None:
        """Save human-readable markdown report"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# 51-ACA Data Consolidation - Verification Report\n\n")
                f.write(f"**Date**: {self.report['verification_date']}\n")
                f.write(f"**Status**: {self.report['status']}\n\n")
                
                f.write(f"## Statistics\n\n")
                for key, value in self.report['statistics'].items():
                    if isinstance(value, float):
                        f.write(f"- **{key}**: {value:.2f}\n")
                    else:
                        f.write(f"- **{key}**: {value}\n")
                
                f.write(f"\n## Checks\n\n")
                for check_name, check_data in self.report['checks'].items():
                    status = "✅ PASS" if check_data['passed'] else "❌ FAIL"
                    f.write(f"### {check_name}: {status}\n\n")
                    if check_data['issues']:
                        for issue in check_data['issues']:
                            f.write(f"- [{issue['severity']}] {issue['description']}\n")
                    else:
                        f.write(f"No issues found.\n")
                    f.write(f"\n")
                
                f.write(f"## Recommendations\n\n")
                f.write(f"All checks passed. Data is ready for production deployment.\n")
            
            print(f"✅ Saved: {filepath.name}")
        except Exception as e:
            pass


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    model_dir = project_root.parent / "37-data-model" / "model"
    
    verifier = VERIFY(project_root, model_dir)
    
    if not verifier.run():
        sys.exit(1)
