# Native Chain Shift cancellation path

This note applies to the pinned `uni2.exe` SHA-256 recorded in
`data/frame_semantics.json`.

The VM registration table maps `BCMDTbl.CheckCancel` to wrapper `0x894F80`.
That wrapper obtains the current battle entity and calls native function
`0x42B480`. For `_SkillType_ChainShift` (`8`), the relevant native branch is:

```text
0x42B573  test dl, 8
0x42B578  cmp  dword ptr [esi+0x48C], 0
0x42B581  mov  eax, [esi+0x480]
0x42B58B  test al, 2
0x42B58D  jne  success
0x42B58F  test byte ptr [edi+0x18], 8
0x42B593  je   failure
```

Here `esi` is the entity and `edi` was loaded as:

```text
edi = [entity+0x648]
edi = [edi+0x10C]
```

Therefore the non-free result is the OR of:

1. `u32(entity+0x48C) > 0 && (u32(entity+0x480) & 2) != 0`
2. `u8([[entity+0x648]+0x10C]+0x18) & 8 != 0`

Before this branch, native function `0x42B480` calls `0x424B80`. If the entity
is already freely actionable, `CheckCancel` returns `0xFF`. This shortcut is
not rendered as a CS layer because free timeline cells are intentionally
black.

`BCMDTbl.CheckCancelFlag` is a different query (wrapper `0x895000`, native
`0x42B410`) and must not be substituted for the final skill-type check.

`MoveCodeEx` rules are correlated script inputs to a larger command-acceptance
path. They do not alter the local native function documented above, but they
cannot be discarded when asking whether the player's CS command is actually
legal. See `analysis/cs_cancel_investigation.md` for the identified bits,
capture evidence, failed approaches and current suspended status.
