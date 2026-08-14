# Chain Shift cancel investigation (shelved)

This is the hand-off record for the incomplete CS-cancel channel. It applies
only to the pinned `uni2.exe` SHA-256 in `data/frame_semantics.json`.

## Current product decision

`cs_cancel` is **not a confirmed overlay property**. It remains declared with
`status: "incomplete"` and `display: false`. The semantic engine rejects an
attempt to enable an incomplete property, so the partial predicate cannot be
mistaken for a real CS window.

Normal, Special and EX cancellation are separate reconstructed properties.
Their results do not validate the CS implementation.

## What is confirmed

### Native local predicate

The VM wrapper for `BCMDTbl.CheckCancel` is at preferred VA `0x894F80` and
calls native `0x42B480`. The argument for Chain Shift is
`_SkillType_ChainShift == 8`.

For an entity which is not already freely actionable, `CheckCancel(8)` is:

```text
(i32(entity+0x48C) > 0 && (u32(entity+0x480) & 0x02) != 0)
|| (u8([[entity+0x648]+0x10C]+0x18) & 0x08) != 0
```

Before that branch, `0x42B480` calls actionability helper `0x424B80`. If that
helper succeeds, `CheckCancel` returns `0xFF`. This is a generic free/actionable
shortcut and is not proof that a locked attack can be cancelled into CS.

`BCMDTbl.CheckCancelFlag` (wrapper `0x895000`, native `0x42B410`) is a different
query and cannot replace the final CS eligibility check.

### Per-frame cache behavior

The battle update around preferred VA `0x531EF4` invokes the native queries
every logic frame and stores their local results at:

| Field | Local query |
|---|---|
| `entity+0x798` | actionability |
| `entity+0x799` | `CheckCancel(1)` / Normal |
| `entity+0x79A` | `CheckCancel(2)` / Special |
| `entity+0x79B` | `CheckCancel(4)` / EX |
| `entity+0x79C` | `CheckCancel(8)` / CS |
| `entity+0x79D` | `CheckCancel(6)` / EX-or-Special |

Therefore the earlier theory that these bytes change only after an attempted
cancel is rejected. They are per-frame values, but `+0x79C` is still only the
local `CheckCancel(8)` result. It is not the complete result of accepting the
player's Chain Shift command.

### MoveCodeEx storage and script flags

VM method `BMvTbl.GetMoveCodeEx(index)` (preferred VA `0x88B4F0`) reads:

```text
u32(entity + 0x6AC + index * 4)
```

Thus MoveCodeEx bank 1 is `entity+0x6B0`. Unpacked character scripts call:

```text
Battle_Std.MoveCodeEx.AddFlag(1, def_MC1_ChainShiftOK)
Battle_Std.MoveCodeEx.AddFlag(1, def_MC1_GuardChainShiftOK)
Battle_Std.MoveCodeEx.AddFlag(5, def_MC5_ChainShiftOK_NoShield)
```

Capture correlation identifies these two bank-1 bits with high confidence:

| Symbol | Observed bit | Evidence |
|---|---:|---|
| `def_MC1_ChainShiftOK` | `0x02000000` | Appears on contact for WAG 236A and 5B immediately before successful CS |
| `def_MC1_GuardChainShiftOK` | `0x04000000` | Appears during Kuon 3C and combines with guard contact |

The value of `def_MC5_ChainShiftOK_NoShield` and the consumer of that flag have
not been established.

The impact/result source used elsewhere by cancellation is `entity+0x1CC`.
Captured guard contact was `0x11011`; captured damaging contact was `0x11012`.
Bit `0x02` distinguishes the damaging case in native helper `0x42B3D0`.

## Controlled observations

### WAG capture

Source:
`log/uni2_debug_20260814_230937_858170.bin` and its JSONL sidecar.

The performed sequence was WAG 22A CS, 236A-on-contact CS, 236B whiff CS,
214A whiff CS, and 5B-on-contact CS.

- 236A and 5B acquire MoveCodeEx bank-1 bit `0x02000000` on contact before CS.
- 236B successfully CS-cancels without acquiring that bit.
- 214A successfully CS-cancels without acquiring that bit.
- Local cancel cache values can all be `0xFF` both where a whiff CS is legal
  and where it is not. Treating `0xFF` as CS permission creates false positives.

Representative MoveCodeEx banks:

```text
WAG 236A start: [0x2, 0x4000, 0, 0x20, 0x100, 0, 0x80, 0]
WAG 236A hit:   [0x1002, 0x02000000, 0x40000100, 0x80020,
                 0x100, 0, 0x80, 0]
WAG 5B hit:     [0x1, 0x02000000, 0x40040000, 0x80020,
                 0x100, 0, 0, 0]
```

### Kuon captures

Sources:

- `log/uni2_debug_20260814_211332_285025.bin`: two 3C blocks and two 28B
  blocks.
- `log/uni2_debug_20260814_212058_371082.bin`: two dash-C blocks.

Findings:

- Kuon 3C changes MoveCodeEx bank 1 from `0x4000` to `0x04000000`; with guard
  result `0x11011`, CS is legal. This supports the GuardChainShiftOK mapping.
- Kuon 28B did not provide a general CS rule: bank 1 was zero during the
  relevant action and its local predicate did not establish eligibility.
- Kuon dash C uses bank-1 values `0x124000` then `0x120000` and can CS on
  block. It demonstrates another permission route not covered by the two
  identified high bits.

### Live overlay observations

The partial descriptor/timer implementation produced all of these failures:

- Some EX moves showed a plausible subset of the CS window but also marked
  frames on which CS was not executable.
- Normal moves and most special moves omitted legal contact CS windows.
- Some specials, including Kuon j623B, happened to display a window.

This combination proves that `CheckCancel(8)` is a component of the command
path, not the full property the frame bar needs.

## Rejected implementations

Do not reintroduce any of these as a shortcut:

1. Rendering `entity+0x79C` directly.
2. Rendering `CheckCancel(8)` reconstructed from descriptor `StatusFlag1` and
   timed overrides alone.
3. Treating actionability/`0xFF` as locked-action CS permission.
4. Treating `0x02000000` as the only CS bit; it misses whiff-cancellable moves.
5. Backfilling earlier cells after a successful CS input.
6. Recognizing character names, move names, commands or move frame numbers.

The overlay must eventually compute the current frame from general live state,
without identifying the move and without rewriting history.

## Missing piece and resume point

The unresolved target is the complete Convert/Chain Shift command acceptance
predicate. It must combine at least:

- the local `CheckCancel(8)` result;
- MoveCodeEx flags, including contact-only, guard-only, direct/whiff and
  no-shield routes;
- current contact type;
- system-wide CS prerequisites and restrictions.

The best next step is to locate and unpack the common `Battle_Std` command
script (not another character script), identify the definition and consumer of
`def_CN_Convert`, then reproduce that predicate from its persistent inputs.
If the final consumer is native, disassemble its call path. Only after that
predicate passes the WAG and Kuon captures above should `cs_cancel` be promoted
to `confirmed` or enabled.
