"""
# EVA-STORY: ACA-03-001
Rule registry -- imports and exports all 12 analysis rules.
"""
from app.rules.rule_01_dev_box_autostop import rule_01_dev_box_autostop
from app.rules.rule_02_vm_right_sizing import rule_02_vm_right_sizing
from app.rules.rule_03_reserved_instances import rule_03_reserved_instances
from app.rules.rule_04_storage_tiering import rule_04_storage_tiering
from app.rules.rule_05_unattached_disks import rule_05_unattached_disks
from app.rules.rule_06_snapshot_cleanup import rule_06_snapshot_cleanup
from app.rules.rule_07_idle_app_services import rule_07_idle_app_services
from app.rules.rule_08_oversized_cosmos import rule_08_oversized_cosmos
from app.rules.rule_09_network_optimization import rule_09_network_optimization
from app.rules.rule_10_openai_throttling import rule_10_openai_throttling
from app.rules.rule_11_rbac_hygiene import rule_11_rbac_hygiene
from app.rules.rule_12_zombie_resources import rule_12_zombie_resources

ALL_RULES = [
    rule_01_dev_box_autostop,
    rule_02_vm_right_sizing,
    rule_03_reserved_instances,
    rule_04_storage_tiering,
    rule_05_unattached_disks,
    rule_06_snapshot_cleanup,
    rule_07_idle_app_services,
    rule_08_oversized_cosmos,
    rule_09_network_optimization,
    rule_10_openai_throttling,
    rule_11_rbac_hygiene,
    rule_12_zombie_resources,
]