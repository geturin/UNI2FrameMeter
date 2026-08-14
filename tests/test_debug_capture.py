import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from debug_capture import DebugCapture


class DebugCaptureTests(unittest.TestCase):
    def test_capture_writes_replayable_binary_events_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            recorder = DebugCapture(
                Path(directory),
                region_offset=0x1000,
                region_size=4,
                tick_offset=0x2000,
                image_sha256="abc",
                build_id="test",
                display_mode="confirmed",
            )
            binary_path = recorder.start()
            recorder.record(42, b"ABCD", {"display": [{"codes": ["startup"]}]})
            stopped_path = recorder.stop()

            self.assertEqual(stopped_path, binary_path)
            raw = binary_path.read_bytes()
            self.assertEqual(raw[:4], b"U2RG")
            self.assertEqual(struct.unpack_from("<IIII", raw, 4), (1, 0x1000, 4, 0x2000))
            self.assertEqual(struct.unpack_from("<I", raw, 20)[0], 42)
            self.assertEqual(raw[-4:], b"ABCD")

            event = json.loads(binary_path.with_suffix(".jsonl").read_text(encoding="utf-8"))
            self.assertEqual(event["tick"], 42)
            self.assertEqual(event["display"][0]["codes"], ["startup"])
            metadata = json.loads(binary_path.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["frames"], 1)
            self.assertEqual(metadata["first_tick"], 42)
            self.assertEqual(metadata["last_tick"], 42)


if __name__ == "__main__":
    unittest.main()
