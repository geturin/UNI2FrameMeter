# UNI2 battle-state semantic inventory

This is the authoritative work list for runtime frame-state decoding. A name
found in a script is not considered a decoded state until its native setter,
storage lifetime, descriptor fallback, and final consumer are identified.

## Completeness sources

- `vm_constants.json`: 622 unique VM constants, with values and registration
  evidence where decoded.
- `vm_apis.json`: 454 native methods in `BMvCore`, `BMvEff`, `BMvTbl`, and
  `BCMDTbl`, with wrapper RVAs.
- `battle_state_catalog.json`: the union inventory. It currently contains 404
  engine gameplay constants from 55 rule/data domains, 262 state-related VM
  APIs, 122 character PP slots referenced by scripts, 12 character PP flag
  symbols, 112 additional character state-like symbols, and all 16 bound-effect
  slots. Unknown items remain present rather than being silently filtered out.
- HA6 records: static attack/judgment fields and per-judgment-frame data.
- Character/common scripts: dynamic assignments, clear conditions, and actual
  use cases. Script usage is evidence of use, not the completeness boundary.
- System tables: `BattleInfo.txt` and `BoundEff.txt`. The latter reserves 16
  status-effect slots and explicitly defines normal, burn, freeze, electric,
  confusion, four character-specific abnormal-hit visuals, explosion and short
  freeze (slots 0-10; 11-15 are unassigned defaults in this build).

There is no single flat `Status` list. The executable registers independent
rule domains. The battle-relevant domains include at least:

| Domain | Entries | Role |
|---|---:|---|
| `GuardFlag` | 42 | Attack guardability, shield categories and guard-result removal |
| `HanteiFlag` | 34 | Judgment/hitbox categories, including 25 extension bits |
| `HitCheckFlag` | 32 | Defender filtering/invulnerability categories |
| `AtkFlag` | 25 | Attack outcome rules: armor break, ukemi, burst, counter, hitstop, etc. |
| `ObjFlags` | 19 | Object lifetime, parent propagation, time stop, ground/camera/render behavior |
| `CatchFlag` | 15 | Catch/throw target and guard/shield conditions |
| `InterruptType` | 10 | Interrupt/callback categories |
| `ImpactFlag` | 9 | Resolved hit outcome: guard, counter, bound, armor, capture, etc. |
| `SkillCount` | 9 | System action counters/limits |
| `HitType` | 8 | Resolved collision result kind |
| `AsFlag` | 7 | Timed action-system overrides |
| `Exist` | 7 | Which judgment components exist |
| `ThrowRelease` | 7 | Throw-release recovery/vector/burst rules |
| `ThrowType` | 7 | Throw state and recovery rules |
| `SkillType` | 6 | Normal/special/EX/CS and related cancel queries |
| `CancelFlag` | 5 | None/hit/always/damage/invalid cancel condition |
| `ClearFlag` | 5 | Timed-state lifetime boundaries |
| `PosState` | 5 | Position-state query categories |
| `StatusFlag1` | 5 | Descriptor EX/CS/jump/guard-disable/hit-erase rules |
| `FrameFlagEx` | 4 | Animation-frame transition behavior |
| `MvStFlag` | 4 | Counter/danger-HP attacker and defender state |
| `StatusFlag0` | 3 | Descriptor stand/crouch/air guard permissions |
| `Status` | 3 | Stand/crouch/air position state |
| `PartnerFlag` | 2 | Parent hit-status/hitstop propagation |
| `CaptureHitFlag` | 1 | Capture result propagation |
| `MoveCode0` | 1 | Basic-action suppression |

AI-only, rendering-only, sound, networking, and mathematical constant domains
remain in the complete generated catalog, even though they are not frame-bar
states.

## Character-owned state is a separate layer

There cannot be a complete engine-state list made only from `_Status*` enums.
Character scripts store persistent resources, modes, marks, temporary command
state and buffs in PP slots. Across the extracted scripts, 122 distinct PP slot
symbols are referenced; a further 12 PP bit-flag names and 112 state-like custom
symbols occur. The item-level list and source files are in
`battle_state_catalog.json`.

Native PP wrappers prove the storage model:

```text
pp_base = entity+0x650
PP[index] = i32([pp_base + 0x9C8 + index*4])
```

- `BMvTbl.GetPP` wrapper `0x48B050` reads that cell.
- `BMvTbl.SetPP` wrapper `0x48B000` replaces it.
- `BMvTbl.AddPP` wrapper `0x48AFB0` increments it.

The symbolic-to-numeric PP binding is character-specific and is not part of the
622 global VM constants registered by the executable. Therefore PP entries are
cataloged as first-class state, but their numeric indices and final gameplay
consumers must be resolved per character. This is why a single global enum would
necessarily miss states such as character ammunition, install modes and marks.

## Confirmed timed override layout

All rows below are direct writes observed in the registered native wrappers.

