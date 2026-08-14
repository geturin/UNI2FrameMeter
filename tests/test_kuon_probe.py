from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from build_kuon_probe import build, strip_comments  # noqa: E402


class KuonProbeTests(unittest.TestCase):
    def test_comment_stripper_preserves_comment_markers_inside_strings(self) -> None:
        source = 'local a="//keep"; // remove\r\nlocal b="/*keep*/";/*gone*/\r\n'
        self.assertEqual(
            strip_comments(source),
            'local a="//keep"; \r\nlocal b="/*keep*/";\r\n',
        )

    def test_real_probe_is_fixed_size_and_has_a_schedule(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "chr023_mv_0.txt"
            schedule = build(
                ROOT / "extracted" / "data" / "chr023" / "chr023_mv_0.txt",
                ROOT / "data" / "kuon_probe_states.json",
                output,
            )
            self.assertEqual(
                output.stat().st_size,
                (ROOT / "extracted" / "data" / "chr023" / "chr023_mv_0.txt").stat().st_size,
            )
            manifest = json.loads(
                (ROOT / "data" / "kuon_probe_states.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(schedule["schedule"]), len(manifest["states"]))
            self.assertIn(b"__probe_phase", output.read_bytes())


if __name__ == "__main__":
    unittest.main()
