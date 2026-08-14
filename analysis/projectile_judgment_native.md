# Projectile judgment investigation

Addresses below are for the pinned `uni2.exe` build. Preferred-image virtual
addresses use image base `0x400000`; runtime readers use module-relative
offsets.

## Native object collection

`BMvEff.CreateObject` (wrapper RVA `0x47E180`) calls internal `0x5B5E20`.
The created object is allocated by `0x4343A0`. Native object update and
collision code enumerate a separate pointer table rather than the fixed
character-entity capture region:

| Purpose | Preferred VA | Module-relative offset |
|---|---:|---:|
| current object count | `0x00C58BA0` | `0x858BA0` |
| object pointer table | `0x00C58BA4` | `0x858BA4` |

The loop at `0x5B60D0` reads `[*4 + 0xC58BA4]`. Its collision pass at
`0x5B6242` calls `0x556800` and `0x556070` for entries in the same table.

The earlier U2RG v1 recorder only saved the fixed region at module
`+0xC34E80`, so captures made before overlay build v23 do not contain these
created objects. The binary format remains unchanged; v23 adds selected
dynamic-object fields to the JSONL sidecar.

## Runtime fields

The source/native paths establish the following fields on created battle
objects:

| Field | Meaning |
|---:|---|
| `+0x04` | owner/player byte copied from the creating entity |
| `+0x0C` | object type; `_ObjType_FireBall == 2` |
| `+0x84` | Exist flags; `_Exist_NoAttackHantei == 0x400` |
| `+0x3F8` | parent/owner entity pointer |
| `+0x648` | current animation-frame pointer |
| `[+0x648]+0x110` | attack record consumed for the current frame |
| `+0x64C` | cache that remains zero on the validated standard fireballs |
| `+0x6AC` | MoveCode bank 0 |
| `+0x7BC` | active marker used by the runtime object structure |

The owner is `object+0x04`, not the `entity+0x438` player byte used by the
fixed character pool.

The proposed exact per-player predicate is:

```text
active_marker != 0
&& owner == player
&& object_type == _ObjType_FireBall
&& current_animation_frame->attack_record != 0
&& !(exist_flags & _Exist_NoAttackHantei)
```

Do not substitute `_HitCheckFlag_FireBall`: that value is an attack attribute,
not created-object identity.

## Kuon validation capture

`uni2_debug_20260815_012548_389357.bin` contains Kuon 214A whiff/hit and 236A
whiff/hit/follow-up. The fixed capture contains only the two primary entities;
slots 2-11 never become active. This is consistent with the scripts: Kuon's
214 and 236 families call `Battle_Std.CreateFireBall`, whose products reside in
the native dynamic object table above. A v23 JSONL capture is required to
validate the proposed predicate across creation, impact, follow-up and visual
remnant frames.

The v23 capture beginning `uni2_debug_20260815_013229_761465` disproved use of
the `+0x64C` cache: it was zero on all standard fireballs. The objects were
correctly marked `ObjType == 2`; dereferencing the recorded animation pointer
at `+0x110` produced the attack record exactly on active frames. In the first
five-object sequence, object lifetime/attack intervals were respectively
`56-65/58-65`, `91-105/93-96`, `118-133/121-132`, `160-192/172-191`, and
`332-341/334-341`. The second object therefore remained on screen for nine
frames after its attack record disappeared, confirming that object existence
alone would create a false positive.
