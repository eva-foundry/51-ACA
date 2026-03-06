#!/usr/bin/env python3
"""
Phase 1: HARVEST - Extract data from all sources for 51-ACA data consolidation
    1. Top-down: PLAN.md → WBS (281 stories)
    2. Bottom-up: Git + tests + code → Evidence
    3. ADO: Work items → ADO mapping
    Outputs:
    - .eva/session31-harvest-wbs.json
    - .eva/session31-harvest-evidence.json
    - .eva/session31-harvest-ado.json
"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class HARVEST:
    """Phase 1: Extract and normalize data from all sources"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.plan_md = project_root / "PLAN.md"
        self.status_md = project_root / "STATUS.md"
        self.eva_dir = project_root / ".eva"
        self.evidence_dir = project_root / "evidence"
        self.scripts_dir = project_root / "scripts"
        
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Output structures
        self.wbs_harvest = {
            "harvest_date": self.timestamp,
            "source": "PLAN.md",
            "project_id": "51-ACA",
            "epics": [],
            "features": [],
            "stories": [],
            "statistics": {
                "total_epics": 0,
                "total_features": 0,
                "total_stories": 0,
                "story_status_counts": {}
            }
        }
        
        self.evidence_harvest = {
            "harvest_date": self.timestamp,
            "source": ["git", "tests", "receipts"],
            "project_id": "51-ACA",
            "evidence_records": [],
            "statistics": {
                "total_evidence": 0,
                "by_type": {},
                "by_epic": {}
            }
        }
        
        self.ado_harvest = {
            "harvest_date": self.timestamp,
            "source": "ado-id-map.json + local exports",
            "project_id": "51-ACA",
            "workitems": [],
            "statistics": {
                "total_workitems": 0,
                "by_type": {},
                "by_state": {}
            }
        }
    
    # =========================================================================
    # PHASE 1A: TOP-DOWN HARVEST (PLAN.md → WBS)
    # =========================================================================
    
    def harvest_top_down(self) -> bool:
        """Extract WBS from PLAN.md"""
        print("\n📋 HARVEST PHASE 1A: TOP-DOWN (PLAN.md)")
        print("=" * 70)
        
        try:
            content = self.plan_md.read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ PLAN.md not found at {self.plan_md}")
            return False
        
        # Extract structured elements using regex
        epics = self._parse_epics(content)
        features = self._parse_features(content)
        stories = self._parse_stories(content)
        
        self.wbs_harvest["epics"] = epics
        self.wbs_harvest["features"] = features
        self.wbs_harvest["stories"] = stories
        
        # Statistics
        self.wbs_harvest["statistics"]["total_epics"] = len(epics)
        self.wbs_harvest["statistics"]["total_features"] = len(features)
        self.wbs_harvest["statistics"]["total_stories"] = len(stories)
        
        # Count by status
        status_counts = {}
        for story in stories:
            status = story.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        self.wbs_harvest["statistics"]["story_status_counts"] = status_counts
        
        print(f"✅ Extracted {len(epics)} epics")
        print(f"✅ Extracted {len(features)} features")
        print(f"✅ Extracted {len(stories)} stories")
        print(f"   Status breakdown: {status_counts}")
        
        return True
    
    def _parse_epics(self, content: str) -> List[Dict[str, Any]]:
        """Parse epics from PLAN.md"""
        epics = []
        
        # Pattern: ^EPIC (\d+) -- TITLE \(MILESTONE\)
        epic_pattern = r'^=+\s*EPIC\s+(\d+)\s+--\s+(.+?)\s+\(([A-Z0-9.]+)\)$'
        
        for match in re.finditer(epic_pattern, content, re.MULTILINE):
            epic_num = int(match.group(1))
            title = match.group(2).strip()
            milestone = match.group(3)
            
            epics.append({
                "epic_id": f"ACA-{epic_num}",
                "epic_number": epic_num,
                "title": title,
                "milestone": milestone,
                "status": self._infer_epic_status(content, epic_num)
            })
        
        return epics
    
    def _parse_features(self, content: str) -> List[Dict[str, Any]]:
        """Parse features from PLAN.md"""
        features = []
        
        # Pattern: Feature N.M -- Title
        feature_pattern = r'^Feature\s+(\d+)\.(\d+)\s+--\s+(.+)$'
        
        for match in re.finditer(feature_pattern, content, re.MULTILINE):
            epic = int(match.group(1))
            num = int(match.group(2))
            title = match.group(3).strip()
            
            features.append({
                "feature_id": f"ACA-{epic}.{num}",
                "epic_id": f"ACA-{epic}",
                "feature_number": f"{epic}.{num}",
                "title": title
            })
        
        return features
    
    def _parse_stories(self, content: str) -> List[Dict[str, Any]]:
        """Parse stories from PLAN.md - improved to handle all formats"""
        stories = []
        
        # Use a more comprehensive regex pattern
        # Matches: "  Story N.M.O [ACA-NN-NNN]  As a ... " or multiple spaces
        story_pattern = r'\s+Story\s+[\d.]+\s+\[([A-Z0-9\-]+)\]\s+(.+?)(?:\s+Status:\s+([A-Z_]+\d*))?\s*$'
        
        for line in content.split('\n'):
            match = re.match(story_pattern, line)
            if not match:
                continue
            
            story_id = match.group(1)
            title = match.group(2).strip()
            status = match.group(3) if match.group(3) else "UNKNOWN"
            
            # Only accept valid ACA story IDs
            if not re.match(r'ACA-\d{2}-\d{3}', story_id):
                # If it looks like an old format (e.g., ACA-13-009a), still capture the core ID
                old_format_match = re.match(r'(ACA-\d{2}-\d{3})', story_id)
                if old_format_match:
                    story_id = old_format_match.group(1)
                else:
                    continue
            
            # Extract epic number from story_id
            parts = story_id.split('-')
            if len(parts) >= 2:
                try:
                    epic_num = int(parts[1])
                    feature_num = 1  # Default
                    
                    stories.append({
                        "story_id": story_id,
                        "epic_id": f"ACA-{epic_num:02d}",
                        "feature_id": f"ACA-{epic_num:02d}.{feature_num}",
                        "title": title,
                        "status": status,
                        "harvested_from": "PLAN.md"
                    })
                except (ValueError, IndexError):
                    continue
        
        return stories
    
    # (Removed - now integrated into _parse_stories)
    
    def _infer_epic_status(self, content: str, epic_num: int) -> str:
        """Infer epic status from WBS table"""
        status_pattern = rf'^(\w+)\s+{epic_num}\s+'
        match = re.search(status_pattern, content, re.MULTILINE)
        if match:
            return match.group(1)
        return "UNKNOWN"
    
    # =========================================================================
    # PHASE 1B: BOTTOM-UP HARVEST (Git + Tests → Evidence)
    # =========================================================================
    
    def harvest_bottom_up(self) -> bool:
        """Extract evidence from git, tests, receipts"""
        print("\n🔍 HARVEST PHASE 1B: BOTTOM-UP (Git + Tests + Receipts)")
        print("=" * 70)
        
        # Sub-phase 1: Git commits
        git_evidence = self._harvest_git_evidence()
        print(f"✅ Found {len(git_evidence)} evidence records from git")
        
        # Sub-phase 2: Test results
        test_evidence = self._harvest_test_evidence()
        print(f"✅ Found {len(test_evidence)} evidence records from tests")
        
        # Sub-phase 3: Receipt files
        receipt_evidence = self._harvest_receipt_evidence()
        print(f"✅ Found {len(receipt_evidence)} evidence records from receipts")
        
        # Merge all evidence
        all_evidence = git_evidence + test_evidence + receipt_evidence
        
        # Deduplicate by (story_id, evidence_type)
        deduplicated = {}
        for record in all_evidence:
            key = (record["story_id"], record["evidence_type"])
            if key not in deduplicated or record["timestamp"] > deduplicated[key]["timestamp"]:
                deduplicated[key] = record
        
        self.evidence_harvest["evidence_records"] = list(deduplicated.values())
        
        # Statistics
        self.evidence_harvest["statistics"]["total_evidence"] = len(deduplicated)
        
        by_type = {}
        by_epic = {}
        for record in deduplicated.values():
            etype = record["evidence_type"]
            by_type[etype] = by_type.get(etype, 0) + 1
            
            # Safely extract epic number from story_id
            story_id = record.get("story_id", "")
            if story_id.startswith("ACA-"):
                parts = story_id.split('-')
                if len(parts) >= 2:
                    try:
                        epic_num = int(parts[1])
                        epic_key = f"ACA-{epic_num:02d}"
                        by_epic[epic_key] = by_epic.get(epic_key, 0) + 1
                    except ValueError:
                        pass
        
        self.evidence_harvest["statistics"]["by_type"] = by_type
        self.evidence_harvest["statistics"]["by_epic"] = by_epic
        
        print(f"✅ Total deduplicated evidence: {len(deduplicated)}")
        print(f"   By type: {by_type}")
        
        return True
    
    def _harvest_git_evidence(self) -> List[Dict[str, Any]]:
        """Extract evidence from git commits"""
        records = []
        
        try:
            # Get last 100 commits with message
            result = subprocess.run(
                ["git", "log", "-100", "--format=%H|%s|%ai"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                print(f"⚠️  Git log failed: {result.stderr[:200]}")
                return records
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) < 3:
                    continue
                
                commit_hash = parts[0][:7]
                message = parts[1]
                timestamp = parts[2]
                
                # Extract story ID from commit message
                # Formats: feat(ACA-NN-NNN): ..., fix(ACA-NN-NNN): ...
                match = re.search(r'(feat|fix|docs|refactor|test|chore)\(([A-Z0-9\-]+)\)', message)
                if not match:
                    continue
                
                story_id = match.group(2)
                
                records.append({
                    "story_id": story_id,
                    "evidence_type": "code",
                    "source": "git",
                    "commit": commit_hash,
                    "message": message,
                    "timestamp": timestamp,
                    "proof": f"Commit {commit_hash}: {message}"
                })
        
        except Exception as e:
            print(f"⚠️  Error harvesting git: {e}")
        
        return records
    
    def _harvest_test_evidence(self) -> List[Dict[str, Any]]:
        """Extract evidence from test results"""
        records = []
        
        # Look for test result files
        test_files = [
            self.project_root / "pytest-gate-out.txt",
            self.project_root / "test-runner-output.txt",
            self.project_root / "lint-result.txt"
        ]
        
        for test_file in test_files:
            if not test_file.exists():
                continue
            
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                
                # Look for ACA story IDs in test output
                for match in re.finditer(r'([A-Z0-9\-]+)', content):
                    possible_id = match.group(1)
                    if re.match(r'ACA-\d{2}-\d{3}', possible_id):
                        records.append({
                            "story_id": possible_id,
                            "evidence_type": "test",
                            "source": test_file.name,
                            "timestamp": datetime.fromtimestamp(test_file.stat().st_mtime).isoformat(),
                            "proof": f"Found in {test_file.name}"
                        })
            
            except Exception as e:
                pass
        
        return records
    
    def _harvest_receipt_evidence(self) -> List[Dict[str, Any]]:
        """Extract evidence from receipt files in .eva/evidence/"""
        records = []
        
        if not self.evidence_dir.exists():
            return records
        
        try:
            # Look for receipt.py files: ACA-NN-NNN-receipt.py
            for receipt_file in self.evidence_dir.glob("ACA-*-receipt.py"):
                # Extract story ID: ACA-NN-NNN from filename
                match = re.match(r'(ACA-\d{2}-\d{3})', receipt_file.name)
                if not match:
                    continue
                
                story_id = match.group(1)
                
                records.append({
                    "story_id": story_id,
                    "evidence_type": "receipt",
                    "source": "evidence/" + receipt_file.name,
                    "timestamp": datetime.fromtimestamp(receipt_file.stat().st_mtime).isoformat(),
                    "proof": f"Receipt: {receipt_file.name}"
                })
        
        except Exception as e:
            pass
        
        return records
    
    # =========================================================================
    # PHASE 1C: ADO HARVEST (ADO mapping)
    # =========================================================================
    
    def harvest_ado(self) -> bool:
        """Extract ADO work items and mappings"""
        print("\n🔗 HARVEST PHASE 1C: ADO (Work Items)")
        print("=" * 70)
        
        # Load existing ado-id-map.json
        ado_map_file = self.eva_dir / "ado-id-map.json"
        if not ado_map_file.exists():
            print(f"⚠️  ado-id-map.json not found at {ado_map_file}")
            print("   Creating empty ADO harvest (will be populated from veritas-plan.json)")
            return True
        
        try:
            with open(ado_map_file, 'r', encoding='utf-8') as f:
                ado_map_data = json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading ado-id-map.json: {e}")
            return True
        
        # Convert to harvest format
        if isinstance(ado_map_data, list):
            # Assume format: [{"story_id": "ACA-NN-NNN", "ado_id": "NNNN", ...}, ...]
            for item in ado_map_data:
                self.ado_harvest["workitems"].append({
                    "story_id": item.get("story_id"),
                    "ado_id": item.get("ado_id"),
                    "ado_type": item.get("ado_type", "User Story"),
                    "state": item.get("state", "Unknown"),
                    "title": item.get("title", ""),
                    "parent_epic": item.get("parent_epic"),
                    "assigned_sprint": item.get("assigned_sprint")
                })
        
        self.ado_harvest["statistics"]["total_workitems"] = len(self.ado_harvest["workitems"])
        
        print(f"✅ Loaded {len(self.ado_harvest['workitems'])} ADO work items")
        
        return True
    
    # =========================================================================
    # SAVE HARVESTED DATA
    # =========================================================================
    
    def save_harvest(self) -> bool:
        """Save all harvest outputs to .eva/session31-harvest-*.json"""
        print("\n💾 SAVING HARVEST DATA")
        print("=" * 70)
        
        outputs = [
            (self.eva_dir / "session31-harvest-wbs.json", self.wbs_harvest),
            (self.eva_dir / "session31-harvest-evidence.json", self.evidence_harvest),
            (self.eva_dir / "session31-harvest-ado.json", self.ado_harvest)
        ]
        
        all_ok = True
        for filepath, data in outputs:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Saved: {filepath.name}")
            except Exception as e:
                print(f"❌ Error saving {filepath.name}: {e}")
                all_ok = False
        
        return all_ok
    
    # =========================================================================
    # ORCHESTRATION
    # =========================================================================
    
    def run(self) -> bool:
        """Execute full Phase 1 HARVEST"""
        print("\n" + "=" * 70)
        print("PHASE 1: HARVEST - Extract data from all sources")
        print("=" * 70)
        
        success = True
        success = self.harvest_top_down() and success
        success = self.harvest_bottom_up() and success
        success = self.harvest_ado() and success
        success = self.save_harvest() and success
        
        if success:
            print("\n" + "=" * 70)
            print("✅ HARVEST PHASE 1 COMPLETE")
            print("=" * 70)
            print(f"\nOutputs:")
            print(f"  WBS:      .eva/session31-harvest-wbs.json ({self.wbs_harvest['statistics']['total_stories']} stories)")
            print(f"  Evidence: .eva/session31-harvest-evidence.json ({self.evidence_harvest['statistics']['total_evidence']} records)")
            print(f"  ADO:      .eva/session31-harvest-ado.json ({self.ado_harvest['statistics']['total_workitems']} workitems)")
            print(f"\nNext: Run Phase 2 (NORMALIZE)")
            print("  python scripts/normalize-phase2.py")
        
        return success


if __name__ == "__main__":
    import sys
    
    project_root = Path(__file__).parent.parent
    harvest = HARVEST(project_root)
    
    if not harvest.run():
        sys.exit(1)
