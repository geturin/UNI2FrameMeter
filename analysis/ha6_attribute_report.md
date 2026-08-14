# UNI2 move-attribute source report

## Confirmed file roles

- `chrNNN.ha6`: `Hantei6DataFile`; move judgment and attack-property records.
- `chrNNN.pat`: `PAniDataFile`; per-frame animation, sprite and collision data.
- `chrNNN_mv_0.txt`: move behavior and runtime property overrides.
- `chrNNN_cmd_0.txt`: command/input to move mapping.
- `BaseData.ha6`: shared judgment records inherited by characters.

The archive tool only exposes the package index and stored bytes. The HA6 and
PAT inner formats are separate game formats and need their own readers.

## Confirmed HA6 structure

- `PSTR` + `PTT2`: string-table/inherited record. Kuon's standard attacks use
  Japanese record names such as `立ち弱攻撃`, `立ち中攻撃`, and `立ち強攻撃`.
- `PTCN`: explicit character record name, for example `236A` and `FB_236A`.
- `PDS2`: 32-byte raw record descriptor containing eight signed integers.
- `FSTR` / `FEND`: one judgment-frame record.
- `ATST` / `ATED`: attack-property block start/end.
- `ATGD`, `ATHE`, `ATSP`, `ATHH`, `ATF1`, `ATAT`, `ATC0`: raw attack fields.
  Their exact semantics still require controlled comparisons; they are not yet
  assigned user-facing names.

## Kuon examples

| Record | HA6 frames | Frames containing `ATST` |
|---|---:|---|
| standing weak (5A) | 6 | 2 |
| standing medium (5B) | 8 | 2 |
| standing strong (5C) | 12 | 6, 7 |
| `236A` actor | 13 | none |
| `FB_236A` attack body | 7 | 1, 2 |

HA6 frame indices are judgment-record indices, not automatically logic-frame
counts. PAT durations and runtime frame counters must be used to expand them
onto the 60 Hz timeline.

## Script-level properties already confirmed

- `SetHitMuteki` / `SetHitMuteki2_Param1`: invulnerability windows.
- `SetHitCheckFlag`: attack/body attribute filtering such as head or legs.
- `MoveCode.AddFlag` / `MoveCodeEx.AddFlag`: cancel permissions and move flags.
- `SetAtkGuardFlag`: guard-direction/category overrides.
- `SetMoveableFlag`: early actionability inside a move.
- `SetNoHoseiFlag`: proration/correction overrides.
- hit, block, clash and finalize callbacks: conditional branches.

These dynamic script properties must be combined with the selected HA6 frame;
neither source alone describes every composite state shown by a frame meter.
