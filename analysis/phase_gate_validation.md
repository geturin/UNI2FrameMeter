# Generic attack-phase gate validation

This note records the correction made for Kuon 6B follow-ups and Izumi
5B/5BB/5BBB. Runtime code remains character- and move-agnostic.

## Rejected fields

- `entity+0x4B0` is the value of timed `SetHitCheckFlag(type=1)`, not an
  action type. Izumi's derived attacks can leave it zero.
- `entity+0x57C` is the clear-condition member of `SetChipDamStatus`, not an
  attack-sequence flag.
- `entity+0x644` is not an action boundary. It changes inside some multi-part
  attacks without starting a new move.
- `entity+0x6E8` is the direct `GetMvAction/SetMvAction` value, but ordinary
  attacks and follow-ups commonly leave it zero.

## Replacement

An attack action is current when MoveCode bank 0 at `entity+0x6AC` contains:

```text
def_MC_Atk | def_MC_Skill | def_MC_Throw == 0x01 | 0x02 | 0x04
```

The game scripts themselves use this union when they need the generic concept
of an attack, skill or throw move. Phase tracking starts a new action when the
action-local frame at `+0x674` decreases or the opaque action-instance value at
`+0x680` changes. No absolute `+0x680` value is assigned to a move.

## Capture replay

All 11 debug binaries present on 2026-08-15 were replayed: 10,894 primary
player samples covering Kuon, Hyde, WAG and Izumi.

- The old `+0x4B0 || +0x57C` gate missed 133 frames whose MoveCode identified
  an attack.
- The corrected classifier produced zero frames where an Attack/Skill/Throw
  MoveCode was rendered as `control_lock`.
- Every observed chained-action instance change while MoveCode remained an
  attack coincided with a reset of `+0x674` and a new descriptor.
- Descriptor-only changes without an action-instance change occurred in
  existing captures, confirming that descriptor changes must not restart the
  phase tracker.

Exact replayed phase runs:

```text
Kuon 6B:  startup 193..202, active 203..205, recovery 206
Kuon 6BB: startup 207..218, active 219..232, recovery 233..255

Izumi 5B:   startup 398..404, active 405..415
Izumi 5BB:  startup 416..427, active 428..438
Izumi 5BBB: startup 439..453, active 454..468, recovery 469..491
```

The first two Izumi actions are cancelled during their active phase, so they
correctly have no recovery frames before the next action begins. The final
follow-up supplies the visible recovery segment.
