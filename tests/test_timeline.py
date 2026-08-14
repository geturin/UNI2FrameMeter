import json
import sys
from pathlib import Path
import struct
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frame_timeline import (
    EMPTY_FRAME,
    FrameBands,
    FrameTimeline,
    TimelineSettings,
    primary_band_runs,
)
from semantic_engine import (
    ATTACK_MOVE_CODE_MASK,
    SemanticEngine,
    is_actionable,
    is_control_locked,
)


class FrameTimelineTests(unittest.TestCase):
    @staticmethod
    def entity(
        *,
        movable: int = 0,
        move_code: int = 0,
        action_instance: int = 0,
        attack_filter: int = 0,
        chip_clear: int = 0,
        landing_lock: int = 0,
        control_state: int = 0,
        descriptor: int = 0,
        action_frame: int = 0,
    ) -> bytes:
        entity = bytearray(0xBA4)
        # Preserve the ordinary baseline value seen in captured entities. The
        # property reader deliberately does not use this field as an
        # invincibility predicate.
        struct.pack_into("<I", entity, 0x60, 0x100)
        struct.pack_into("<I", entity, 0x440, movable)
        struct.pack_into("<I", entity, 0x44C, landing_lock)
        struct.pack_into("<I", entity, 0x4B0, attack_filter)
        struct.pack_into("<I", entity, 0x57C, chip_clear)
        struct.pack_into("<I", entity, 0x644, descriptor)
        struct.pack_into("<I", entity, 0x674, action_frame)
        struct.pack_into("<I", entity, 0x680, action_instance)
        struct.pack_into("<I", entity, 0x6AC, move_code)
        struct.pack_into("<I", entity, 0xB6C, control_state)
        return bytes(entity)

    @staticmethod
    def engine_with_attribute_disabled(token: str) -> SemanticEngine:
        profile = json.loads(
            (ROOT / "frame_semantics.json").read_text(encoding="utf-8")
        )
        attribute = next(
            item
            for item in profile["external_attributes"]
            if item["token"] == token
        )
        attribute["display"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame_semantics.json"
            path.write_text(json.dumps(profile), encoding="utf-8")
            return SemanticEngine(profile=path)

    def test_confirmed_movability_gates_control_lock(self) -> None:
        self.assertFalse(is_control_locked(1))
        self.assertTrue(is_control_locked(0))
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

    def test_active_projectile_colors_and_advances_an_actionable_frame(self) -> None:
        engine = SemanticEngine()
        # Runtime checkboxes persist user preferences; make this test's
        # prerequisite explicit instead of depending on the user's config.
        engine.set_attribute_display("active_projectile", True)
        projectile = engine.classify(
            self.entity(movable=1),
            0,
            world_tokens=("active_projectile",),
        ).frame

        self.assertTrue(projectile.actionable)
        self.assertTrue(projectile.relevant)
        self.assertEqual(projectile.codes, ("active_projectile",))

        timeline = FrameTimeline()
        timeline.push(projectile, EMPTY_FRAME)
        timeline.push(projectile, EMPTY_FRAME)
        self.assertTrue(timeline.running)
        self.assertEqual(timeline.written_frames, 2)

        timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertFalse(timeline.running)
        self.assertEqual(timeline.written_frames, 2)

    def test_config_can_hide_active_projectile_world_frames(self) -> None:
        engine = self.engine_with_attribute_disabled("active_projectile")
        frame = engine.classify(
            self.entity(movable=1),
            0,
            world_tokens=("active_projectile",),
        ).frame
        self.assertTrue(frame.actionable)
        self.assertFalse(frame.relevant)
        self.assertEqual(frame.codes, ())

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
            self.entity(move_code=2, action_instance=10, action_frame=1),
            0,
            attack_judgment=False,
        )
        active = engine.classify(
            self.entity(move_code=2, action_instance=10, action_frame=2),
            0,
            attack_judgment=True,
        )
        recovery = engine.classify(
            self.entity(move_code=2, action_instance=10, action_frame=3),
            0,
            attack_judgment=False,
        )
        self.assertEqual(startup.frame.codes, ("startup",))
        self.assertEqual(active.frame.codes, ("attack",))
        self.assertEqual(recovery.frame.codes, ("recovery",))

    def test_confirmed_mode_uses_control_lock_for_non_action_state(self) -> None:
        frame = SemanticEngine().classify(self.entity(move_code=0), 1).frame
        self.assertEqual(frame.codes, ("control_lock",))

    def test_landing_countdown_is_forced_but_zero_is_guard_actionable(self) -> None:
        engine = SemanticEngine()
        forced = engine.classify(
            self.entity(control_state=2, landing_lock=4), 0
        ).frame
        cancelable = engine.classify(
            self.entity(control_state=2, landing_lock=0), 0
        ).frame
        self.assertEqual(forced.codes, ("control_lock",))
        self.assertFalse(forced.actionable)
        self.assertEqual(cancelable.codes, ())
        self.assertTrue(cancelable.actionable)

    def test_derived_attack_uses_move_code_when_hit_filter_is_zero(self) -> None:
        engine = SemanticEngine()
        startup = engine.classify(
            self.entity(move_code=0x2001, action_instance=20, action_frame=1),
            0,
        ).frame
        active = engine.classify(
            self.entity(move_code=0x2001, action_instance=20, action_frame=2),
            0,
            attack_judgment=True,
        ).frame
        recovery = engine.classify(
            self.entity(move_code=0x2001, action_instance=20, action_frame=3),
            0,
        ).frame
        self.assertEqual(startup.codes, ("startup",))
        self.assertEqual(active.codes, ("attack",))
        self.assertEqual(recovery.codes, ("recovery",))

    def test_action_instance_change_starts_a_new_derived_attack(self) -> None:
        engine = SemanticEngine()
        engine.classify(
            self.entity(
                move_code=1,
                action_instance=30,
                descriptor=0x1000,
                action_frame=10,
            ),
            0,
            attack_judgment=True,
        )
        derived = engine.classify(
            self.entity(
                move_code=1,
                action_instance=31,
                descriptor=0x2000,
                action_frame=1,
            ),
            0,
        ).frame
        self.assertEqual(derived.codes, ("startup",))

    def test_internal_descriptor_change_does_not_restart_attack_phase(self) -> None:
        engine = SemanticEngine()
        engine.classify(
            self.entity(
                move_code=2,
                action_instance=40,
                descriptor=0x1000,
                action_frame=10,
            ),
            0,
            attack_judgment=True,
        )
        recovery = engine.classify(
            self.entity(
                move_code=2,
                action_instance=40,
                descriptor=0x2000,
                action_frame=11,
            ),
            0,
        ).frame
        self.assertEqual(recovery.codes, ("recovery",))

    def test_izumi_5b_followups_each_get_full_phase_tracking(self) -> None:
        engine = SemanticEngine()
        for action_instance in (0x267E, 0x2680, 0x2690):
            startup = engine.classify(
                self.entity(
                    move_code=1,
                    action_instance=action_instance,
                    attack_filter=0,
                    chip_clear=0,
                    action_frame=1,
                ),
                0,
            ).frame
            active = engine.classify(
                self.entity(
                    move_code=0x2001,
                    action_instance=action_instance,
                    attack_filter=0,
                    chip_clear=0,
                    action_frame=8,
                ),
                0,
                attack_judgment=True,
            ).frame
            recovery = engine.classify(
                self.entity(
                    move_code=0x2001,
                    action_instance=action_instance,
                    attack_filter=0,
                    chip_clear=0,
                    action_frame=9,
                ),
                0,
            ).frame
            self.assertEqual(startup.codes, ("startup",))
            self.assertEqual(active.codes, ("attack",))
            self.assertEqual(recovery.codes, ("recovery",))

    def test_all_standard_move_code_categories_are_attack_actions(self) -> None:
        self.assertEqual(ATTACK_MOVE_CODE_MASK, 0x07)
        for move_code in (0x01, 0x02, 0x04, 0x2001, 0x10000002):
            frame = SemanticEngine().classify(
                self.entity(move_code=move_code, action_frame=1), 0
            ).frame
            self.assertEqual(frame.codes, ("startup",))

    def test_hit_filter_and_chip_clear_do_not_fake_an_attack_action(self) -> None:
        frame = SemanticEngine().classify(
            self.entity(attack_filter=2, chip_clear=1), 0
        ).frame
        self.assertEqual(frame.codes, ("control_lock",))

    def test_incomplete_cs_cancel_is_filtered_by_default(self) -> None:
        entity = self.entity(move_code=2, descriptor=0x3000, action_frame=8)
        absent = SemanticEngine().classify(entity, 0).frame
        present = SemanticEngine().classify(
            entity, 0, external_tokens=("cs_cancel",)
        ).frame
        self.assertNotIn("cs_cancel", absent.codes)
        self.assertNotIn("cs_cancel", present.codes)

    def test_cs_cancel_is_declared_incomplete_and_disabled(self) -> None:
        profile = json.loads(
            (ROOT / "frame_semantics.json").read_text(encoding="utf-8")
        )
        cs = next(
            item
            for item in profile["external_attributes"]
            if item["token"] == "cs_cancel"
        )
        self.assertFalse(cs["display"])
        self.assertEqual(cs["status"], "incomplete")

    def test_semantic_colors_keep_cs_and_invulnerability_visually_distinct(self) -> None:
        profile = json.loads(
            (ROOT / "frame_semantics.json").read_text(encoding="utf-8")
        )
        colors = {name: style["color"] for name, style in profile["tokens"].items()}
        self.assertEqual(colors["cs_cancel"], "#ffffff")
        self.assertNotEqual(colors["full_invincible"], colors["throw_invincible"])

    def test_disabled_head_invincibility_external_result_is_filtered(self) -> None:
        engine = self.engine_with_attribute_disabled("head_invincible")
        normal = engine.classify(self.entity(move_code=2, action_frame=1), 0).frame
        head_invincible = engine.classify(
            self.entity(move_code=2, action_frame=2),
            0,
            external_tokens=("head_invincible",),
        ).frame
        self.assertNotIn("head_invincible", normal.codes)
        self.assertNotIn("head_invincible", head_invincible.codes)

    def test_external_display_switch_updates_engine_without_reload(self) -> None:
        engine = SemanticEngine()
        entity = self.entity(move_code=2, action_frame=1)
        hidden = engine.classify(
            entity, 0, external_tokens=("head_invincible",)
        ).frame
        self.assertNotIn("head_invincible", hidden.codes)

        engine.set_attribute_display("head_invincible", True)
        visible = engine.classify(
            entity, 0, external_tokens=("head_invincible",)
        ).frame
        self.assertIn("head_invincible", visible.codes)

        engine.set_attribute_display("head_invincible", False)
        hidden_again = engine.classify(
            entity, 0, external_tokens=("head_invincible",)
        ).frame
        self.assertNotIn("head_invincible", hidden_again.codes)

    def test_incomplete_attribute_cannot_be_enabled_at_runtime(self) -> None:
        with self.assertRaises(ValueError):
            SemanticEngine().set_attribute_display("cs_cancel", True)

    def test_disabled_full_invincibility_external_result_is_filtered(self) -> None:
        engine = self.engine_with_attribute_disabled("full_invincible")
        entity = self.entity(move_code=2, action_frame=1)
        absent = engine.classify(entity, 0).frame
        present = engine.classify(
            entity, 0, external_tokens=("full_invincible",)
        ).frame
        self.assertNotIn("full_invincible", absent.codes)
        self.assertNotIn("full_invincible", present.codes)

    def test_internal_air_dive_filter_is_not_displayed(self) -> None:
        engine = SemanticEngine()
        entity = bytearray(self.entity(move_code=2, action_frame=1))
        struct.pack_into("<I", entity, 0x4A0, 0x40)
        frame = engine.classify(bytes(entity), 0).frame
        self.assertFalse(any("dive" in str(token) for token in frame.codes))
        self.assertFalse(any("invincible" in str(token) for token in frame.codes))

    def test_requested_properties_are_visible_external_attributes(self) -> None:
        profile = json.loads(
            (ROOT / "frame_semantics.json").read_text(encoding="utf-8")
        )
        attributes = {
            item["token"]: item for item in profile["external_attributes"]
        }
        requested = {
            "normal_cancel", "special_cancel", "ex_cancel", "cs_cancel",
            "strike_invincible", "body_invincible", "throw_invincible",
            "head_invincible", "foot_invincible", "light_foot_invincible",
            "dive_invincible", "projectile_invincible", "full_invincible",
            "active_projectile",
        }
        self.assertTrue(requested.issubset(attributes))
        self.assertFalse(attributes["cs_cancel"]["display"])

    def test_lingering_param1_bits_do_not_create_invincibility(self) -> None:
        engine = SemanticEngine()
        entity = bytearray(self.entity(move_code=2, action_frame=1))
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
        self.assertEqual(len(timeline.chronological_frames()), 1)
        self.assertFalse(timeline.running)

    def test_short_idle_is_materialized_as_black_gap_on_next_action(self) -> None:
        timeline = FrameTimeline()
        first = FrameBands(True, action="first")
        second = FrameBands(True, action="second")
        timeline.push(first, EMPTY_FRAME)
        for _ in range(3):
            timeline.push(EMPTY_FRAME, EMPTY_FRAME)

        # Waiting alone does not scroll the result off screen.
        self.assertEqual(len(timeline.chronological_frames()), 1)
        timeline.push(second, EMPTY_FRAME)

        recorded = timeline.chronological_frames()
        self.assertEqual(len(recorded), 5)
        self.assertEqual(recorded[0][0].action, "first")
        self.assertTrue(
            all(
                p1 == EMPTY_FRAME and p2 == EMPTY_FRAME
                for p1, p2 in recorded[1:4]
            )
        )
        self.assertEqual(recorded[4][0].action, "second")

    def test_long_idle_remains_visible_until_next_action(self) -> None:
        timeline = FrameTimeline(idle_reset_frames=3)
        timeline.push(FrameBands(True, action="startup"), EMPTY_FRAME)
        for _ in range(3):
            timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(len(timeline.chronological_frames()), 1)
        self.assertFalse(timeline.running)
        timeline.push(FrameBands(True, action="active"), EMPTY_FRAME)
        self.assertEqual(len(timeline.chronological_frames()), 1)
        self.assertEqual(timeline.frames[0][0].action, "active")

    def test_full_bar_wraps_with_five_black_cells_ahead(self) -> None:
        timeline = FrameTimeline(capacity=12, tail_gap=5)
        for number in range(12):
            timeline.push(FrameBands(True, state=number), EMPTY_FRAME)

        timeline.push(FrameBands(True, state=12), EMPTY_FRAME)

        self.assertEqual(timeline.frames[0][0].state, 12)
        self.assertEqual(timeline.write_index, 1)
        self.assertTrue(
            all(
                frame == (EMPTY_FRAME, EMPTY_FRAME)
                for frame in timeline.frames[1:6]
            )
        )
        self.assertEqual(timeline.frames[6][0].state, 6)

    def test_default_bar_holds_two_seconds_of_exact_frames(self) -> None:
        timeline = FrameTimeline()
        self.assertEqual(timeline.capacity, 120)
        for number in range(100):
            timeline.push(FrameBands(True, state=number), EMPTY_FRAME)
        recorded = timeline.chronological_frames()
        self.assertEqual(len(recorded), 100)
        self.assertEqual(recorded[-1][0].state, 99)

    def test_default_config_controls_timeline_layout(self) -> None:
        settings = TimelineSettings.load(ROOT / "frame_semantics.json")
        self.assertEqual(settings.length_frames, 120)
        self.assertEqual(settings.idle_reset_frames, 60)
        self.assertEqual(settings.wrap_gap_frames, 5)
        self.assertEqual(settings.current_frame_border_color, "#ffffff")
        self.assertTrue(settings.show_primary_run_counts)
        self.assertEqual(settings.primary_run_count_color, "#ffffff")
        self.assertEqual(settings.primary_run_count_font_size, 9)

    def test_primary_band_counts_split_only_when_first_color_changes(self) -> None:
        frames = [
            (FrameBands(True, codes=("startup",)), EMPTY_FRAME),
            (FrameBands(True, codes=("startup", "head_invincible")), EMPTY_FRAME),
            (FrameBands(True, codes=("attack",)), EMPTY_FRAME),
            (FrameBands(True, codes=("active_projectile",), actionable=True), EMPTY_FRAME),
            (EMPTY_FRAME, EMPTY_FRAME),
            (FrameBands(True, codes=("active_projectile",), actionable=True), EMPTY_FRAME),
        ]

        runs = primary_band_runs(frames, 0)

        self.assertEqual(
            [(run.token, run.first_column, run.last_column, run.frames) for run in runs],
            [
                ("startup", 0, 1, 2),
                ("attack", 2, 2, 1),
                ("active_projectile", 3, 3, 1),
                ("active_projectile", 5, 5, 1),
            ],
        )

    def test_primary_band_counts_are_independent_for_both_players(self) -> None:
        frames = [
            (
                FrameBands(True, codes=("startup",)),
                FrameBands(True, codes=("control_lock",)),
            ),
            (
                FrameBands(True, codes=("startup",)),
                FrameBands(True, codes=("control_lock", "full_invincible")),
            ),
        ]
        self.assertEqual(primary_band_runs(frames, 0)[0].frames, 2)
        self.assertEqual(primary_band_runs(frames, 1)[0].frames, 2)

    def test_current_frame_marker_follows_the_last_written_slot(self) -> None:
        timeline = FrameTimeline(capacity=12, tail_gap=5)
        timeline.push(FrameBands(True, state=0), EMPTY_FRAME)
        self.assertEqual(timeline.last_written_index, 0)
        for number in range(1, 12):
            timeline.push(FrameBands(True, state=number), EMPTY_FRAME)
        self.assertEqual(timeline.last_written_index, 11)
        timeline.push(FrameBands(True, state=12), EMPTY_FRAME)
        self.assertEqual(timeline.last_written_index, 0)

    def test_sixty_idle_frames_restart_next_action_at_left(self) -> None:
        timeline = FrameTimeline(capacity=60)
        timeline.push(FrameBands(True, action="old"), EMPTY_FRAME)
        for _ in range(60):
            timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        timeline.push(FrameBands(True, action="new"), EMPTY_FRAME)
        self.assertEqual(timeline.frames[0][0].action, "new")
        self.assertEqual(timeline.write_index, 1)

    def test_minus_seven_keeps_seven_p2_free_cells(self) -> None:
        timeline = FrameTimeline()
        locked = FrameBands(True, action="locked")
        # Recorded 236A block endpoints: P2 is free at 118, P1 at 125.
        for _tick in range(81, 118):
            timeline.push(locked, locked)
        for _tick in range(118, 125):
            timeline.push(locked, EMPTY_FRAME)
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)

        recorded = timeline.chronological_frames()
        self.assertEqual(sum(not p2.relevant for _p1, p2 in recorded[-7:]), 7)
        self.assertTrue(all(p1.relevant for p1, _p2 in recorded[-7:]))
        frozen_count = timeline.written_frames
        timeline.push(EMPTY_FRAME, EMPTY_FRAME)
        self.assertEqual(timeline.written_frames, frozen_count)


if __name__ == "__main__":
    unittest.main()
