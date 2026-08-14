from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from display_config import DisplayConfig  # noqa: E402


class DisplayConfigTests(unittest.TestCase):
    def test_display_switch_persists_without_changing_other_settings(self) -> None:
        source = json.loads(
            (ROOT / "frame_semantics.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame_semantics.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            config = DisplayConfig.load(path)

            config.set_display("head_invincible", True)

            saved = json.loads(path.read_text(encoding="utf-8"))
            attribute = next(
                item
                for item in saved["external_attributes"]
                if item["token"] == "head_invincible"
            )
            self.assertTrue(attribute["display"])
            self.assertEqual(saved["timeline"], source["timeline"])
            self.assertEqual(saved["tokens"], source["tokens"])

    def test_incomplete_display_switch_cannot_be_enabled(self) -> None:
        config = DisplayConfig.load(ROOT / "frame_semantics.json")
        cs = next(item for item in config.items() if item.token == "cs_cancel")
        self.assertEqual(cs.status, "incomplete")
        with self.assertRaises(ValueError):
            config.set_display("cs_cancel", True)


if __name__ == "__main__":
    unittest.main()