| Script API | Value | Clear condition | Timer | Setter wrapper |
|---|---:|---:|---:|---:|
| `SetMoveableFlag` | `entity+0x440` | `+0x448` | `+0x44C` | `0x488DF0` |
| `SetAsStatusFlag` | `+0x460` normal/special bytes | `+0x468` | `+0x46C` | `0x488C00` |
| `SetAsPosStatusFlag` | `+0x470` | `+0x478` | `+0x47C` | `0x488B50` |
| `SetAsFlag` | `+0x480` | `+0x488` | `+0x48C` | `0x488AA0` |
| `SetAtkGuardFlag` | `+0x490` | `+0x498` | `+0x49C` | `0x4889F0` |
| `SetHitCheckFlag(type=0)` | structure at `+0x4A0` | inside structure | inside structure | `0x4881C0` |
| `SetHitCheckFlag(type=1)` | structure at `+0x4B0` | inside structure | inside structure | `0x4881C0` |

Consequently, `entity+0x4B0` is not a generic `action_type`. It is the value
member of the second hit-check state structure. Any action-phase use of that
field must be removed after the real action predicate is decoded.

`BMvTbl.GetMvAction` and `SetMvAction` read/write `entity+0x6E8` directly
(wrappers `0x48B430/0x48B460`). This is a script-visible move-action override,
but controlled normal, derived and special attacks commonly leave it zero. It
is therefore not the generic frame-meter action gate.

The generic gate used by the scripts is MoveCode bank 0 at `entity+0x6AC`.
Character code explicitly tests the union
`def_MC_Atk | def_MC_Skill | def_MC_Throw`; live values establish those low
bits as `0x01 | 0x02 | 0x04`. This union remains set for derived attacks even
when the timed attacker HitCheck structure at `+0x4B0` is zero.

New chained actions reset the action-local counter at `entity+0x674`. Across
all controlled captures, the opaque value at `+0x680` also changes at each
such boundary and does not change during an action. Its absolute value is not
a stable move identifier and must never be mapped to a move name; only relative
change is used as a second action-instance boundary signal. The move descriptor
at `+0x644` can change within one action and must not reset phase tracking.

`BMvEff.SetPlayerTimer` writes four independent byte timers:

| Parameter | Field |
|---|---:|
| `muteki_dage` | `entity+0x204` |
| `muteki_nage` | `entity+0x205` |
| `muteki_dageX` | `entity+0x206` |
| `muteki_nageX` | `entity+0x207` |

The following setters share a generic 16-byte timed-state structure. Within
each structure, byte `+0` is the value, dword `+4` is reset by the setter,
byte `+8` is the clear-condition mask, and dword `+0x0C` is the timer. This
layout is implemented by native helper `0x887FC0`.

| Script API | Structure base | Current evidence |
|---|---:|---|
| `SetCaptureHitFlag` | `entity+0x4C0` | storage confirmed |
| `SetNoHoseiFlag` | `entity+0x4D0` | storage confirmed |
| `SetNoHoseiHitFlag` | `entity+0x4E0` | storage confirmed |
| `SetNoUkemiTimeLimitFlag` | `entity+0x4F0` | storage confirmed |
| `SetVirtualGuardFlag` | `entity+0x510` | storage confirmed |
| `SetCounterHitFlag` | `entity+0x530` | storage confirmed; also refreshes native counter state |
| `SetForceUkemiTimeLimitFlag` | `entity+0x550` | storage confirmed |
| `SetSuperArmorFlag` | `entity+0x564` | nonzero final composite confirmed; value variants pending |
| `SetInvAtkFlag` | `entity+0x5D8` | storage confirmed; precise `Inv` meaning pending |
| `SetInvDefFlag` | `entity+0x5E8` | storage confirmed; precise `Inv` meaning pending |

Other confirmed direct structures:

| Script API | Fields | Evidence state |
|---|---|---|
| `SetChipDamStatus` | value `+0x574`, clear `+0x57C`, timer `+0x580` | confirmed storage |
| `SetSousaiFlag` | value `+0x5F8`, clear `+0x600`, timer `+0x604` | confirmed storage |
| `SetAtkCatchFlag` | value `+0x608`, clear `+0x610`, timers/data `+0x614..+0x61C` | confirmed storage |
| `SetGuardPlusFlag` | byte `+0x63E` | confirmed final for bits `0x01` and `0x04` |

### Super armor composite

The direct getter returns `entity+0x564` only while timer `+0x570` is positive,
but hit resolution does not treat that byte alone as the final state. Native
helper `0x54C330` and inlined copies in the hit pipeline require:

```text
entity+0x08 == 0
&& entity+0x570 > 0
&& u8(entity+0x564) != 0
&& u8(character_data+0x8D4) == 0
```

`character_data` is `entity+0x650`, with the owner fallback through
`entity+0x3F8`. Collision resolution sets `character_data+0x8D4` after armor is
consumed. Therefore the timed flag is a capability request; the displayed
per-frame result must also account for the per-character consumed latch. This
composite is now `confirmed_final` for the nonzero armor form; meanings of
individual nonzero values remain unproven.

