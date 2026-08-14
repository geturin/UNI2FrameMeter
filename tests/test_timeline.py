import json
import sys
from pathlib import Path
import struct
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frame_timeline import EMPTY_FRAME, FrameBands, FrameTimeline
from semantic_engine import SemanticEngine, is_actionable, is_hard_locked


class FrameTimelineTests(unittest.TestCase):
    @staticmethod
    def entity(*, movable: int = 0, action_type: int = 0, action_frame: int = 0) -> bytes:
        entity = bytearray(0xBA4)
        # +0x60 bit 8 set is the ordinary vulnerable state.
        struct.pack_into("<I", entity, 0x60, 0x100)
        struct.pack_into("<I", entity, 0x440, movable)
        struct.pack_into("<I", entity, 0x4B0, action_type)
        struct.pack_into("<I", entity, 0x674, action_frame)
        return bytes(entity)

    def test_confirmed_movability_gates_hard_lock(self) -> None:
        self.assertFalse(is_hard_locked(1))
        self.assertTrue(is_hard_locked(0))
        self.assertTrue(is_actionable(0, b"Mv_Modori_GuardS"))
        self.assertTrue(is_actionable(0, b"Mv_Modori_GuardC"))

    def test_actionable_cell_cannot_be_relevant(self) -> None:
        free_with_lingering_states = FrameBands(
            False,
            action="guard_return",
            state=99,
            codes=("locked", "some_state"),
            actionable=True,
        )
        self.assertFalse(free_with_lingering_states.relevant)
        self.assertTrue(free_with_lingering_states.actionable)

    def test_parse_ignores_every_lingering_state_when_440_is_free(self) -> None:
        entity = bytearray(0xBA4)
        for offset, value in (
            (0x24, 9),
            (0x440, 1),
            (0x4B0, 2),
            (0x644, 0x12345678),
            (0xB6C, 7),
        ):
            struct.pack_into("<I", entity, offset, value)
        frame = SemanticEngine(raw_states=True).classify(bytes(entity), 1).frame
        self.assertTrue(frame.actionable)
        self.assertFalse(frame.relevant)
        self.assertEqual(frame.codes, ())

    def test_guard_return_is_black_even_while_440_remains_zero(self) -> None:
        entity = bytearray(0xBA4)
        struct.pack_into("<I", entity, 0x24, 3)
        struct.pack_into("<I", entity, 0x440, 0)
        struct.pack_into("<I", entity, 0x644, 0x12345678)
        entity[0xACC : 0xACC + len(b"Mv_Modori_GuardS\0")] = b"Mv_Modori_GuardS\0"
        frame = SemanticEngine(raw_states=True).classify(bytes(entity), 1).frame
        self.assertTrue(frame.actionable)
        self.assertFalse(frame.relevant)
        self.assertEqual(frame.codes, ())

    def test_confirmed_mode_tracks_startup_active_and_recovery(self) -> None:
        engine = SemanticEngine(raw_states=False)
        startup = engine.classify(
            self.entity(action_type=2, action_frame=1), 0, attack_judgment=False
        )
        active = engine.classify(
            self.entity(action_type=2, action_frame=2), 0, attack_judgment=True
        )
        recovery = engine.classify(
            self.entity(action_type=2, action_frame=3), 0, attack_judgment=False
        )
        self.assertEqual(startup.frame.codes, ("startup",))
        self.assertEqual(active.frame.codes, ("active", "attack"))
        self.assertEqual(recovery.frame.codes, ("recovery",))

    def test_confirmed_mode_uses_hard_lock_for_non_action_state(self) -> None:
        frame = SemanticEngine().classify(self.entity(action_type=0), 1).frame
        self.assertEqual(frame.codes, ("hard_lock",))

    def test_head_invincibility_is_read_from_the_current_frame(self) -> None:
        engine = SemanticEngine()
        normal = engine.classify(self.entity(action_type=2, action_frame=1), 0).frame
        entity = bytearray(self.entity(action_type=2, action_frame=2))
        struct.pack_into("<I", entity, 0x4A0, 0x1)
        head_invincible = engine.classify(bytes(entity), 0).frame
        self.assertNotIn("head_invincible", normal.codes)
        self.assertIn("head_invincible", head_invincible.codes)

    def test_full_invincibility_is_read_from_the_current_frame(self) -> None:
        engine = SemanticEngine()
        entity = bytearray(self.entity(action_type=2, action_frame=1))
        struct.pack_into("<I", entity, 0x60, 0x0)
        frame = engine.classify(bytes(entity), 0).frame
        self.assertIn("full_invincible", frame.codes)

    def test_internal_air_dive_filter_is_not_displayed(self) -> None:
        engine = SemanticEngine()
        entity = bytearray(self.entity(action_type=2, action_frame=1))
        struct.pack_into("<I", entity, 0x4A0, 0x40)
        frame = engine.classify(bytes(entity), 0).frame
        self.assertFalse(any("dive" in str(token) for token in frame.codes))
        self.assertFalse(any("invincible" in str(token) for token in frame.codes))

    def test_air_dive_filter_can_be_enabled_in_config(self) -> None:
        profile = json.loads(
            (ROOT / "data" / "frame_semantics.json").read_text(encoding="utf-8")
        )
        dive = next(
            item
            for item in profile["runtime_attributes"]
            if item["token"] == "dive_invincible"
        )
        self.assertFalse(dive["display"])
        dive["display"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame_semantics.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            engine = SemanticEngine(profile=path)
            entity = bytearray(self.entity(action_type=2, action_frame=1))
            struct.pack_into("<I", entity, 0x4A0, 0x40)
            frame = engine.classify(bytes(entity), 0).frame
        self.assertIn("dive_invincible", frame.codes)

    def test_lingering_param1_bits_do_not_create_invincibility(self) -> None:
        engine = SemanticEngine()
        entity = bytearray(self.entity(action_type=2, action_frame=1))
        struct.pack_into("<I", entity, 0x6B8, 8 << 16)
        struct.pack_into("<I", entity, 0x6C8, 64 << 16)
        frame = engine.classify(bytes(entity), 0).frame
        self.assertFalse(any("invincible" in str(token) for token in frame.codes))

    def test_idle_does_not_start_display(self) -> None:
        timeline = FrameTimeline()
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(timeline.frames, [])

    def test_action_starts_and_idle_freezes_visible_history(self) -> None:
        timeline = FrameTimeline()
        active = FrameBands(True, action="startup")
        timeline.push(active, EMPTY_FRAME)
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(len(timeline.frames), 1)
        self.assertFalse(timeline.running)

    def test_short_idle_is_materialized_as_black_gap_on_next_action(self) -> None:
        timeline = FrameTimeline()
        first = FrameBands(True, action="first")
        second = FrameBands(True, action="second")
        timeline.push(first, EMPTY_FRAME)
        for _ in range(3):
            timeline.push(EMPTY_FRAME, EMPTY_FRAME)

        # Waiting alone does not scroll the result off screen.
        self.assertEqual(len(timeline.frames), 1)
        timeline.push(second, EMPTY_FRAME)

        self.assertEqual(len(timeline.frames), 5)
        self.assertEqual(timeline.frames[0][0].action, "first")
        self.assertTrue(
            all(
                p1 == EMPTY_FRAME and p2 == EMPTY_FRAME
                for p1, p2 in timeline.frames[1:4]
            )
        )
        self.assertEqual(timeline.frames[4][0].action, "second")

    def test_long_idle_remains_visible_until_next_action(self) -> None:
        timeline = FrameTimeline(idle_reset_frames=3)
        timeline.push(FrameBands(True, action="startup"), EMPTY_FRAME)
        for _ in range(3):
            timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(len(timeline.frames), 1)
        self.assertFalse(timeline.running)
        timeline.push(FrameBands(True, action="active"), EMPTY_FRAME)
        self.assertEqual(len(timeline.frames), 1)
        self.assertEqual(timeline.frames[0][0].action, "active")

    def test_only_last_sixty_frames_are_retained(self) -> None:
        timeline = FrameTimeline(capacity=60)
        for number in range(75):
            timeline.push(FrameBands(True, state=number), EMPTY_FRAME)
        self.assertEqual(len(timeline.frames), 60)
        self.assertEqual(timeline.frames[0][0].state, 15)

    def test_minus_seven_keeps_seven_p2_free_cells(self) -> None:
        timeline = FrameTimeline()
        locked = FrameBands(True, action="locked")
        # Recorded 236A block endpoints: P2 is free at 118, P1 at 125.
        for _tick in range(81, 118):
            timeline.push(locked, locked)
        for _tick in range(118, 125):
            timeline.push(locked, EMPTY_FRAME)
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)

        self.assertEqual(sum(not p2.relevant for _p1, p2 in timeline.frames[-7:]), 7)
        self.assertTrue(all(p1.relevant for p1, _p2 in timeline.frames[-7:]))
        frozen_length = len(timeline.frames)
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(len(timeline.frames), frozen_length)


if __name__ == "__main__":
    unittest.main()
