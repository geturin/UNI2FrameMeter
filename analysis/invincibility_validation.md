# UNI2 invincibility validation (2026-08-14)

This profile is pinned to `uni2.exe` SHA-256
`55615E8B2A91BE57EDD5EFF68EC0E283D8F0591F1977BB6F0B8A8DDB7AF2EC22`.

## Published frame windows

| Character | Move | Startup | Active | Recovery / total | Published invulnerability |
|---|---|---:|---:|---:|---|
| Kuon | `[2]8A` | 7 | 12 | 31 recovery | 1-10 Dive; 3-10 Head |
| Kuon | `[2]8B` | 12 | 12 | 46 recovery | 1-15 Full |
| Hyde | `623A` | 5 | 9 | total 51 | 1-11 Dive; 3-11 Head |
| Hyde | `623B` | 6 | 11 | 55 recovery | 1-13 Full |

Sources:

- https://mizuumi.wiki/w/Under_Night_In-Birth/UNI2/Kuon
- https://mizuumi.wiki/w/Under_Night_In-Birth/UNI2/Hyde

## Unpacked-data cross-check

- Kuon `chr023_mv_0.txt`: the charge-DP template calls
  `SetHitMuteki2_Param1({[8]=Head, [64]=AirDive})` every update.
- Hyde `chr000_mv_0.txt`: `Mv_Skill_623A` calls the same function; `623B`'s
  full invulnerability is supplied by its judgment data rather than that move
  script callback.
- Kuon HA6 records `41236A/B` contain the corresponding attack judgments.
- Hyde HA6 records `623A/B` contain the corresponding attack judgments.

## Runtime anchors

- Entity byte `+0x05`: character id (`0` Hyde, `23` Kuon). A character swap
  recording confirmed that P1 changed 23 -> 0 while the unchanged Kuon P2
  remained 23.
- Entity `+0x674`: action-local logic frame.
- Entity `+0x680` is **not** a stable move id: its absolute values change
  between sessions and must never be mapped to a move. Across the controlled
  captures, however, a relative value change together with the `+0x674` reset
  consistently marks a new action instance, including chained follow-ups.
- Entity `+0x4A0` bit 0 is the head-attribute rejection filter, but the mask is
  live only while its timed-state lifetime at `+0x4AC` is positive. It is set
  on action frames 3-10 in the Kuon A recording and 3-11 in the Hyde A
  recording. Gating the mask fixes expired values lingering after the window.
- The current action descriptor is reached through `[[entity+0x648]+0x10C]`.
  Its byte `+0x0D` is read by the native strike/throw predicates: values 3, 4,
  and 5 mean strike, throw, and both/full respectively.
- Entity bytes `+0x204..+0x207` are four independent system invulnerability
  countdowns: strike, throw, extended strike, and extended throw. Wake-up and
  VO-style invulnerability use these timers. Full is descriptor type 5 or the
  simultaneous effective native strike and throw results.

The Wiki/script information is validation data only. Runtime classification
does not identify a character or move and does not consult a move frame table.
Each cell reads these live fields from the snapshot captured for that logic
frame; no completed-action recognition or retroactive annotation remains.

`AirDive` is an internal attack category (aerial special attacks that move the
attacker). Its filter is visible at `+0x4A0` bit 6. It is registered as a
confirmed runtime attribute, while its config `display` switch retains the
requested default of false.

`+0x6B8/+0x6C8` must not be treated as a live invulnerability result. Their
Param1-like bits persist through recovery, and unrelated air actions can carry
the same bits. They remain in debug logs only as raw research channels.
