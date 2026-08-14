# UNI2 cancellation and invincibility predicates

This note applies to the pinned `uni2.exe` SHA-256 in
`data/frame_semantics.json`. Addresses beginning with `0x4...`/`0x5...` are
preferred-image virtual addresses; `entity+...` values are runtime structure
offsets.

## Cancellation

Native battle code has the following conditional result bytes:

| Property | `BCMDTbl.CheckCancel` argument | Cached byte |
|---|---:|---:|
| freely actionable | internal `0x424B80` | `entity+0x798` |
| Normal | `_SkillType_Normal` (`1`) | `entity+0x799` |
| Special | `_SkillType_Special` (`2`) | `entity+0x79A` |
| EX | `_SkillType_Ex` (`4`) | `entity+0x79B` |
| Chain Shift | `_SkillType_ChainShift` (`8`) | `entity+0x79C` |
| EX or Special | `6` | `entity+0x79D` |

The battle update around `0x531EF4` refreshes these local query results every
logic frame. The overlay nevertheless does not consume them directly: a result
such as `0xFF` can describe generic actionability and is not final command
eligibility. It evaluates predicate `0x42B480` itself on every sample. That
predicate returns `0xFF` when native actionability
function `0x424B80` succeeds. During a locked action:

- Normal starts from descriptor byte `+0x0E`, optionally overridden by the low
  byte of `entity+0x460` while `+0x46C > 0`.
- Special starts from descriptor byte `+0x0F`, optionally overridden by the
  high byte of the same timed override.
- Normal/Special rule values are evaluated by `0x42B3D0`: `1` requires a
  hit/contact result, `2` is always, and `3` requires the damage-result bit.
  Current result flags come from `entity+0x1CC`.
- EX is descriptor `+0x18 & 0x01`, or timed
  `entity+0x48C > 0 && entity+0x480 & 0x01`.
- CS is descriptor `+0x18 & 0x08`, or timed
  `entity+0x48C > 0 && entity+0x480 & 0x02`.

The `0x42B3D0` helper first converts `entity+0x1CC` into a local result: zero
stays zero, a nonzero value becomes 2 when bit `0x02` is set and 1 otherwise.
`_CancelFlag_Hit` accepts either nonzero result, `_CancelFlag_Always` accepts
unconditionally, and `_CancelFlag_Damage` accepts only result 2. These backing
fields are persistent inputs; reading them does not depend on the game calling
`CheckCancel` during that frame.

The native actionability shortcut `0x424B80` is also reconstructed from
descriptor `+0x11`, entity `+0x440/+0x44C`, and the secondary timed pair
`+0x450/+0x45C`.

### Known limitation: Chain Shift

The reconstructed `CheckCancel(8)` source predicate is not the complete CS
command-eligibility result and is disabled by default. Live observation on
2026-08-15 established:

- EX moves satisfy only part of the expected window; some frames are marked
  even though CS cannot actually be performed.
- Normal moves and most special moves fail to produce their expected window.
- Some special cases do produce a window, including Kuon `j623B`.

The unpacked character scripts independently add and remove
`def_MC1_ChainShiftOK`, `def_MC1_GuardChainShiftOK`, and in one case
`def_MC5_ChainShiftOK_NoShield` through `Battle_Std.MoveCodeEx`. Therefore the
complete answer combines descriptor/timed `CheckCancel(8)` inputs with
MoveCodeEx flags, contact/guard state, and global CS prerequisites. Until that
native command path is reconstructed, the overlay must not label the partial
predicate as confirmed CS availability.

The complete evidence log, rejected shortcuts and exact resume point are in
`analysis/cs_cancel_investigation.md`. CS research is currently shelved and its
configuration entry is both incomplete and disabled.

`UNQ` is not registered as a `_SkillType` and has no cache byte. It is a wiki
classification for character-specific branches implemented in command/move
scripts. Each branch can depend on PP state, prior normals, held buttons,
objects, hit state or a named follow-up. A generic `UNQ` bit would therefore be
invented data. Supporting it requires a separate per-character rule catalog or
a native aggregate that this executable does not expose.

## Broad strike/throw invincibility

Native function `0x42DB70` evaluates strike invincibility from:

```text
descriptor+0x0D in {3, 5}
|| entity+0x204 > 0
|| entity+0x206 > 0
```

Native function `0x42DB30` evaluates throw invincibility from:

```text
descriptor+0x0D in {4, 5}
|| entity+0x205 > 0
|| entity+0x207 > 0
```

Thus descriptor values `3`, `4`, and `5` mean strike, throw, and both/full for
these predicates. The four bytes are the ordinary and extended strike/throw
timers written by `BMvEff.SetPlayerTimer`; the native getter returns the maximum
of each ordinary/extended pair.

## Attribute-specific invincibility

Native collision filter `0x557170` reads the defender mask at `entity+0x4A0`
only while `entity+0x4AC > 0`. The overlay uses the same lifetime gate:

| Display property | Defender filter bit |
|---|---:|
| Head | `0x001` |
| Body | `0x002` |
| Foot/Legs | `0x004` |
| Projectile/FireBall | `0x008` |
| Throw | `0x010` |
| Dive/AirDive | `0x040` |
| Light Foot | `0x100` |

The attacker-side category is the corresponding timed mask at `entity+0x4B0`
while `+0x4BC > 0`. Bit `0x40000000` reverses the match. The old overlay read
`+0x4A0` without checking `+0x4AC`; that could render expired residual values
and has been removed.

Full invincibility is reported for descriptor value `5` or when the effective
broad strike and throw predicates are both true. No move name, command input or
completed-action backfill is involved.
