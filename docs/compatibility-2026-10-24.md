# October 24 EXE compatibility / 10 月 24 日 EXE 兼容性

Version 0.6.1 supports the supplied EXE with SHA-256
`0c3e86429ff1239f98eed1570fb90139a79bac3484de684e228927b30ce4d2ba`.
It is PE32 x86, 6,921,216 bytes, with `SizeOfImage=0x44e5000` and
`TimeDateStamp=0x6ad1f4af`. The date identifies the update reported by the
user; compatibility is bound to this exact hash.

0.6.0 checks for the earlier `4ebed985…` hash and `0x6abcb77f` timestamp,
so it refuses this EXE before installing a hook. Its 22-byte hook entry still
matches. Matching that common compiler prologue alone does not establish
compatibility: it occurs at hundreds of functions in this image.

The new image was checked against every location consumed by the collector:

| Dependency | Audited location |
| --- | --- |
| Battle update hook | RVA `0x126660` |
| Entity pool | RVA `0xc65280`, 12 entities, stride `0xbc0` |
| Completed elapsed tick | RVA `0x5a58c4` |
| Phase state / tick | RVAs `0x5a4b2c` / `0x5a4b34` |
| Slow skip / global stop | RVAs `0x657e78` / `0x657e80` |
| Scene | RVA `0x5a4a84` |
| Object count / pointer table | RVAs `0x87b4e0` / `0x87b4e4` |
| Object allocation bounds | 2000 objects, size `0x7dc` |
| Training mode / submode | RVAs `0x5a5948` / `0x5a594c` |
| Network-active byte | RVA `0x1d595ed` |

The entity iterator at VA `0x430d80` confirms the pool, count, stride and
active marker `+0x7d8`. The allocator near `0x434290` confirms object bounds.
The action-permission (`0x424a20`), posture (`0x4260b0`, `0x426130`), cancel
(`0x42b2a0`, `0x42b350`), invincibility (`0x42db10`, `0x42db50`), hit-filter
(`0x5587c0`) and bound-state (`0x89ab60`) paths consume the fields represented
in `src/runtime_layout.py`. Animation descriptor and attack pointers remain
at `animation+0x10c` and `animation+0x110`; descriptor properties remain at
`+0x0c..+0x1b`. The guard-direction consumer still reads the attacker's
`+0x64a` flags. The compatibility change therefore keeps the audited hook,
layout and collection behavior and updates the exact EXE identity.

REA 3.2.1 with Ghidra 12.1.4 analyzed the complete hook body at
`0x526660..0x5277e9` (4490 bytes), evidence ID
`ev_ee2b64d278ad2cf43c06d0d04a5e037f47cadd070a4909f8c53c26208878ea23`.
The assembly and decompilation corroborate the logic-byte gate and elapsed
counter increment at `0x9a58c4`: global stop suppresses `0x9a58c8`, while
`0x9a58c4` still advances on the admitted logic pass. The routine passes the
phase-state address `0x9a4b2c` to `0x643b80`, performs 12 entity iterations
at stride `0xbc0` using the `+0x7d8` active marker, and uses the same Training
Mode predicate, `(mode == 0 && submode == 1) || mode == 3`. These observations
support retaining the collector's capture after the original routine returns;
this function alone does not identify the writer of the separate phase-tick
field. REA's default, low-confidence calling-convention recovery was not used
as ABI evidence. This analysis was static and did not start the game.

The prior `4ebed985…` binary was unavailable for a direct byte comparison.
An older local `cf64ec26…` binary is a different build and was not treated
as that baseline. No claim is made that only the PE timestamp changed.

From a source checkout, run the offline check with Python 3:

```sh
python verify_game_profile.py /path/to/uni2.exe --json
```

It checks the EXE identity and hook entry, consistency of the native/Python
profiles, and 15 audited code-window fingerprints in
`compatibility/2026-10-24.json`. These windows are static observations, not
an automatic proof of game semantics. The script never starts or injects
the game and does not include game files. Other EXEs remain unsupported.

The preceding 0.6.0 release had user Training Mode testing. Static analysis
of this EXE and package checks do not substitute for a live game test of
0.6.1. Restart the game before replacing an already loaded collector DLL.

中文结论：本次 EXE 的指纹和 PE 时间戳已改变，0.6.0 会按设计拒绝。
重新检查新版的挂钩、全局地址、角色与物体布局及状态判定路径后，
0.6.1 更新身份检查，保留严格拒绝未知 EXE 的机制。以上是静态兼容性
证据，尚未证明新版实机运行；旧版本的实机验收不能替代此次更新的实测。
