# UNI2 AirDive attack-attribute inventory

`Def_HitCheckFlag_AirDive` is an attack-side category. A move that calls
`BMvTbl.SetHitCheckFlag(...Def_HitCheckFlag_AirDive...)` will whiff against a
defender whose AirDive immunity filter is enabled. It does **not** mean the
attacking move itself is invincible.

This inventory was produced by scanning all 27 installed
`chr000`-`chr026` move scripts and then checking the corresponding command
tables. `EX` internal move names are written as the player-facing `C` input.

| ID | Character | Script-confirmed AirDive attacks |
|---:|---|---|
| 001 | Linne | `j.63214A/B/C` |
| 005 | Gordeau | `j.214A/B/C` |
| 007 | Vatista | `j.623A/B` (the C-version assignment is commented out) |
| 008 | Seth | `j.623A/B/C`; `j.214A/B` (the C-version assignment is commented out) |
| 009 | Yuzuriha | `j.214A/B` |
| 011 | Eltnum | `j.214A/B/C` |
| 012 | Nanase | `j.214A/B/C`; the airborne `A/B/C` follow-ups from grounded `214A/B` |
| 013 | Byakuya | the airborne web-jump/spin `A/B/C` follow-ups, including the immediate/timed `A/B` variants; the base `214/j.214` placements are not marked AirDive |
| 016 | Wagner | `j.236A/B/C` |
| 017 | Enkidu | `j.236A/B/C` |
| 020 | Uzuki | `236B` from its script update ID 200 onward; `j.214A/B/C` |
| 021 | Mika | `j.623A/B/C`; `j.236A/B/C`; all normal/EX directional follow-ups (`1/2/3/4/6/7/8/9`) |
| 026 | Izumi | `j.236A/B/C` |

Primary script locations:

- Linne: `chr001_mv_0.txt:1941-1985`
- Gordeau: `chr005_mv_0.txt:1246-1303`
- Vatista: `chr007_mv_0.txt:2287-2360`
- Seth: `chr008_mv_0.txt:1450-1721`, `2673-2760`
- Yuzuriha: `chr009_mv_0.txt:3586-3620`
- Eltnum: `chr011_mv_0.txt:2948-3080`
- Nanase: `chr012_mv_0.txt:1256-1396`
- Byakuya: `chr013_mv_0.txt:1547-1918`, `2128-2186`
- Wagner: `chr016_mv_0.txt:1467-1651`
- Enkidu: `chr017_mv_0.txt:2055-2122`
- Uzuki: `chr020_mv_0.txt:1185-1357`, `3013-3133`
- Mika: `chr021_mv_0.txt:1246-1354`, `1850-2214`
- Izumi: `chr026_mv_0.txt:1922-2007`

No active `SetHitCheckFlag` assignment containing `AirDive` was found in the
other 14 installed character move scripts. Calls to
`SetHitMuteki2_Param1(...AirDive...)` were excluded: those grant defense
against this category and do not assign the category to an attack.
