# Kuon block/hit capture report

Capture: `captures/kuon_block_hit_down.bin`

- 8,636 logic-frame snapshots over 150 seconds.
- Seven tick epochs were detected automatically from Training resets.
- Epoch 3 contains the requested blocking sequence.
- Epoch 5 contains the requested hit, down, and recovery sequence.

## Confirmed runtime fields

- Entity `+0x4B0` happened to be non-zero (`2`) for these attacks, but later
  native analysis identified it as the timed attacker HitCheck filter. It is
  not a generic action gate; use MoveCode bank 0 at `+0x6AC` instead.
- Entity `+0x674`: action-local frame counter. It advances normally, holds
  during hitstop, survives an internal descriptor change inside 5C, and resets
  to 1 for a new action.
- Entity `+0x1E4`: remaining hitstop counter.
- Entity `+0x644`: current descriptor pointer; its first bytes decode as a
  CP932 display/state name.
- Entity `+0x64C`: current attack-data pointer. It marks the attack-bearing
  record but can remain selected throughout hitstop, so non-zero alone must not
  be counted as ordinary active frames.

## Blocking path (epoch 3)

| Event | Tick | Action frame | Hitstop |
|---|---:|---:|---:|
| 5B begins (`立ち中攻撃`) | 39 | 1 | 0 |
| 5B attack data selected | 47 | 9 | 0 |
| 2P enters `★しゃがみガード` | 48 | 9 | 10 |
| 5C begins (`立ち強攻撃`) | 58 | 1 | 0 |
| 5C internal descriptor changes | 65 | 8 | 0 |
| 5C attack data selected | 69 | 12 | 0 |
| second block hitstop begins | 70 | 12 | 11 |
| following action begins | 81 | 1 | 0 |
| 2P enters actionable `Mv_Modori_GuardC` | 118 | — | 0 |
| 2P guard-return animation ends | 124 | — | 0 |
| P1 action permission (`+0x440`) becomes free | 125 | — | 0 |

The actionable endpoints are therefore tick 118 for P2 and tick 125 for P1.
P2 has seven free frames (118 through 124) before P1 recovers, reproducing the
game's `-7F` display. A second standalone 236A recording independently enters
`Mv_Modori_GuardS` at tick 614 while P1 recovers at tick 621. In that sample
`+0x440` remains zero until tick 620, proving it is not by itself an actionability
gate. The final neutral/control transition is only the end of the guard-return
presentation; using it as the blockstun endpoint produces the incorrect `-1F`.

## Hit/down path (epoch 5)

| Event | Tick | Action frame | Hitstop |
|---|---:|---:|---:|
| 5B begins (`立ち中攻撃`) | 51 | 1 | 0 |
| 5B attack data selected | 59 | 9 | 0 |
| 2P enters medium crouching hit reaction | 60 | 9 | 10 |
| 5C begins (`立ち強攻撃`) | 70 | 1 | 0 |
| 5C internal descriptor changes | 77 | 8 | 0 |
| 5C attack data selected | 81 | 12 | 0 |
| 2P enters strong crouching hit reaction | 82 | 12 | 11 |
| following action begins | 93 | 1 | 0 |
| follow-up descriptor/down transition | 105 | 1 | 0 |
| 2P enters `★追撃ダウン` | 105 | — | 0 |
| 2P enters `★垂直吹き飛び` | 120 | — | 0 |
| P1 returns neutral | 157 | — | 0 |
| 2P lies face down | 157 | — | 0 |
| 2P ground recovery begins | 175 | — | 0 |
| landing portion | 200 | — | 0 |
| return/crouch transition | 210 | — | 0 |
| 2P returns to crouch wait | 222 | — | 0 |

## Remaining interpretation work

The third action uses descriptors that do not expose a player attack-data
pointer at `+0x64C`. Its attack event may be represented by another field or a
scripted sub-action. PAT/script correlation and a short whiff sample will be
used to distinguish ordinary active duration from collision-triggered hitstop
without maintaining a manual move list.
