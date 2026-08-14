# UNI2 Frame Timeline Research

This workspace contains a read-only, external-process research probe for
`UNDER NIGHT IN-BIRTH II Sys:Celes`.

Safety boundary:

- no DLL injection;
- no process-memory writes;
- no remote threads or hooks;
- the game process is opened with `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ` only;
- the eventual UI will be a separate transparent overlay window.

## Current target

Installed executable:

```text
C:\Program Files (x86)\Steam\steamapps\common\UNDER NIGHT IN-BIRTH II Sys Celes\uni2.exe
SHA-256: 55615E8B2A91BE57EDD5EFF68EC0E283D8F0591F1977BB6F0B8A8DDB7AF2EC22
Architecture: PE32 / x86
Renderer: Direct3D 9
```

## Probe commands

Run from this directory:

```powershell
python .\src\uni2_probe.py status
python .\src\uni2_probe.py regions
python .\src\uni2_probe.py scan-counter --duration 5 --interval 0.25 --out .\captures\counter_candidates.json
python .\src\uni2_probe.py watch --candidates .\captures\counter_candidates.json
```

`scan-counter` looks for writable 32-bit values that progress at roughly the
game's simulation rate. It never modifies the target process. Run it while a
training match is actively simulating, not while a pause menu is open.

`watch` prints only candidate values and is intended for controlled experiments
such as pausing, resuming, resetting training, and entering/leaving a match.

## Confirmed research anchors (this executable hash)

- `uni2.exe+0x596B34`: battle logic tick. It advances by exactly one at about
  60 Hz, stops in the pause menu, and resets with Training reset.
- `uni2.exe+0x596B2C`: battle-state object base; the tick is field `+0x08`.
- `uni2.exe+0xC34E80`: 12-slot battle-entity pool.
- `0xBA4`: battle-entity stride. Slots 0 and 1 are active in the current
  two-character Training setup; unused slots remain unchanged.
- Entity `+0x438`: player/slot mapping byte observed as 0 and 1.
- Entity `+0x648`: rapidly changing pointer associated with the current
  animation/collision-frame record (classification still being verified).
- Entity `+0x64C`: runtime attack-data pointer candidate. In the confirmed
  Kuon 5A sample it becomes non-zero around the active interval, allowing the
  reader to infer phases from live state instead of a hand-authored roster.
- Entity `+0x4B0`: bounded action field used by the generic runtime tracker.
  Unlike `+0x1C`, it does not remain set merely because a player is crouching.
- Entity `+0x674`: action-local frame counter. It advances on normal action
  frames, holds during hitstop, survives internal descriptor changes, and
  resets for the next move.
- Entity `+0x1E4`: remaining hitstop countdown. The captured 5B block/hit
  sample counted from 10 to 1; the 5C sample counted from 11 to 1.
- Entity `+0x644`: current move-descriptor pointer. It changes for the complete
  move duration; the descriptor's first 16 bytes contain a CP932 move name.
  Kuon 5A was observed as `立ち弱攻撃` at descriptor `0x22F70080` in the
  current process instance (the absolute heap address is not persistent).
- Entity `+0xACC`: readable state/class label observed as `Mv_Neutral` and
  `Mv_Crouch_Wait`; it is not yet proven to be the current move name.

Frame-synchronized region recording is available with:

```powershell
python .\analysis\record_battle_region.py --delay 0 --duration 20 `
  --relative 0xC34E80 --size 0x8BB0 --out .\captures\entities.bin
```

The recorder polls only with `ReadProcessMemory` and takes one snapshot per
confirmed battle-logic tick.

The current live reader writes one JSON object per battle frame:

```powershell
python .\src\uni2_frame_reader.py --duration 10 `
  --out .\captures\live_frames.jsonl --print-changes
```

The initial external transparent overlay can be started with:

```powershell
python .\src\uni2_overlay.py
```

The default view is the conservative semantic view: hard lock, startup,
active, recovery, confirmed attack judgment, and validated invincibility.
Invulnerability is never inferred directly from the lingering values at
`+0x6B8/+0x6C8`; those values persist through recovery and appear in unrelated
air actions. Instead, every displayed cell is produced only from that frame's
live entity snapshot: `+0x4A0` bit 0 is the current head-invulnerability
filter, while a clear bit 8 at `+0x60` is the current full-invulnerability
state. The four controlled Kuon/Hyde recordings and published frame tables
were used only to validate those field meanings; no character id, move name,
input, or move-frame table participates at runtime. The confirmed `AirDive`
attack-category filter is available but disabled by default. Free/actionable
cells are always black. The former all-state diagnostic palette is retained
behind an explicit option:

```powershell
python .\src\uni2_overlay.py --raw-states
```

### Per-frame semantics architecture

The overlay has no move-recognition path and never rewrites old cells:

- `data/frame_semantics.json` declares token order, colors, visibility, and
  generic offset/mask/equality rules for confirmed live runtime attributes.
- `src/semantic_engine.py` converts the current entity snapshot directly into
  the current cell. Adding another bitmask-backed attribute is a data edit.
- `src/frame_timeline.py` only appends and freezes already-classified cells.
- `src/uni2_overlay.py` owns external reads, the transparent window, and
  drawing. It contains no character, move, input, or frame-table branches.

Every entry under `runtime_attributes` has a `display` switch. Head and full
invulnerability default to `true`; Dive invulnerability defaults to `false`.
To show Dive invulnerability in purple, change only this entry and restart the
overlay:

```json
{
  "token": "dive_invincible",
  "display": true
}
```

While the overlay is running, press `F8` once to begin a frame-synchronised
debug capture and press `F8` again to stop it. Files are written under
`./log`: `.bin` contains the complete 12-entity pool for every logic frame,
`.jsonl` contains readable decisions and key fields, and `.json` contains
capture metadata. The key can be changed, for example with
`--debug-hotkey F10`. Recording remains external and read-only.

It follows the UNI2 client window, is click-through, hides whenever UNI2 is not
the foreground application, and never injects or writes to game memory. Use
windowed or borderless display mode; exclusive fullscreen may appear above
ordinary desktop overlays. Only two unlabelled 60-column bars are drawn. In
`--raw-states` mode the confirmed raw channels are hard lock, hitstop
(`+0x1E4`), state code (`+0x24`), action type (`+0x4B0`), and control state
(`+0xB6C`). Concurrent colors are compacted but deterministically sorted; no
absolute empty lanes are reserved. `+0x440 == 1` marks ordinary control, but it
can remain zero during the cancelable `Mv_Modori_GuardS/C` presentation. Those
guard-return frames are free and must not be counted as blockstun. Two recorded
Kuon 236A block samples independently place P2 at the guard-return boundary
seven frames before P1 recovers, reproducing the game's `-7F`. The visible
timeline freezes as soon as both players are free, but it continues counting
the elapsed neutral logic frames. When activity resumes, those counted frames
are inserted as black cells before the new action, preserving the real temporal
gap. Merely waiting never erases the display. After at least 60F of free time,
the next action starts a fresh timeline at the left.

In a confirmed Kuon 5A sample, the entity fields held their action values from
battle tick `63434` through `63454` and returned to idle at `63455`: exactly 21
action frames. This agrees with the published 6 startup, 2 active, 14 recovery
(`6 + 2 + 14 - 1 = 21`) data. The raw phase-related fields are exposed by the
reader. The `+0x64C` interpretation still needs verification across varied
single-hit, multi-hit, projectile, whiff, hit, and block cases before its UI
labels are considered final.

## Tests

```powershell
python -m unittest discover -s tests -v
```
