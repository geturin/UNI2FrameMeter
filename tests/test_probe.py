from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "uni2_probe.py"


class ProbeSafetyTests(unittest.TestCase):
    def test_source_has_no_mutating_process_apis(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in (ROOT / "src").glob("*.py")
        )
        forbidden = (
            "WriteProcessMemory",
            "VirtualAllocEx",
            "CreateRemoteThread",
            "QueueUserAPC",
            "SetThreadContext",
        )
        for symbol in forbidden:
            self.assertNotIn(symbol, text)

    def test_open_process_rights_are_read_only(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertRegex(text, r"PROCESS_VM_READ\s*=\s*0x0010")
        self.assertRegex(text, r"PROCESS_QUERY_INFORMATION\s*=\s*0x0400")
        self.assertIn(
            "READ_ONLY_PROCESS_RIGHTS = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION",
            text,
        )
        self.assertNotRegex(text, r"PROCESS_VM_WRITE\s*=")
        self.assertNotRegex(text, r"PROCESS_VM_OPERATION\s*=")

    def test_expected_binary_hash_is_pinned(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        match = re.search(r'EXPECTED_SHA256 = "([A-F0-9]{64})"', text)
        self.assertIsNotNone(match)
        self.assertEqual(
            match.group(1),
            "55615E8B2A91BE57EDD5EFF68EC0E283D8F0591F1977BB6F0B8A8DDB7AF2EC22",
        )


if __name__ == "__main__":
    unittest.main()