### Virtual guard is split into two mechanisms

`SetVirtualGuardFlag` stores a timed selector at `entity+0x510` (timer `+0x51C`).
Native collision/proximity function `0x536870` uses `value+8` to select an
additional rectangle from the current frame's judgment data. It is not itself
a boolean "currently guarding" state.

`BMvTbl.VGuard_CheckKeep` instead calls native `0x539110`, which computes whether
virtual guard may continue from current conditions. It checks player/object
status, a character-data mask, hit/capture state, current input/actionability,
guard permission, timed guard-disable (`AsFlag_GuardRev`), collision proximity
through `0x536870`, and direction through `0x536ED0`. This is a per-call computed
predicate, not a single stored flag.

### Forced/no ukemi limit

The timed values at `+0x4F0` and `+0x550` are numeric recovery-limit inputs, not
booleans. Hit resolution copies active `SetForceUkemiTimeLimitFlag` values into
the resolved hit record (for example native paths around `0x557600` and
`0x562D90`). Script uses pass frame counts such as 13, 15, 20, 31 and 45. The
final recovery decision consuming that resolved field is still pending.

## Confirmed descriptor/override composites

The current move descriptor is `[[entity+0x648]+0x10C]`.

### Skill cancellation

Native `BCMDTbl.CheckCancel` (`0x42B480`) combines descriptor defaults and
timed overrides. Chain Shift is:

```text
(entity+0x48C > 0 && (u32(entity+0x480) & 0x02))
|| (u8(current_descriptor+0x18) & 0x08)
```

Normal and special cancellation use descriptor bytes `+0x0E/+0x0F`, replaced
by the two bytes at `entity+0x460` while `+0x46C` is active. EX uses descriptor
`+0x18 & 0x01` or the timed action-system override.

### Guard permission and guard disable

Native function `0x537220` builds stand/crouch/air guard-permission bits from
descriptor `+0x14` (`StatusFlag0` bits `0x100/0x200/0x400`) and timed `AsFlag`
bits `0x10/0x20/0x40`.

Native function `0x5A2040` tests guard disable from descriptor
`+0x18 & 0x80000000` or timed `AsFlag_GuardRev` (`entity+0x480 & 0x04` while
its timer is active). Despite its name, extracted script comments explicitly
describe this flag as making an otherwise actionable character unable to
guard.

### Reverse-direction/two-way guard assistance

`BMvEff.SetGuardPlusFlag` is the script API used for the opponent-facing
guard-direction buff. Its wrapper `0x478C50` writes one byte directly to
`entity+0x63E`.

- bit `0x01`: comments state "can guard even in the reverse direction"
  (`逆方向でもガードができるようになる`).
- bit `0x04`: comments state that automatic guard-direction correction during
  facing changes is disabled.

Native guard-direction function `0x536ED0` consumes `entity+0x63E`; bit `0x01`
directly enables its reverse-direction path. This state is neither an HA6
guard mask nor `AsFlag_GuardRev`.

### Attack guardability

The current attack record is reached through `[entity+0x648]+0x110`.
Guard-resolution functions including `0x536AC0` OR its base `GuardFlag` word
with the timed `SetAtkGuardFlag` value at `entity+0x490` when `+0x49C` is
active. The resulting mask belongs to the `GuardFlag` domain (42 registered
names, including aliases). Its bits control stand/crouch/air/shield
guardability and several guard-result transformations.

### Hit-check attribute matching

Native function `0x557170` performs the final match between the attack-side
timed structure (`SetHitCheckFlag(type=1)`, value at `entity+0x4B0`) and the
defender-side timed structure (`type=0`, value at `entity+0x4A0`). Attack bit
`0x40000000` (`HitCheckFlag_Reverse`) changes the match to an inverted mask.

Its caller `0x5570D0` first checks another pair of masks:

- attack descriptor `+0x20`, overridden by timed `SetInvAtkFlag` at
  `entity+0x5D8`;
- defender descriptor `+0x24`, overridden by timed `SetInvDefFlag` at
  `entity+0x5E8`.

Only after those masks permit interaction does it run the type-1/type-0
attribute comparison. Thus head/body/leg/projectile/dive and extension-bit
immunity are a true attack-category versus defender-filter relation, not
independent booleans guessed from move names.

## Classification states

Each catalog item will receive one of these evidence states:

- `confirmed_final`: final native predicate/result path decoded.
- `confirmed_storage`: setter and lifetime decoded; final consumers pending.
- `descriptor_static`: static record field decoded; runtime override pending.
- `resolved_result`: produced after collision/hit resolution rather than a
  pre-existing per-frame capability.
- `unknown`: name/value only; no user-facing interpretation yet.

Only `confirmed_final` items are eligible for default overlay display.
