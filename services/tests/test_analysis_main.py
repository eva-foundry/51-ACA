# EVA-STORY: ACA-03-021
import unittest
from unittest.mock import patch, MagicMock

from services.analysis.app.findings import FindingsAssembler
from services.analysis.app.main import get_cosmos_client

class TestFindingsAssembler(unittest.TestCase):
    @patch("services.analysis.app.cosmos.get_cosmos_client")
    def test_findings_assembler_construction(self, mock_get_cosmos_client):
        mock_cosmos_client = MagicMock()
        mock_get_cosmos_client.return_value = mock_cosmos_client

        scan_id = "test-scan-id"
        subscription_id = "test-sub-id"

        try:
            assembler = FindingsAssembler(scan_id=scan_id, subscription_id=subscription_id,
                                          cosmos_client=mock_cosmos_client)
            self.assertIsNotNone(assembler)
            self.assertEqual(assembler.scan_id, scan_id)
            self.assertEqual(assembler.subscription_id, subscription_id)
            self.assertEqual(assembler.cosmos, mock_cosmos_client)
            print("[PASS] FindingsAssembler instantiated successfully")
        except Exception as e:
            self.fail(f"FindingsAssembler instantiation failed: {e}")

if __name__ == "__main__":
    unittest.main()
