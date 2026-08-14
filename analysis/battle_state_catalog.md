# UNI2 exhaustive battle-state catalog

This is an engine-derived union catalog, not the overlay display list. Unknown
items remain listed until their final native predicate has been decoded.

## Coverage

- `vm_constants_total`: 622
- `vm_apis_total`: 454
- `battle_constants`: 404
- `other_or_unclassified_constants`: 218
- `state_related_apis`: 262
- `other_or_unclassified_apis`: 192
- `character_pp_slots_referenced`: 122
- `character_pp_flag_symbols`: 12
- `character_state_like_symbols`: 112
- `bound_effect_slots`: 16

## Engine rule domains

| Domain | Members |
|---|---:|
| `Angle` | 2 |
| `AsFlag` | 7 |
| `AtkFlag` | 25 |
| `CancelFlag` | 5 |
| `CaptureHitFlag` | 1 |
| `CatchFlag` | 15 |
| `CatchSuccess` | 5 |
| `CharaMoveMode` | 3 |
| `CharaPrio` | 29 |
| `ClearFlag` | 5 |
| `Direction` | 4 |
| `Exist` | 7 |
| `ExistMode` | 4 |
| `FrameFlagEx` | 4 |
| `GetPos` | 8 |
| `GuardFlag` | 42 |
| `HC` | 5 |
| `Han6Hantei` | 4 |
| `Hantei` | 5 |
| `HanteiFlag` | 34 |
| `HitCheckFlag` | 32 |
| `HitType` | 8 |
| `ImpactFlag` | 9 |
| `InterruptType` | 10 |
| `KOMode` | 2 |
| `LiberateType` | 3 |
| `MODE` | 5 |
| `MoveCode0` | 1 |
| `MvStFlag` | 4 |
| `ObjFlags` | 19 |
| `ObjProcFlag` | 2 |
| `ObjProcFlags` | 2 |
| `ObjType` | 2 |
| `PAniFlag` | 3 |
| `PAniFrame` | 8 |
| `PCGaugeType` | 1 |
| `PartnerFlag` | 2 |
| `PosState` | 5 |
| `Position` | 6 |
| `PrioType` | 1 |
| `SkillCount` | 9 |
| `SkillType` | 6 |
| `SpCommandFlag` | 2 |
| `SpGauge` | 2 |
| `SpGaugeMode` | 3 |
| `State` | 2 |
| `Status` | 3 |
| `StatusFlag0` | 3 |
| `StatusFlag1` | 5 |
| `ThrowRelease` | 7 |
| `ThrowType` | 7 |
| `VecFlag` | 2 |
| `Vector` | 5 |
| `defBtlFinish` | 4 |
| `eWinType` | 5 |

## Engine gameplay constants (all items)

| Domain | Constant | Registered value(s) | Script uses |
|---|---|---|---:|
| `Angle` | `_Angle_AngleAdd` | `0x1` | 1 |
| `Angle` | `_Angle_PositionAdd` | `0x2` | 0 |
| `AsFlag` | `_AsFlag_ChainShift` | `0x2` | 3 |
| `AsFlag` | `_AsFlag_DamageEx` | `0x100` | 1 |
| `AsFlag` | `_AsFlag_ExCancel` | `0x1` | 7 |
| `AsFlag` | `_AsFlag_GuardRev` | `0x4` | 4 |
| `AsFlag` | `_AsFlag_Guard_Air` | `0x20` | 0 |
| `AsFlag` | `_AsFlag_Guard_Crouch` | `0x40` | 0 |
| `AsFlag` | `_AsFlag_Guard_Stand` | `0x10` | 0 |
| `AtkFlag` | `_AtkFlag_ArmorBreak` | `0x8000` | 0 |
| `AtkFlag` | `_AtkFlag_AttackStop` | `0x2000000` | 0 |
| `AtkFlag` | `_AtkFlag_ChgCounterVec` | `0x10` | 0 |
| `AtkFlag` | `_AtkFlag_ChgHitFlagVec` | `0x4000000` | 0 |
| `AtkFlag` | `_AtkFlag_ChgReflexHitVec` | `0x4000` | 0 |
| `AtkFlag` | `_AtkFlag_ComboEnd` | `0x4` | 0 |
| `AtkFlag` | `_AtkFlag_GuardStop` | `0x10000` | 0 |
| `AtkFlag` | `_AtkFlag_HitYure` | `0x40` | 0 |
| `AtkFlag` | `_AtkFlag_HpCut` | `0x1` | 0 |
| `AtkFlag` | `_AtkFlag_NoAirUkemi` | `0x80` | 0 |
| `AtkFlag` | `_AtkFlag_NoBoundCorrect` | `0x20000` | 0 |
| `AtkFlag` | `_AtkFlag_NoBoundCorrectPlus` | `0x100000` | 0 |
| `AtkFlag` | `_AtkFlag_NoBurst` | `0x20000000` | 0 |
| `AtkFlag` | `_AtkFlag_NoCounter` | `0x40000` | 0 |
| `AtkFlag` | `_AtkFlag_NoFirstAttack` | `0x1000` | 0 |
| `AtkFlag` | `_AtkFlag_NoGroundUkemi` | `0x100` | 0 |
| `AtkFlag` | `_AtkFlag_NoHitPlus` | `0x20` | 0 |
| `AtkFlag` | `_AtkFlag_NoHitStop` | `0x400` | 0 |
| `AtkFlag` | `_AtkFlag_NoKo` | `0x2` | 0 |
| `AtkFlag` | `_AtkFlag_NoPrio` | `0x200000` | 0 |
| `AtkFlag` | `_AtkFlag_NoWallUkemi` | `0x800000` | 0 |
| `AtkFlag` | `_AtkFlag_SwingPlus` | `0x1000000` | 0 |
| `AtkFlag` | `_AtkFlag_TeamHit` | `0x200` | 0 |
| `AtkFlag` | `_AtkFlag_TimeCorrect` | `0x8000000` | 0 |
| `AtkFlag` | `_AtkFlag_VectorSp` | `0x80000` | 0 |
| `CancelFlag` | `_CancelFlag_Always` | `0x2` | 31 |
| `CancelFlag` | `_CancelFlag_Damage` | `0x3` | 3 |
| `CancelFlag` | `_CancelFlag_Hit` | `0x1` | 9 |
| `CancelFlag` | `_CancelFlag_Invalid` | `0xFF` | 1 |
| `CancelFlag` | `_CancelFlag_None` | `0x0` | 30 |
| `CaptureHitFlag` | `_CaptureHitFlag_Parent` | `0x1` | 0 |
| `CatchFlag` | `_CatchFlag_AtkAirGuard` | `0x2` | 1 |
| `CatchFlag` | `_CatchFlag_AtkAirShield` | `0x200` | 1 |
| `CatchFlag` | `_CatchFlag_AtkAllGuard` | `0x7` | 7 |
| `CatchFlag` | `_CatchFlag_AtkCrouchGuard` | `0x4` | 2 |
| `CatchFlag` | `_CatchFlag_AtkCrouchShield` | `0x400` | 2 |
| `CatchFlag` | `_CatchFlag_AtkGroundGuard` | `0x5` | 0 |
| `CatchFlag` | `_CatchFlag_AtkGroundShield` | `0x500` | 0 |
| `CatchFlag` | `_CatchFlag_AtkNoGuard` | `0x8` | 0 |
| `CatchFlag` | `_CatchFlag_AtkNoGuardThrow` | `0x10` | 0 |
| `CatchFlag` | `_CatchFlag_AtkStandGuard` | `0x1` | 6 |
| `CatchFlag` | `_CatchFlag_AtkStandShield` | `0x100` | 5 |
| `CatchFlag` | `_CatchFlag_Invalid_Through_ExceptBound` | `0x10000` | 12 |
| `CatchFlag` | `_CatchFlag_StateAir` | `0x40` | 0 |
| `CatchFlag` | `_CatchFlag_StateCrouch` | `0x80` | 0 |
| `CatchFlag` | `_CatchFlag_StateStand` | `0x20` | 0 |
| `CatchSuccess` | `_CatchSuccess_FlagHit_Enemy` | `0x8` | 7 |
| `CatchSuccess` | `_CatchSuccess_HitSub` | `0x1` | 8 |
| `CatchSuccess` | `_CatchSuccess_HitSub_Enemy` | `0x2` | 8 |
| `CatchSuccess` | `_CatchSuccess_HitSub_None` | `0x4` | 0 |
| `CatchSuccess` | `_CatchSuccess_NoMuteki` | `0x10000` | 0 |
| `CharaMoveMode` | `_CharaMoveMode_Disable` | `0x2` | 10 |
| `CharaMoveMode` | `_CharaMoveMode_Enable` | `0x0` | 3 |
| `CharaMoveMode` | `_CharaMoveMode_Limit` | `0x1` | 0 |
| `CharaPrio` | `_CharaPrio_Far` | `0x2` | 5 |
| `CharaPrio` | `_CharaPrio_Far_Layer_0` | `0xD` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_1` | `0xE` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_2` | `0xF` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_3` | `0x10` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_4` | `0x11` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_5` | `0x12` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_6` | `0x13` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_7` | `0x14` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_8` | `0x15` | 0 |
| `CharaPrio` | `_CharaPrio_Far_Layer_9` | `0x16` | 0 |
| `CharaPrio` | `_CharaPrio_GaugeCombo_P1` | `0x1B` | 0 |
| `CharaPrio` | `_CharaPrio_GaugeHP_P1` | `0x1C` | 0 |
| `CharaPrio` | `_CharaPrio_Near` | `0x1` | 8 |
| `CharaPrio` | `_CharaPrio_Near_Layer_0` | `0x3` | 0 |
| `CharaPrio` | `_CharaPrio_Near_Layer_1` | `0x4` | 1 |
| `CharaPrio` | `_CharaPrio_Near_Layer_2` | `0x5` | 1 |
| `CharaPrio` | `_CharaPrio_Near_Layer_3` | `0x6` | 1 |
| `CharaPrio` | `_CharaPrio_Near_Layer_4` | `0x7` | 1 |
| `CharaPrio` | `_CharaPrio_Near_Layer_5` | `0x8` | 0 |
| `CharaPrio` | `_CharaPrio_Near_Layer_6` | `0x9` | 0 |
| `CharaPrio` | `_CharaPrio_Near_Layer_7` | `0xA` | 0 |
| `CharaPrio` | `_CharaPrio_Near_Layer_8` | `0xB` | 0 |
| `CharaPrio` | `_CharaPrio_Near_Layer_9` | `0xC` | 0 |
| `CharaPrio` | `_CharaPrio_Near_P1` | `0x1A` | 0 |
| `CharaPrio` | `_CharaPrio_None` | `0x0` | 0 |
| `CharaPrio` | `_CharaPrio_Parent_BG` | `0x19` | 6 |
| `CharaPrio` | `_CharaPrio_Parent_M1` | `0x18` | 2 |
| `CharaPrio` | `_CharaPrio_Parent_P1` | `0x17` | 6 |
| `ClearFlag` | `_ClearFlag_ChangeFrame` | `0x2` | 30 |
| `ClearFlag` | `_ClearFlag_ChangeMv` | `0x1` | 445 |
| `ClearFlag` | `_ClearFlag_ChangePattern` | `0x4` | 133 |
| `ClearFlag` | `_ClearFlag_ComboEnd` | `0x40` | 0 |
| `ClearFlag` | `_ClearFlag_Landing` | `0x20` | 1 |
| `Direction` | `_Direction_Auto` | `0xFFFFFFFF` | 78 |
| `Direction` | `_Direction_Left` | `0x0` | 10 |
| `Direction` | `_Direction_Reverse` | `0xA` | 86 |
| `Direction` | `_Direction_Right` | `0x1` | 17 |
| `Exist` | `_Exist_NoAttackHantei` | `0x400` | 0 |
| `Exist` | `_Exist_NoCamera` | `0x1` | 13 |
| `Exist` | `_Exist_NoEtcHantei` | `0x800` | 0 |
| `Exist` | `_Exist_NoHantei` | `0xF00` | 34 |
| `Exist` | `_Exist_NoKasanariHantei` | `0x100` | 36 |
| `Exist` | `_Exist_NoKuraiHantei` | `0x200` | 0 |
| `Exist` | `_Exist_NoWall` | `0x2` | 18 |
| `ExistMode` | `_ExistMode_Add` | `0x1` | 10 |
| `ExistMode` | `_ExistMode_Erase` | `0x2` | 41 |
| `ExistMode` | `_ExistMode_Reverse` | `0x3` | 0 |
| `ExistMode` | `_ExistMode_Set` | `0x0` | 13 |
| `FrameFlagEx` | `_FrameFlagEx_ChakutiEnd` | `0x1` | 0 |
| `FrameFlagEx` | `_FrameFlagEx_JumpRel` | `0x4` | 0 |
| `FrameFlagEx` | `_FrameFlagEx_LEJumpRel` | `0x8` | 0 |
| `FrameFlagEx` | `_FrameFlagEx_LoopCheck` | `0x2` | 0 |
| `GetPos` | `_GetPos_DispCamera` | `0x4` | 14 |
| `GetPos` | `_GetPos_NoMuki` | `0x800` | 18 |
| `GetPos` | `_GetPos_Offset` | `0x100` | 16 |
| `GetPos` | `_GetPos_ToolOffset` | `0x1000` | 2 |
| `GetPos` | `_GetPos_TrueCamera` | `0x1` | 5 |
| `GetPos` | `_GetPos_TypeScreen` | `0x400` | 1 |
| `GetPos` | `_GetPos_TypeWall` | `0x200` | 2 |
| `GetPos` | `_GetPos_ViewCamera` | `0x2` | 11 |
| `GuardFlag` | `_GuardFlag_Air` | `0x2` | 0 |
| `GuardFlag` | `_GuardFlag_Crouch` | `0x4` | 0 |
| `GuardFlag` | `_GuardFlag_GuardAir` | `0x2` | 27 |
| `GuardFlag` | `_GuardFlag_GuardCrouch` | `0x4` | 26 |
| `GuardFlag` | `_GuardFlag_GuardStand` | `0x1` | 2 |
| `GuardFlag` | `_GuardFlag_ShAir` | `0x20` | 0 |
| `GuardFlag` | `_GuardFlag_ShCrouch` | `0x40` | 0 |
| `GuardFlag` | `_GuardFlag_ShStand` | `0x10` | 0 |
| `GuardFlag` | `_GuardFlag_ShXAir` | `0x100000` | 0 |
| `GuardFlag` | `_GuardFlag_ShXCrouch` | `0x200000` | 0 |
| `GuardFlag` | `_GuardFlag_ShXStand` | `0x80000` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldAir` | `0x20` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldCrouch` | `0x40` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldStand` | `0x10` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldXAir` | `0x100000` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldXCrouch` | `0x200000` | 0 |
| `GuardFlag` | `_GuardFlag_ShieldXStand` | `0x80000` | 0 |
| `GuardFlag` | `_GuardFlag_Stand` | `0x1` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughAir` | `0x200` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughBound` | `0x800` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughCrouch` | `0x400` | 2 |
| `GuardFlag` | `_GuardFlag_ThroughDownBound` | `0x2000` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughExceptBound` | `0x4000` | 11 |
| `GuardFlag` | `_GuardFlag_ThroughExceptDownBound` | `0x8000` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughGuardBound` | `0x1000` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughRemoveBound` | `0x10000` | 3 |
| `GuardFlag` | `_GuardFlag_ThroughRemoveDamage` | `0x20000` | 1 |
| `GuardFlag` | `_GuardFlag_ThroughRemoveDamagePlus` | `0x40000` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughRemoveGuardBound` | `0x400000` | 0 |
| `GuardFlag` | `_GuardFlag_ThroughStand` | `0x100` | 0 |
| `GuardFlag` | `_GuardFlag_XAir` | `0x200` | 0 |
| `GuardFlag` | `_GuardFlag_XBound` | `0x800` | 0 |
| `GuardFlag` | `_GuardFlag_XCrouch` | `0x400` | 0 |
| `GuardFlag` | `_GuardFlag_XDown` | `0x2000` | 0 |
| `GuardFlag` | `_GuardFlag_XExceptDown` | `0x8000` | 0 |
| `GuardFlag` | `_GuardFlag_XExceptGuard` | `0x4000` | 0 |
| `GuardFlag` | `_GuardFlag_XGuard` | `0x1000` | 0 |
| `GuardFlag` | `_GuardFlag_XRemoveBound` | `0x10000` | 0 |
| `GuardFlag` | `_GuardFlag_XRemoveDamage` | `0x20000` | 0 |
| `GuardFlag` | `_GuardFlag_XRemoveDamagePlus` | `0x40000` | 0 |
| `GuardFlag` | `_GuardFlag_XRemoveGuardBound` | `0x400000` | 0 |
| `GuardFlag` | `_GuardFlag_XStand` | `0x100` | 0 |
| `HC` | `_HC_EnemyObj` | `0x2` | 9 |
| `HC` | `_HC_EnemyPc` | `0x1` | 25 |
| `HC` | `_HC_FavourObj` | `0x8` | 5 |
| `HC` | `_HC_FavourPc` | `0x4` | 5 |
| `HC` | `_HC_WithoutNoHanteiFlagObj` | `0x10` | 7 |
| `Han6Hantei` | `_Han6Hantei_Attack` | `0x0` | 0 |
| `Han6Hantei` | `_Han6Hantei_Etc` | `0x3` | 0 |
| `Han6Hantei` | `_Han6Hantei_Kasanari` | `0x1` | 0 |
| `Han6Hantei` | `_Han6Hantei_Kurai` | `0x2` | 0 |
| `Hantei` | `_Hantei_Attack` | `0x3` | 17 |
| `Hantei` | `_Hantei_Error` | `0xFF8B344F` | 63 |
| `Hantei` | `_Hantei_Etc` | `0x2` | 88 |
| `Hantei` | `_Hantei_Kasanari` | `0x0` | 12 |
| `Hantei` | `_Hantei_Kurai` | `0x1` | 23 |
| `HanteiFlag` | `_HanteiFlag_Body` | `0x2` | 0 |
| `HanteiFlag` | `_HanteiFlag_FireBall` | `0x8` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx00` | `0x20` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx01` | `0x40` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx02` | `0x80` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx03` | `0x100` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx04` | `0x200` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx05` | `0x400` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx06` | `0x800` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx07` | `0x1000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx08` | `0x2000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx09` | `0x4000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx10` | `0x8000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx11` | `0x10000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx12` | `0x20000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx13` | `0x40000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx14` | `0x80000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx15` | `0x100000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx16` | `0x200000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx17` | `0x400000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx18` | `0x800000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx19` | `0x1000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx20` | `0x2000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx21` | `0x4000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx22` | `0x8000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx23` | `0x10000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_FlagEx24` | `0x20000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_Head` | `0x1` | 0 |
| `HanteiFlag` | `_HanteiFlag_Legs` | `0x4` | 0 |
| `HanteiFlag` | `_HanteiFlag_NoMukiChange` | `0x4` | 41 |
| `HanteiFlag` | `_HanteiFlag_Offset` | `0x2` | 9 |
| `HanteiFlag` | `_HanteiFlag_Reverse` | `0x40000000` | 0 |
| `HanteiFlag` | `_HanteiFlag_Throw` | `0x10` | 0 |
| `HanteiFlag` | `_HanteiFlag_Tool` | `0x1` | 24 |
| `HitCheckFlag` | `_HitCheckFlag_Body` | `0x2` | 24 |
| `HitCheckFlag` | `_HitCheckFlag_Dive` | `0x40` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FireBall` | `0x8` | 108 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx00` | `0x20` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx01` | `0x40` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx02` | `0x80` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx03` | `0x100` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx04` | `0x200` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx05` | `0x400` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx06` | `0x800` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx07` | `0x1000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx08` | `0x2000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx09` | `0x4000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx10` | `0x8000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx11` | `0x10000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx12` | `0x20000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx13` | `0x40000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx14` | `0x80000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx15` | `0x100000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx16` | `0x200000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx17` | `0x400000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx18` | `0x800000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx19` | `0x1000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx20` | `0x2000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx21` | `0x4000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx22` | `0x8000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx23` | `0x10000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_FlagEx24` | `0x20000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_Head` | `0x1` | 166 |
| `HitCheckFlag` | `_HitCheckFlag_Legs` | `0x4` | 169 |
| `HitCheckFlag` | `_HitCheckFlag_Reverse` | `0x40000000` | 0 |
| `HitCheckFlag` | `_HitCheckFlag_Throw` | `0x10` | 0 |
| `HitType` | `_HitType_Damage` | `0x2` | 32 |
| `HitType` | `_HitType_FlagSousai` | `0x10` | 0 |
| `HitType` | `_HitType_Guard` | `0x1` | 4 |
| `HitType` | `_HitType_Hit` | `0x7` | 18 |
| `HitType` | `_HitType_Partner` | `0x40` | 0 |
| `HitType` | `_HitType_Player` | `0x20` | 0 |
| `HitType` | `_HitType_Sousai` | `0x4` | 0 |
| `HitType` | `_HitType_SuperArmor` | `0x8` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsBound` | `0x1` | 1 |
| `ImpactFlag` | `_ImpactFlag_IsBound_Old` | `0x100` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsCapture` | `0x10` | 1 |
| `ImpactFlag` | `_ImpactFlag_IsCounter` | `0x80` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsDangerHP` | `0x40` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsFirstAttack` | `0x20` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsGuard` | `0x2` | 1 |
| `ImpactFlag` | `_ImpactFlag_IsHitNoPlus` | `0x400` | 0 |
| `ImpactFlag` | `_ImpactFlag_IsSuperArmor` | `0x200` | 0 |
| `InterruptType` | `_InterruptType_BlastCharge` | `0x8` | 0 |
| `InterruptType` | `_InterruptType_DrawMotion` | `0x3` | 0 |
| `InterruptType` | `_InterruptType_Jem` | `0x7` | 0 |
| `InterruptType` | `_InterruptType_Judge` | `0x2` | 0 |
| `InterruptType` | `_InterruptType_Ko_Atk` | `0x0` | 0 |
| `InterruptType` | `_InterruptType_Ko_Def` | `0x1` | 0 |
| `InterruptType` | `_InterruptType_LoseMotion` | `0x5` | 0 |
| `InterruptType` | `_InterruptType_SupportCharge` | `0x6` | 0 |
| `InterruptType` | `_InterruptType_TM_MoonDriveReset` | `0x9` | 0 |
| `InterruptType` | `_InterruptType_WinMotion` | `0x4` | 0 |
| `KOMode` | `_KOMode_ToEndWait` | `0xD0` | 0 |
| `KOMode` | `_KOMode_ToEndWait_Fade` | `0xD1` | 0 |
| `LiberateType` | `_LiberateType_Combo` | `0x2` | 0 |
| `LiberateType` | `_LiberateType_Max` | `0x1` | 0 |
| `LiberateType` | `_LiberateType_Normal` | `0x0` | 0 |
| `MODE` | `_MODE_TYPE__ARCADE` | `0x1` | 0 |
| `MODE` | `_MODE_TYPE__BOSS_RUSH` | `0x2` | 0 |
| `MODE` | `_MODE_TYPE__BOSS_RUSH_BATTLE` | `0x3` | 0 |
| `MODE` | `_MODE_TYPE__ETC` | `0x0` | 0 |
| `MODE` | `_MODE_TYPE__VERSUS` | `0x4` | 0 |
| `MoveCode0` | `_MoveCode0_NoMoveBasicAction` | `0x1000000` | 0 |
| `MvStFlag` | `_MvStFlag_CounterAtk` | `0x1` | 1 |
| `MvStFlag` | `_MvStFlag_CounterDef` | `0x2` | 0 |
| `MvStFlag` | `_MvStFlag_DangerHPAtk` | `0x8` | 0 |
| `MvStFlag` | `_MvStFlag_DangerHPDef` | `0x4` | 0 |
| `ObjFlags` | `_ObjFlags_EraseParentDamage` | `0x1` | 46 |
| `ObjFlags` | `_ObjFlags_EraseParentPatChange` | `0x20` | 198 |
| `ObjFlags` | `_ObjFlags_FromParentStop` | `0x8` | 30 |
| `ObjFlags` | `_ObjFlags_MoveTimeStop` | `0x400000` | 0 |
| `ObjFlags` | `_ObjFlags_MoveTimeStopAll` | `0x10000000` | 99 |
| `ObjFlags` | `_ObjFlags_MukiXPosMove` | `0x2000` | 5 |
| `ObjFlags` | `_ObjFlags_NoCamera` | `0x800000` | 65 |
| `ObjFlags` | `_ObjFlags_NoGround` | `0x40` | 299 |
| `ObjFlags` | `_ObjFlags_NoRender` | `0x20000000` | 92 |
| `ObjFlags` | `_ObjFlags_NoRenderBlackOut` | `0x200000` | 12 |
| `ObjFlags` | `_ObjFlags_NoRenderOrder` | `0x100000` | 29 |
| `ObjFlags` | `_ObjFlags_NoRenderOrderPlus` | `0x40000000` | 0 |
| `ObjFlags` | `_ObjFlags_ParentMove` | unresolved | 99 |
| `ObjFlags` | `_ObjFlags_ParentMuki` | `0x1000` | 12 |
| `ObjFlags` | `_ObjFlags_PatChangeNoLanding` | `0x4000` | 5 |
| `ObjFlags` | `_ObjFlags_RenderShadow` | `0x10000` | 17 |
| `ObjFlags` | `_ObjFlags_ToParentHitBack` | `0x8000` | 23 |
| `ObjFlags` | `_ObjFlags_ToParentHitStatus` | `0x40000` | 50 |
| `ObjFlags` | `_ObjFlags_ToParentStop` | `0x80000` | 39 |
| `ObjProcFlag` | `_ObjProcFlag_EraseParentDelete` | `0x8` | 3 |
| `ObjProcFlag` | `_ObjProcFlag_UnEraseDamageEx` | `0x4` | 0 |
| `ObjProcFlags` | `_ObjProcFlags_EraseChangeParentMv` | `0x2` | 53 |
| `ObjProcFlags` | `_ObjProcFlags_EraseParentNull` | `0x1` | 10 |
| `ObjType` | `_ObjType_Blade` | `0x3` | 5 |
| `ObjType` | `_ObjType_FireBall` | `0x2` | 20 |
| `PAniFlag` | `_PAniFlag_JpEqual` | `0x1` | 0 |
| `PAniFlag` | `_PAniFlag_JpGrater` | `0x2` | 0 |
| `PAniFlag` | `_PAniFlag_JpLess` | `0x3` | 0 |
| `PAniFrame` | `_PAniFrame_IpAccel` | `0x1` | 0 |
| `PAniFrame` | `_PAniFrame_IpAccelEx` | `0x3` | 0 |
| `PAniFrame` | `_PAniFrame_IpAtoD` | `0x5` | 0 |
| `PAniFrame` | `_PAniFrame_IpDecel` | `0x2` | 0 |
| `PAniFrame` | `_PAniFrame_IpDecelEx` | `0x4` | 0 |
| `PAniFrame` | `_PAniFrame_IpDtoA` | `0x6` | 0 |
| `PAniFrame` | `_PAniFrame_IpNone` | `0x7` | 0 |
| `PAniFrame` | `_PAniFrame_IpNormal` | `0x0` | 0 |
| `PCGaugeType` | `_PCGaugeType_Eltnum` | `0x2` | 1 |
| `PartnerFlag` | `_PartnerFlag_ToParentHitStatus` | `0x1` | 0 |
| `PartnerFlag` | `_PartnerFlag_ToParentHitStop` | `0x2` | 0 |
| `PosState` | `_PosState_Air` | `0x2` | 116 |
| `PosState` | `_PosState_Always` | `0x7` | 18 |
| `PosState` | `_PosState_Crouch` | `0x4` | 3 |
| `PosState` | `_PosState_Ground` | `0x5` | 104 |
| `PosState` | `_PosState_Stand` | `0x1`, `0xA` | 3 |
| `Position` | `_Position_Add` | `0x8` | 90 |
| `Position` | `_Position_CaptureChara` | `0x1` | 9 |
| `Position` | `_Position_CaptureShift` | `0x2` | 32 |
| `Position` | `_Position_ChangeMuki` | `0x4` | 99 |
| `Position` | `_Position_NoMoveChild` | `0x10` | 4 |
| `Position` | `_Position_ToolShift` | `0x2` | 236 |
| `PrioType` | `_PrioType_` | `0x7` | 0 |
| `SkillCount` | `_SkillCount_Assult` | `0x0` | 0 |
| `SkillCount` | `_SkillCount_ChainShift` | `0x1` | 0 |
| `SkillCount` | `_SkillCount_Sp` | `0x3` | 0 |
| `SkillCount` | `_SkillCount_SpEx` | `0x4` | 0 |
| `SkillCount` | `_SkillCount_SpIFW` | `0x5` | 0 |
| `SkillCount` | `_SkillCount_SpIFWX` | `0x6` | 0 |
| `SkillCount` | `_SkillCount_Throw` | `0x7` | 0 |
| `SkillCount` | `_SkillCount_ThrowRecover` | `0x8` | 0 |
| `SkillCount` | `_SkillCount_VeilOff` | `0x2` | 0 |
| `SkillType` | `_SkillType_ChainShift` | `0x8` | 3 |
| `SkillType` | `_SkillType_Ex` | `0x4` | 3 |
| `SkillType` | `_SkillType_ExSpecial` | `0x6` | 1 |
| `SkillType` | `_SkillType_None` | `0x0` | 11 |
| `SkillType` | `_SkillType_Normal` | `0x1` | 5 |
| `SkillType` | `_SkillType_Special` | `0x2` | 12 |
| `SpCommandFlag` | `_SpCommandFlag_2AB` | `0x0` | 0 |
| `SpCommandFlag` | `_SpCommandFlag_BC` | `0x1` | 0 |
| `SpGauge` | `_SpGauge_UseAll` | `0xFFFFFFFF` | 0 |
| `SpGauge` | `_SpGauge_UseBuffer` | `0xFFFFFFFE` | 0 |
| `SpGaugeMode` | `_SpGaugeMode_Liberate` | `0x1` | 0 |
| `SpGaugeMode` | `_SpGaugeMode_Normal` | `0x0` | 1 |
| `SpGaugeMode` | `_SpGaugeMode_OverLiberate` | `0x2` | 0 |
| `State` | `_State_Guard` | `0x1` | 0 |
| `State` | `_State_GuardCancel` | `0x2` | 0 |
| `Status` | `_Status_Air` | `0x1` | 0 |
| `Status` | `_Status_Crouch` | `0x2` | 0 |
| `Status` | `_Status_Stand` | `0x0` | 0 |
| `StatusFlag0` | `_StatusFlag0_GuardA` | `0x400` | 0 |
| `StatusFlag0` | `_StatusFlag0_GuardC` | `0x200` | 0 |
| `StatusFlag0` | `_StatusFlag0_GuardS` | `0x100` | 0 |
| `StatusFlag1` | `_StatusFlag1_ChainShift` | `0x8` | 0 |
| `StatusFlag1` | `_StatusFlag1_ExCancel` | `0x1` | 0 |
| `StatusFlag1` | `_StatusFlag1_GuardRev` | `0x80000000` | 0 |
| `StatusFlag1` | `_StatusFlag1_HitEraseDisable` | `0x10` | 0 |
| `StatusFlag1` | `_StatusFlag1_JumpCancel` | `0x4` | 0 |
| `ThrowRelease` | `_ThrowRelease_NoAttackHit` | `0x40` | 64 |
| `ThrowRelease` | `_ThrowRelease_NoBurst` | `0x4000` | 0 |
| `ThrowRelease` | `_ThrowRelease_NoGroundRecover` | `0x10` | 110 |
| `ThrowRelease` | `_ThrowRelease_NoVec` | `0x1` | 0 |
| `ThrowRelease` | `_ThrowRelease_NoVecTimeHosei` | `0x10000` | 6 |
| `ThrowRelease` | `_ThrowRelease_NoWallRecover` | `0x20` | 18 |
| `ThrowRelease` | `_ThrowRelease_ReverseVec` | `0x2` | 8 |
| `ThrowType` | `_ThrowType_Center` | `0x4` | 0 |
| `ThrowType` | `_ThrowType_HitNageMuteki` | `0x8` | 0 |
| `ThrowType` | `_ThrowType_IsDone` | `0x1` | 0 |
| `ThrowType` | `_ThrowType_Kasanari` | `0x2` | 0 |
| `ThrowType` | `_ThrowType_NoRecover` | `0x10` | 0 |
| `ThrowType` | `_ThrowType_NoRecoverEx` | `0x20` | 0 |
| `ThrowType` | `_ThrowType_TypeBlow` | `0x40` | 0 |
| `VecFlag` | `_VecFlag_Add` | `0x1` | 29 |
| `VecFlag` | `_VecFlag_NoMuki` | `0x2` | 11 |
| `Vector` | `_Vector_Bound` | `0x40000000` | 22 |
| `Vector` | `_Vector_Div` | `0x20000000` | 157 |
| `Vector` | `_Vector_DivKeep` | `0x8000000` | 27 |
| `Vector` | `_Vector_Keep` | `0x10000000` | 48 |
| `Vector` | `_Vector_Normal` | `0x80000000` | 342 |
| `defBtlFinish` | `_defBtlFinish_ExSpecial` | `0x3` | 0 |
| `defBtlFinish` | `_defBtlFinish_None` | `0x0` | 0 |
| `defBtlFinish` | `_defBtlFinish_Normal` | `0x1` | 0 |
| `defBtlFinish` | `_defBtlFinish_Special` | `0x2` | 0 |
| `eWinType` | `_eWinType_DoubleKo` | `0x3` | 0 |
| `eWinType` | `_eWinType_MissionEnd` | `0x4` | 0 |
| `eWinType` | `_eWinType_None` | `0x0` | 0 |
| `eWinType` | `_eWinType_NormalKo` | `0x1` | 0 |
| `eWinType` | `_eWinType_Timeup` | `0x2` | 0 |

## State-related native VM APIs (all items)

| API | Wrapper RVA(s) | Script uses |
|---|---|---:|
| `BCMDTbl.CheckCancel` | `0x494F80` | 26 |
| `BCMDTbl.CheckCancelFlag` | `0x495000` | 8 |
| `BCMDTbl.CheckPosState` | `0x2F930`, `0x48A9A0`, `0x495700` | 19 |
| `BCMDTbl.CheckState` | `0x494F20` | 0 |
| `BCMDTbl.GetCancelFlagData` | `0x494FB0` | 0 |
| `BCMDTbl.IsMoveAble` | `0x4957A0` | 0 |
| `BCMDTbl.ResetAirJump` | `0x494E30` | 0 |
| `BMvCore.GetBossFlag` | `0x474540` | 0 |
| `BMvCore.GetBossRushFlag` | `0x474510` | 0 |
| `BMvCore.GetCaptureCharaData` | `0x474A30` | 67 |
| `BMvCore.GetLastCatchCharaData` | `0x474700` | 0 |
| `BMvCore.GetLastDamageCharaData` | `0x4747C0` | 3 |
| `BMvCore.GetLastHitCharaData` | `0x474760` | 11 |
| `BMvCore.GetTagStatus` | `0x4745C0` | 0 |
| `BMvCore.SetLastDamageCharaData` | `0x474820` | 0 |
| `BMvCore.isPlayer` | `0x4742C0` | 0 |
| `BMvEff.AddAttackHitNum` | `0x47B7A0` | 2 |
| `BMvEff.AttackInfoString_Set` | `0x47A690` | 3 |
| `BMvEff.CapturePlayer` | `0x47F920` | 4 |
| `BMvEff.CheckObjectFlags` | `0x47DF60` | 0 |
| `BMvEff.ClearAttackHitNum` | `0x47B720` | 2 |
| `BMvEff.ClearGuardSP_Success` | `0x47A700` | 0 |
| `BMvEff.Cockpit_SetPrioU` | `0x478FC0` | 9 |
| `BMvEff.EraseObjectFlags` | `0x47DEE0` | 82 |
| `BMvEff.FadeProc_SetRenderFlag` | `0x47A670` | 12 |
| `BMvEff.GRD_AddValue` | `0x47AA40` | 1 |
| `BMvEff.GRD_CheckStock` | `0x47AC40` | 2 |
| `BMvEff.GRD_ClearBreak` | `0x47AE00` | 0 |
| `BMvEff.GRD_ClearVorpal` | `0x47AF00` | 0 |
| `BMvEff.GRD_CorrectBreakTime` | `0x47AFD0` | 0 |
| `BMvEff.GRD_GetBreak` | `0x47AF60` | 8 |
| `BMvEff.GRD_GetConvertCount` | `0x47ACE0` | 0 |
| `BMvEff.GRD_GetJudgeResult` | `0x47ABD0` | 68 |
| `BMvEff.GRD_GetJudgeWinCount` | `0x47AB90` | 0 |
| `BMvEff.GRD_GetTime` | `0x47AEC0` | 0 |
| `BMvEff.GRD_IsBreakImpact` | `0x47B0E0` | 1 |
| `BMvEff.GRD_SetBreak` | `0x47B080` | 0 |
| `BMvEff.GRD_SetConvertBreak` | `0x47AD20` | 0 |
| `BMvEff.GRD_SetSpFlag` | `0x47AE80` | 0 |
| `BMvEff.GRD_TS_AddValue` | `0x47A950` | 0 |
| `BMvEff.GRD_TS_SetPlusValue` | `0x47A9C0` | 0 |
| `BMvEff.GRD_UseStock` | `0x47AB00` | 2 |
| `BMvEff.GetAngle_FromVector` | `0x47C2A0` | 14 |
| `BMvEff.GetAttackHitPos` | `0x47B750` | 13 |
| `BMvEff.GetBoundVectorAngle` | `0x47B7F0` | 0 |
| `BMvEff.GetCameraPosition` | `0x47BC20` | 20 |
| `BMvEff.GetCamera_Clipping` | `0x47D630` | 0 |
| `BMvEff.GetPlayerMuteki` | `0x301B0`, `0x47B8B0` | 2 |
| `BMvEff.GetPlayerMutekiTimer` | `0x47B8E0` | 0 |
| `BMvEff.GetPointStatus` | `0x47C450` | 67 |
| `BMvEff.GetVector_FromAngle` | `0x47C320` | 43 |
| `BMvEff.GuardSP_Get` | `0x47A760` | 0 |
| `BMvEff.GuardSP_Set` | `0x47A790` | 0 |
| `BMvEff.GuardSP_Success` | `0x47A730` | 1 |
| `BMvEff.IsAttackRect` | `0x47E430` | 0 |
| `BMvEff.IsKuraiRect` | `0x47E3F0` | 1 |
| `BMvEff.IsMyStopTime` | `0x47D0F0` | 0 |
| `BMvEff.Liberate_Calc` | `0x47B150` | 0 |
| `BMvEff.Liberate_End` | `0x47B310` | 0 |
| `BMvEff.Liberate_Get` | `0x47B2D0` | 1 |
| `BMvEff.Liberate_GetTimeValue` | `0x47B140` | 0 |
| `BMvEff.Liberate_GetType` | `0x47B260` | 0 |
| `BMvEff.Liberate_OK` | `0x47B6B0` | 0 |
| `BMvEff.Liberate_Set` | `0x47B400` | 0 |
| `BMvEff.Liberate_SetMinusValue` | `0x47B390` | 0 |
| `BMvEff.Liberate_SetType` | `0x47B2A0` | 0 |
| `BMvEff.ObjProcFlags_Erase` | `0x47DE00` | 4 |
| `BMvEff.ObjProcFlags_Set` | `0x47DE70` | 48 |
| `BMvEff.SetBgSpeculer` | `0x4786D0` | 0 |
| `BMvEff.SetBoundSt` | `0x47F800` | 7 |
| `BMvEff.SetCamera_Clipping` | `0x47D640` | 68 |
| `BMvEff.SetCamera_UpdateFlag` | `0x47D610` | 10 |
| `BMvEff.SetExist` | `0x47DCF0` | 103 |
| `BMvEff.SetFlags` | `0x4B2D0` | 0 |
| `BMvEff.SetGuardPlusFlag` | `0x478C50` | 31 |
| `BMvEff.SetHitLimitCancel` | `0x47F8E0` | 0 |
| `BMvEff.SetHpGauge` | `0x47CDB0` | 11 |
| `BMvEff.SetNoDamageFlag` | `0x47CFF0` | 0 |
| `BMvEff.SetObjectFlags` | `0x47DFC0` | 417 |
| `BMvEff.SetPlayerTimer` | `0x47B950` | 39 |
| `BMvEff.SetPositionBufferFlag` | `0x47A8F0` | 16 |
| `BMvEff.SetSpGauge` | `0x47CAB0` | 0 |
| `BMvEff.SetStopTime` | `0x47D2E0` | 5 |
| `BMvEff.SetStopTimeAll` | `0x47D270` | 0 |
| `BMvEff.SetUkemiTime` | `0x47F740` | 1 |
| `BMvEff.SpGauge_GetAwakens` | `0x47C6F0` | 0 |
| `BMvEff.SpGauge_GetPlusCorrect_ComboTimePos` | `0x47C700` | 0 |
| `BMvEff.SpGauge_SetAwakens` | `0x47C6E0` | 0 |
| `BMvEff.SpGauge_SetLimit` | `0x47CA10` | 0 |
| `BMvEff.SpGauge_SetLimitBound` | `0x47C790` | 0 |
| `BMvEff.SpGauge_SetLimitCombo` | `0x47C880` | 8 |
| `BMvEff.SpGauge_SetZeroTime` | `0x47C970` | 0 |
| `BMvEff.TM_GetCharaGauge` | `0x478650` | 0 |
| `BMvEff.TM_IsCelestialVorpalGRDMode` | `0x478590` | 0 |
| `BMvEff.TM_IsNormalVorpalGRDMode` | `0x478500` | 0 |
| `BMvEff.ThrowChara_SetCamera` | `0x47FE80` | 48 |
| `BMvEff.ThrowChara_SetJoint` | `0x47FEF0` | 84 |
| `BMvEff.ThrowChara_Transfer` | `0x47FBD0` | 3 |
| `BMvEff.ThrowParam` | `0x47FF90` | 233 |
| `BMvEff.ThrowRelease` | `0x47FA40` | 151 |
| `BMvEff.VecHitFlag_Set` | `0x47F6B0` | 0 |
| `BMvTbl.AddAirCount` | `0x48AC80` | 162 |
| `BMvTbl.AddAirJumpCount` | `0x48AC30` | 4 |
| `BMvTbl.AddComboCount` | `0x4873C0` | 3 |
| `BMvTbl.AddHitCheckFlag` | `0x488100` | 4 |
| `BMvTbl.AddLP` | `0x48AE40` | 139 |
| `BMvTbl.AddLPEx` | `0x48AEE0` | 1 |
| `BMvTbl.AddPP` | `0x48AFB0` | 24 |
| `BMvTbl.AddSP` | `0x48B0B0` | 1 |
| `BMvTbl.AirSkill_Begin` | `0x486FE0` | 0 |
| `BMvTbl.AirSkill_Check` | `0x486F80` | 0 |
| `BMvTbl.BoundCorrect_Calc` | `0x4884F0` | 0 |
| `BMvTbl.CalcHitValue` | `0x488880` | 41 |
| `BMvTbl.CheckBlast_BoundInit` | `0x486790` | 0 |
| `BMvTbl.CheckBlast_IsNGStatus` | `0x4868C0` | 0 |
| `BMvTbl.CheckCharaAlive_str` | `0x486A90` | 0 |
| `BMvTbl.CheckFrameFinalize` | `0x4895F0` | 0 |
| `BMvTbl.CheckFurimuki` | `0x48BAC0` | 26 |
| `BMvTbl.CheckPosState` | `0x2F930`, `0x48A9A0`, `0x495700` | 2 |
| `BMvTbl.CheckRecoverCommandTiming` | `0x4891A0` | 0 |
| `BMvTbl.ClearAllAirCounts` | `0x48AC00` | 0 |
| `BMvTbl.ClearBound` | `0x48D2E0` | 0 |
| `BMvTbl.ClearGuard` | `0x48D0D0` | 0 |
| `BMvTbl.ClearHitStatus` | `0x48BE30` | 14 |
| `BMvTbl.ClearTriVector` | `0x48C9F0` | 0 |
| `BMvTbl.DamageFlag_Func` | `0x486750` | 0 |
| `BMvTbl.DamageFlag_IsBound` | `0x486720` | 0 |
| `BMvTbl.EraseHitCheckFlag` | `0x488070` | 5 |
| `BMvTbl.FromFinalize` | `0x48B550` | 28 |
| `BMvTbl.GetAirUkemi` | `0x4D0D0` | 0 |
| `BMvTbl.GetAirUkemiTimeMax` | `0x4D150` | 0 |
| `BMvTbl.GetAirUkemiTimeNow` | `0x4D140` | 0 |
| `BMvTbl.GetAtkCatchHanteiPos` | `0x4886E0` | 0 |
| `BMvTbl.GetAtkCatchIsDone` | `0x488750` | 0 |
| `BMvTbl.GetAtkGuardFlag` | `0x4889A0` | 11 |
| `BMvTbl.GetBoundFlag` | `0x4D100` | 0 |
| `BMvTbl.GetBoundTime` | `0x30140` | 0 |
| `BMvTbl.GetBoundTimeAll` | `0x4D0F0` | 0 |
| `BMvTbl.GetBoundVectorStatus` | `0x48D480` | 0 |
| `BMvTbl.GetCallCount` | `0x4D0B0` | 0 |
| `BMvTbl.GetCountMax` | `0x4D120` | 0 |
| `BMvTbl.GetCountMaxTrue` | `0x4D130` | 0 |
| `BMvTbl.GetCountNow` | `0x30190` | 0 |
| `BMvTbl.GetCounterHitFlag` | `0x487BC0` | 0 |
| `BMvTbl.GetDrawAlpha` | `0x487CC0` | 1 |
| `BMvTbl.GetFinalizeCode` | `0x48B580` | 8 |
| `BMvTbl.GetFlags` | `0x4D100` | 0 |
| `BMvTbl.GetHitCheckFlag` | `0x488150` | 1 |
| `BMvTbl.GetHitCheckMvFlag` | `0x488040` | 3 |
| `BMvTbl.GetHitStop` | `0x48BDA0` | 0 |
| `BMvTbl.GetHoseiBaseMinValue` | `0x487640` | 0 |
| `BMvTbl.GetHoseiMinValue` | `0x4876F0` | 0 |
| `BMvTbl.GetInvAtkFlag` | `0x4878B0` | 0 |
| `BMvTbl.GetInvDefFlag` | `0x487880` | 0 |
| `BMvTbl.GetLP` | `0x48AEB0` | 834 |
| `BMvTbl.GetLPEx` | `0x48AF70` | 8 |
| `BMvTbl.GetMuki` | `0x48BB00` | 200 |
| `BMvTbl.GetMvCancel` | `0x486DD0` | 1 |
| `BMvTbl.GetMvCount` | `0x30800` | 0 |
| `BMvTbl.GetMvCountFrame` | `0x4D160` | 0 |
| `BMvTbl.GetMvHitStatus` | `0x48BF20` | 68 |
| `BMvTbl.GetMvHitStatusBF` | `0x48BEA0` | 0 |
| `BMvTbl.GetMvRoundStatus` | `0x489310` | 15 |
| `BMvTbl.GetMvStageStatus` | `0x4894E0` | 30 |
| `BMvTbl.GetMvStatus` | `0x48C110` | 610 |
| `BMvTbl.GetMvStatusBF` | `0x48C070` | 9 |
| `BMvTbl.GetNoHoseiHitFlag` | `0x487E80` | 0 |
| `BMvTbl.GetPP` | `0x48B050` | 485 |
| `BMvTbl.GetPosition` | `0x48C760` | 209 |
| `BMvTbl.GetPositionBuffer` | `0x487170` | 0 |
| `BMvTbl.GetPower` | `0x30100`, `0x30150` | 0 |
| `BMvTbl.GetRecoverMvFlags` | `0x486690` | 3 |
| `BMvTbl.GetRecoverStatus` | `0x4891E0` | 0 |
| `BMvTbl.GetSP` | `0x48B170` | 2 |
| `BMvTbl.GetScale` | `0x48C170` | 2 |
| `BMvTbl.GetScreenPosition` | `0x48C6A0` | 0 |
| `BMvTbl.GetSkillLv` | `0x48B310` | 0 |
| `BMvTbl.GetSparkDisableAttack` | `0x48B400` | 0 |
| `BMvTbl.GetSparkDisableMove` | `0x48B3A0` | 0 |
| `BMvTbl.GetSubtitleFlag` | `0x486680` | 0 |
| `BMvTbl.GetSuperArmorFlag` | `0x487DC0` | 0 |
| `BMvTbl.GetTutoMvFlag` | `0x487260` | 1 |
| `BMvTbl.GetUkemifailedtime` | `0x300E0` | 0 |
| `BMvTbl.GetUkeminum_g` | `0x300F0` | 0 |
| `BMvTbl.GetVecCount` | `0x30120` | 0 |
| `BMvTbl.GetVecMuki` | `0x4D0C0` | 0 |
| `BMvTbl.GetVector` | `0x48C800` | 165 |
| `BMvTbl.GetWallCount` | `0x4D0E0` | 0 |
| `BMvTbl.HitPat_Check` | `0x4882B0` | 6 |
| `BMvTbl.IsBound` | `0x300E0` | 0 |
| `BMvTbl.IsCapture` | `0x4D0B0` | 0 |
| `BMvTbl.IsDown` | `0x4D110`, `0x4D1A0` | 0 |
| `BMvTbl.IsExistAtkCatchRect` | `0x488720` | 0 |
| `BMvTbl.IsFileAlive` | `0x48D0A0` | 0 |
| `BMvTbl.IsLanding` | `0x30150` | 0 |
| `BMvTbl.MoveStartPosition` | `0x48C4A0` | 0 |
| `BMvTbl.MvBoundStatus` | `0x4D110` | 0 |
| `BMvTbl.MvBoundVectorStatus` | `0x30100` | 0 |
| `BMvTbl.MvHitStatus` | `0x4D1A0` | 14 |
| `BMvTbl.MvStageStatus` | `0x4D190` | 0 |
| `BMvTbl.MvStatus` | `0x4D150` | 0 |
| `BMvTbl.PcGauge_Set` | `0x4885B0` | 1 |
| `BMvTbl.SetAirJumpOK` | `0x48AC50` | 3 |
| `BMvTbl.SetAliveFlag` | `0x487C40` | 0 |
| `BMvTbl.SetAsFlag` | `0x488AA0` | 13 |
| `BMvTbl.SetAsPosStatusFlag` | `0x488B50` | 0 |
| `BMvTbl.SetAsStatusFlag` | `0x488C00` | 46 |
| `BMvTbl.SetAtkCatchFlag` | `0x488790` | 10 |
| `BMvTbl.SetAtkGuardFlag` | `0x4889F0` | 36 |
| `BMvTbl.SetBoundFinalize` | `0x48D350` | 0 |
| `BMvTbl.SetBoundStatus` | `0x48D410` | 0 |
| `BMvTbl.SetCaptureHitFlag` | `0x487C80` | 0 |
| `BMvTbl.SetChipDamStatus` | `0x4888D0` | 6 |
| `BMvTbl.SetCounterHitFlag` | `0x487BF0` | 0 |
| `BMvTbl.SetDrawAlpha` | `0x487D00` | 7 |
| `BMvTbl.SetFinalize` | `0x48B5E0` | 389 |
| `BMvTbl.SetFinalizeCode` | `0x48B5B0` | 28 |
| `BMvTbl.SetForceUkemiTimeLimitFlag` | `0x487B40` | 23 |
| `BMvTbl.SetGrdLimit` | `0x487530` | 2 |
| `BMvTbl.SetGuardFinalize` | `0x48D1B0` | 0 |
| `BMvTbl.SetGuardStatus` | `0x48D270` | 0 |
| `BMvTbl.SetHitCheckFlag` | `0x4881C0` | 194 |
| `BMvTbl.SetHitStop` | `0x48BDF0` | 2 |
| `BMvTbl.SetHoseiBaseMinValue` | `0x487690` | 0 |
| `BMvTbl.SetHoseiMinValue` | `0x487740` | 0 |
| `BMvTbl.SetInvAtkFlag` | `0x487920` | 0 |
| `BMvTbl.SetInvDefFlag` | `0x4878E0` | 0 |
| `BMvTbl.SetKasanariValue` | `0x487D40` | 8 |
| `BMvTbl.SetLP` | `0x48AE80` | 1438 |
| `BMvTbl.SetLPEx` | `0x48AF30` | 1 |
| `BMvTbl.SetMoveableFlag` | `0x488DF0` | 26 |
| `BMvTbl.SetMoveableFlagEx` | `0x488CE0` | 2 |
| `BMvTbl.SetMuki` | `0x48BB40` | 187 |
| `BMvTbl.SetMvHitStatus` | `0x48BE60` | 15 |
| `BMvTbl.SetNoHoseiFlag` | `0x487F00` | 108 |
| `BMvTbl.SetNoHoseiHitFlag` | `0x487EC0` | 1 |
| `BMvTbl.SetNoUkemiTimeLimitFlag` | `0x487E40` | 2 |
| `BMvTbl.SetPP` | `0x48B000` | 439 |
| `BMvTbl.SetPartnerFlag` | `0x487B80` | 0 |
| `BMvTbl.SetPosition` | `0x201C70`, `0x48C4F0` | 437 |
| `BMvTbl.SetPrio` | `0x23780`, `0x48A5F0` | 25 |
| `BMvTbl.SetRecoverMvFlags` | `0x4866D0` | 0 |
| `BMvTbl.SetSP` | `0x48B110` | 1 |
| `BMvTbl.SetScale` | `0x48C1E0` | 50 |
| `BMvTbl.SetSkillLv` | `0x48B340` | 0 |
| `BMvTbl.SetSousaiFlag` | `0x487A80` | 0 |
| `BMvTbl.SetSpPrio` | `0x48A550` | 4 |
| `BMvTbl.SetSparkDisableAttack` | `0x48B3D0` | 0 |
| `BMvTbl.SetSparkDisableMove` | `0x48B370` | 0 |
| `BMvTbl.SetSuperArmorFlag` | `0x487E00` | 0 |
| `BMvTbl.SetTutoMvFlag` | `0x487290` | 27 |
| `BMvTbl.SetVector` | `0x48CB20` | 471 |
| `BMvTbl.SetVector_CCharaVector` | `0x48CA80` | 5 |
| `BMvTbl.SetVector_MaxX` | `0x48CAE0` | 26 |
| `BMvTbl.SetVirtualGuardFlag` | `0x487D80` | 0 |
| `BMvTbl.SetWallCount` | `0x48AD00` | 5 |
| `BMvTbl.TM_GetCancelShieldTiming` | `0x486E90` | 0 |
| `BMvTbl.TM_SetDownStatus` | `0x486F10` | 0 |
| `BMvTbl.TobiParamEndFlag_Func` | `0x48AA20` | 0 |
| `BMvTbl.UseSkill_Check` | `0x488390` | 1 |
| `BMvTbl.VGuard_CheckKeep` | `0x48BA90` | 0 |
| `BMvTbl.VGuard_Time` | `0x48BA50` | 0 |

## Character-owned state

The scripts access character-specific persistent state through PP slots. These
cannot be reduced to the engine `_Status` enum. The JSON catalog records every
referenced slot, PP flag and state-like symbol together with source files.

### PP slots referenced by scripts

| Symbol/index | Uses | Character files |
|---|---:|---|
| `0` | 4 | chr017, chr023 |
| `CDef_Enk_PP_HavocType` | 4 | chr017 |
| `CDef_Kuo_PP_DashAddTiming` | 1 | chr023 |
| `CDef_Kuo_PP_FFKeep` | 10 | chr023 |
| `CDef_Kuo_PP_FFMoveVecMuki` | 2 | chr023 |
| `CDef_Kuo_PP_FFMoveVecX` | 2 | chr023 |
| `CDef_Kuo_PP_FFMoveVecY` | 2 | chr023 |
| `CDef_Kuo_PP_FFStick` | 4 | chr023 |
| `CDef_Kuo_PP_FFZurashi` | 4 | chr023 |
| `CDef_Kuo_PP_FFfurimukiCheck` | 7 | chr023 |
| `CDef_Kuo_PP_HitStrikeFlashBlade` | 4 | chr023 |
| `CDef_Kuo_PP_ThrowRollingBall` | 4 | chr023 |
| `CDef_Lnd_PP_FFAddInput` | 4 | chr018 |
| `CDef_Lnd_PP_FreeMotion` | 4 | chr018 |
| `CDef_Lnd_PP_FreezeCheck` | 9 | chr018 |
| `CDef_Lnd_PP_FreezeCombo` | 5 | chr018 |
| `CDef_Lnd_PP_IceCoffin` | 9 | chr018 |
| `CDef_Lnd_PP_IcePillarID` | 3 | chr018 |
| `CDef_Lnd_PP_IcePillarLocked` | 3 | chr018 |
| `CDef_Lnd_PP_IceWedgeShot` | 4 | chr018 |
| `CDef_Pho_PP_BakuhaCount` | 16 | chr024 |
| `CDef_Tsu_PP_FFKeep` | 9 | chr019 |
| `CDef_Wag_PP_LastPowerUp` | 7 | chr016 |
| `CDef_Wag_PP_ShieldPowerUp` | 13 | chr016 |
| `CDef_Wag_PP_SwordHit` | 6 | chr016 |
| `CDef_Wag_PP_SwordPowerUp` | 15 | chr016 |
| `_checkPP` | 5 | chr016 |
| `another_weaponPP` | 3 | chr016 |
| `chp` | 1 | data |
| `def_ACS_IZU_ElefeeFlags` | 8 | chr026 |
| `def_ACS_IZU_ElefeeFlagsTmp` | 7 | chr026 |
| `def_ACS_IZU_ElefeeMode` | 21 | chr026 |
| `def_ACS_IZU_ElefeeMoveAddDivFrame` | 7 | chr026 |
| `def_ACS_IZU_ElefeeMoveDivFrame` | 6 | chr026 |
| `def_PP_Aka_KouseiSuccess` | 5 | chr014 |
| `def_PP_Aka_Near_StdB` | 3 | chr014 |
| `def_PP_Aka_Status` | 13 | chr014 |
| `def_PP_Aka_StdBandCType` | 8 | chr014 |
| `def_PP_Bya_LastWebTrapAirPosX` | 2 | chr013 |
| `def_PP_Bya_LastWebTrapAirPosY` | 2 | chr013 |
| `def_PP_Bya_LastWebTrapPosX` | 2 | chr013 |
| `def_PP_Bya_LastWebTrapPosY` | 2 | chr013 |
| `def_PP_Bya_LastWebTrapType` | 3 | chr013 |
| `def_PP_Car_214Hold` | 7 | chr003 |
| `def_PP_Car_BandC_Type` | 5 | chr003 |
| `def_PP_Car_BlodDrainObjID` | 3 | chr003 |
| `def_PP_Car_BlodDrainObjSt` | 3 | chr003 |
| `def_PP_Car_BloodPoolCount` | 4 | chr003 |
| `def_PP_Car_FreeMotionType` | 3 | chr003 |
| `def_PP_Cha_ButtonA_HoldFrame` | 4 | chr015 |
| `def_PP_Cha_ButtonB_HoldFrame` | 4 | chr015 |
| `def_PP_Cha_ButtonC_HoldFrame` | 4 | chr015 |
| `def_PP_Cha_ButtonHoldFrame` | 4 | chr015 |
| `def_PP_Cha_DahActList` | 37 | chr015 |
| `def_PP_Cha_DahActionPoint` | 40 | chr015 |
| `def_PP_Cha_DahFireBallSt` | 3 | chr015 |
| `def_PP_Cha_DahMode` | 18 | chr015 |
| `def_PP_Cha_DahNormalCancel` | 30 | chr015 |
| `def_PP_Cha_DahRiseUpYoyaku` | 7 | chr015 |
| `def_PP_Cha_DahStatus` | 21 | chr015 |
| `def_PP_Cha_DirectActionType` | 2 | chr015 |
| `def_PP_CmdStatus` | 4 | chr001, chr015, chr023 |
| `def_PP_Elt_AerialStatus` | 6 | chr011 |
| `def_PP_Elt_Bullet` | 14 | chr011 |
| `def_PP_Elt_CuttingSinkCount` | 6 | chr011 |
| `def_PP_Elt_FreeMotionType` | 3 | chr011 |
| `def_PP_Elt_PowBullet` | 8 | chr011 |
| `def_PP_Elt_ReloadTmp0` | 3 | chr011 |
| `def_PP_Elt_ReloadTmp1` | 6 | chr011 |
| `def_PP_Elt_SkillAddReload` | 6 | chr011 |
| `def_PP_GRDAction_UseGRD` | 3 | chr001, chr014, chr022 |
| `def_PP_Hil_3CCommand` | 7 | chr010 |
| `def_PP_Hil_HoldLv` | 7 | chr010 |
| `def_PP_Hyd_236Bakuha` | 6 | chr000 |
| `def_PP_Hyd_236BakuhaPosX` | 4 | chr000 |
| `def_PP_Hyd_236BakuhaPosY` | 4 | chr000 |
| `def_PP_Hyd_CrossBladeAddst` | 3 | chr000 |
| `def_PP_JumpFrame` | 2 | chr011, chr012 |
| `def_PP_JumpStatus` | 1 | chr014 |
| `def_PP_Kag_Cancel3C` | 3 | chr022 |
| `def_PP_LastPlaySound` | 1 | chr013 |
| `def_PP_Mik_B_B_FromDamage` | 3 | chr021 |
| `def_PP_Mik_FreeMotionType` | 3 | chr021 |
| `def_PP_Mik_MoveAtkAddCount` | 3 | chr021 |
| `def_PP_Mik_PP_J236InputType` | 4 | chr021 |
| `def_PP_Nan_StdBStickType` | 3 | chr012 |
| `def_PP_Ogr_BombSnapReady` | 7 | chr025 |
| `def_PP_Ogr_BombStatus` | 5 | chr025 |
| `def_PP_Ori_FFStickType` | 6 | chr004 |
| `def_PP_RecoverHoldMask` | 6 | chr007, chr010, chr020 |
| `def_PP_Set_214SakeStatus` | 17 | chr008 |
| `def_PP_Set_BlackShotPowStatus` | 2 | chr008 |
| `def_PP_Set_CreateBlackHole` | 3 | chr008 |
| `def_PP_Set_HitCount` | 3 | chr008 |
| `def_PP_StdComboChain` | 12 | chr009, chr010, chr012, chr016, chr018, chr021, chr022, chr023 |
| `def_PP_TMP0` | 4 | chr018 |
| `def_PP_Temp` | 23 | chr000, chr003, chr008, chr010 |
| `def_PP_Temp2` | 12 | chr008 |
| `def_PP_Udu_AirDiveCoffinLimit` | 5 | chr020 |
| `def_PP_Udu_CanRideCoffin` | 18 | chr020 |
| `def_PP_Udu_CoffinType` | 21 | chr020 |
| `def_PP_Udu_FFKeep` | 14 | chr020 |
| `def_PP_Udu_GusDamageStatus` | 6 | chr020 |
| `def_PP_Udu_OnCoffinType` | 2 | chr020 |
| `def_PP_Vat_Bit_CheckObject` | 3 | chr007 |
| `def_PP_Vat_Bit_ComboCount` | 7 | chr007 |
| `def_PP_Vat_Bit_DamageCount` | 5 | chr007 |
| `def_PP_Vat_Bit_is_Bombing` | 3 | chr007 |
| `def_PP_Wal_BandC_Type` | 1 | chr002 |
| `def_PP_Wal_DoubleCircle` | 7 | chr002 |
| `def_PP_Yuz_BattouA` | 34 | chr009 |
| `def_PP_Yuz_BattouAutoButton` | 20 | chr009 |
| `def_PP_Yuz_BattouB` | 38 | chr009 |
| `def_PP_Yuz_BattouC` | 34 | chr009 |
| `def_PP_Yuz_BattouD` | 28 | chr009 |
| `def_PP_Yuz_BattouMode` | 17 | chr009 |
| `def_PP_Yuz_CoolTimeBattouCnt` | 5 | chr009 |
| `def_TS_Bya_ThrowType` | 3 | chr013 |
| `def_TS_Bya_WebTrapAddJumpEnableInput` | 6 | chr013 |
| `slot` | 1 | chr009 |
| `v` | 2 | chr009 |
| `weaponPP` | 3 | chr016 |

### PP bit flags referenced by scripts

| Symbol | Uses | Character files |
|---|---:|---|
| `def_PPFlag_Aka_ElectDmgCreate` | 3 | chr014 |
| `def_PPFlag_Aka_KouseiHold` | 6 | chr014 |
| `def_PPFlag_Cha_DS_CallVanishEff` | 3 | chr015 |
| `def_PPFlag_Cha_DS_Hiding` | 24 | chr015 |
| `def_PPFlag_Cha_DS_Invisible` | 10 | chr015 |
| `def_PPFlag_Cha_DS_PowerfulMode` | 1 | chr015 |
| `def_PPFlag_Cha_DS_Rising` | 5 | chr015 |
| `def_PPFlag_Cha_DS_Vanishing` | 24 | chr015 |
| `def_PPFlag_Izu_EF_Event` | 7 | chr026 |
| `def_PPFlag_Izu_EF_NoActive` | 3 | chr026 |
| `def_PPFlag_Izu_EF_NoFinalize_UQChange` | 11 | chr026 |
| `def_PPFlag_Izu_EF_NoUpdate_InitUQ` | 3 | chr026 |

### Other character state-like symbols

| Symbol | Uses | Character files |
|---|---:|---|
| `CDef_Pho_BakuhaPowerUpTime` | 3 | chr024 |
| `CDef_Pho_PP_BakuhaCount` | 17 | chr024 |
| `CDef_Wag_PP_LastPowerUp` | 8 | chr016 |
| `CDef_Wag_PP_ShieldPowerUp` | 21 | chr016 |
| `CDef_Wag_PP_SwordPowerUp` | 35 | chr016 |
| `Def_Dbg_LocalDebugMode` | 12 | chr008, chr015, chr018, chr020, chr024, chr025, data |
| `Def_HitCheckFlag_AirDive` | 77 | chr000, chr001, chr002, chr003, chr004, chr005, chr006, chr007, chr008, chr009, chr010, chr011, chr012, chr013, chr014, chr016, chr017, chr018, chr019, chr020, chr021, chr022, chr023, chr024, chr025, chr026 |
| `Def_HitCheckFlag_LightLegs` | 43 | chr000, chr001, chr004, chr005, chr006, chr008, chr009, chr010, chr011, chr012, chr014, chr015, chr016, chr017, chr018, chr020, chr021, chr022, chr024, chr025, chr026 |
| `Def_SEP_DamageLv1` | 3 | chr023 |
| `Def_SEP_DamageLv2` | 3 | chr023 |
| `Def_SEP_DamageLv3` | 4 | chr023 |
| `Def_SEP_GuardLv1` | 3 | chr023 |
| `Def_SEP_GuardLv2` | 3 | chr023 |
| `Def_SEP_GuardLv3` | 3 | chr023 |
| `Def_Sys_SetSpGaugeLimit_Throw` | 9 | chr005, chr009, chr013 |
| `def_ACS_IZU_ElefeeFlags` | 8 | chr026 |
| `def_ACS_IZU_ElefeeFlagsTmp` | 7 | chr026 |
| `def_ACS_IZU_ElefeeMode` | 24 | chr026 |
| `def_AtkTmplFlags_Enable` | 52 | chr001, chr002, chr003, chr007, chr009, chr010, chr014, chr015, chr017, chr018, chr019, chr020, chr022, chr023, chr025, chr026 |
| `def_BallFlags_Finalize` | 1 | chr009 |
| `def_BallFlags_NoAddHitComboRate` | 66 | chr000, chr002, chr005, chr006, chr008, chr010, chr012, chr014, chr015, chr016, chr018, chr022, chr023, chr024 |
| `def_CHR_Dah_ActFlag_0202A` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_0202B` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_0202D` | 4 | chr015 |
| `def_CHR_Dah_ActFlag_0202EX` | 11 | chr015 |
| `def_CHR_Dah_ActFlag_214A` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_214B` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_214EX` | 15 | chr015 |
| `def_CHR_Dah_ActFlag_236A` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_236B` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_236EX` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_41236B` | 8 | chr015 |
| `def_CHR_Dah_ActFlag_421A` | 9 | chr015 |
| `def_CHR_Dah_ActFlag_623A` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_623B` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_623EX` | 13 | chr015 |
| `def_CHR_Dah_ActFlag_AirAct` | 18 | chr015 |
| `def_CHR_Dah_ActFlag_AppearAct` | 34 | chr015 |
| `def_CHR_Dah_ActFlag_ChaDmgVanish` | 4 | chr015 |
| `def_CHR_Dah_ActFlag_DahDmgVanish` | 10 | chr015 |
| `def_CHR_Dah_ActFlag_DahLimitVanish` | 9 | chr015 |
| `def_CHR_Dah_ActFlag_HideRock` | 2 | chr015 |
| `def_CHR_Dah_ActFlag_IW` | 8 | chr015 |
| `def_CHR_Dah_ActFlag_InputWalk` | 7 | chr015 |
| `def_CHR_Dah_ActFlag_RiseUp` | 6 | chr015 |
| `def_CHR_Dah_ActFlag_Stand` | 18 | chr015 |
| `def_CHR_Dah_ActFlag_Walk_B` | 7 | chr015 |
| `def_CHR_Dah_ActFlag_Walk_F` | 10 | chr015 |
| `def_CMDFlags_AnnounceSmaetSteer` | 27 | chr000, chr001, chr002, chr003, chr004, chr005, chr006, chr007, chr008, chr009, chr010, chr011, chr012, chr013, chr014, chr015, chr016, chr017, chr018, chr019, chr020, chr021, chr022, chr023, chr024, chr025, chr026 |
| `def_DF_CharaFlag1` | 18 | chr003, chr005, chr009, chr015, chr018, chr021, chr024 |
| `def_DF_CharaFlag2` | 4 | chr009, chr018 |
| `def_DF_CharaFlag3` | 2 | chr018 |
| `def_DF_MarkingBound` | 4 | chr018 |
| `def_FBTmplFlags_NewTypeFireBall` | 30 | chr000, chr007, chr010, chr012, chr014, chr016, chr018, chr020, chr022, chr023, chr025, chr026 |
| `def_FBTmplFlags_NoEXSLimit` | 2 | chr005, chr024 |
| `def_FBTmplFlags_NoVanishAtkCountZero` | 1 | chr012 |
| `def_FBTmplFlags_NoVanishDamage` | 3 | chr020, chr025 |
| `def_FBTmplFlags_NoVanishHit` | 6 | chr023, chr026 |
| `def_FBTmplFlags_NoVanishLand` | 1 | chr010 |
| `def_FBTmplFlags_NoVanishScreenOut` | 10 | chr007, chr010, chr012, chr023, chr025, chr026 |
| `def_JFN_SetExtendFlagPlayer` | 7 | chr015 |
| `def_LPDSFlags_Finalized` | 4 | chr015 |
| `def_LP_Dah_Status` | 6 | chr015 |
| `def_MC1_CharaFlag3` | 40 | chr009, chr011, chr014, chr015, chr017, chr018, chr020, chr023 |
| `def_MC1_CmdLvDZ_OK` | 14 | chr007, chr011, chr015, chr016, chr018, chr019, chr021, chr024 |
| `def_MC2_CharaFlag4` | 18 | chr014, chr015, chr017 |
| `def_MC2_CounterHit` | 1 | chr016 |
| `def_MC3_CharaFlag5` | 1 | chr015 |
| `def_MC6_NoSetUseExSkillFlag` | 8 | chr003, chr005, chr007, chr010, chr011, chr012, chr016, chr024 |
| `def_MC7_ThrowCounter` | 2 | chr017 |
| `def_MC_CharaFlag1` | 168 | chr006, chr007, chr009, chr011, chr012, chr013, chr014, chr015, chr016, chr017, chr018, chr019, chr020, chr023, chr025, chr026 |
| `def_MC_CharaFlag2` | 80 | chr006, chr009, chr011, chr015, chr017, chr018, chr020, chr023, chr025 |
| `def_MC_EnableAirAtkStatus` | 1 | chr015 |
| `def_MC_HitStatus_Damage` | 1 | chr004 |
| `def_MC_Sousai_NoSubHitCount` | 35 | chr000, chr002, chr004, chr007, chr008, chr010, chr011, chr015, chr016, chr017, chr021, chr022, chr026 |
| `def_PPFlag_Aka_ElectDmgCreate` | 3 | chr014 |
| `def_PPFlag_Aka_KouseiHold` | 6 | chr014 |
| `def_PPFlag_Cha_DS_CallVanishEff` | 3 | chr015 |
| `def_PPFlag_Cha_DS_Hiding` | 24 | chr015 |
| `def_PPFlag_Cha_DS_Invisible` | 10 | chr015 |
| `def_PPFlag_Cha_DS_PowerfulMode` | 1 | chr015 |
| `def_PPFlag_Cha_DS_Rising` | 5 | chr015 |
| `def_PPFlag_Cha_DS_Vanishing` | 24 | chr015 |
| `def_PPFlag_Izu_EF_Event` | 7 | chr026 |
| `def_PPFlag_Izu_EF_NoActive` | 3 | chr026 |
| `def_PPFlag_Izu_EF_NoFinalize_UQChange` | 11 | chr026 |
| `def_PPFlag_Izu_EF_NoUpdate_InitUQ` | 3 | chr026 |
| `def_PP_AirAtkStatus` | 3 | chr014, chr015 |
| `def_PP_Aka_Status` | 13 | chr014 |
| `def_PP_Car_BloodPoolCount` | 4 | chr003 |
| `def_PP_Cha_DahMode` | 18 | chr015 |
| `def_PP_Cha_DahStatus` | 21 | chr015 |
| `def_PP_CmdStatus` | 4 | chr001, chr015, chr023 |
| `def_PP_Elt_AerialStatus` | 6 | chr011 |
| `def_PP_Elt_CuttingSinkCount` | 7 | chr011 |
| `def_PP_Hil_HoldLv` | 7 | chr010 |
| `def_PP_JumpStatus` | 1 | chr014 |
| `def_PP_Mik_MoveAtkAddCount` | 3 | chr021 |
| `def_PP_Ogr_BombStatus` | 5 | chr025 |
| `def_PP_Set_214SakeStatus` | 17 | chr008 |
| `def_PP_Set_BlackShotPowStatus` | 2 | chr008 |
| `def_PP_Set_HitCount` | 3 | chr008 |
| `def_PP_Udu_GusDamageStatus` | 6 | chr020 |
| `def_PP_Vat_Bit_ComboCount` | 7 | chr007 |
| `def_PP_Vat_Bit_DamageCount` | 5 | chr007 |
| `def_PP_Yuz_BattouMode` | 18 | chr009 |
| `def_TmplFlags_Add` | 68 | chr000, chr001, chr002, chr003, chr004, chr005, chr006, chr007, chr008, chr010, chr012, chr013, chr015, chr017, chr018, chr022, chr023, chr024, chr026 |
| `def_TmplFlags_ChangeStatusOnly` | 33 | chr000, chr002, chr003, chr004, chr006, chr007, chr008, chr009, chr010, chr011, chr012, chr013, chr022, chr024 |
| `def_TmplFlags_NoAddComboRate` | 159 | chr000, chr001, chr002, chr003, chr004, chr005, chr006, chr007, chr008, chr009, chr010, chr011, chr012, chr013, chr014, chr015, chr016, chr017, chr018, chr019, chr020, chr021, chr022, chr023, chr024, chr025, chr026 |
| `def_TmplFlags_NoClearVector` | 6 | chr019, chr020, chr021, chr023 |
| `def_TmplFlags_NoFurimuki` | 19 | chr001, chr009, chr014, chr019, chr020, chr022, chr023, chr025 |
| `def_TmplFlags_NoSurinuke` | 2 | chr016, chr025 |

## Bound/status-effect table

| Slot | Definition | Duration | Effect interval |
|---:|---|---:|---:|
| 0 | 通常、変更しない | 0 | 0 |
| 1 | もえ | 60 | 6 |
| 2 | 凍結 | 90 | 4 |
| 3 | 感電 | 90 | 4 |
| 4 | 乱心 | 90 | 4 |
| 5 | ハイド状態異常やられ(赤い煙が散る) | 60 | 12 |
| 6 | オリエ状態異常やられ(光が横に広がり線になる) | 60 | 12 |
| 7 | バティスタ状態異常やられ(電撃が出る) | 60 | 12 |
| 8 | ゴルドー状態異常やられ(青い煙が散る) | 60 | 12 |
| 9 | 爆発やられ（燃えより激しい） | 60 | 6 |
| 10 | ロンドレキア状態以上やられ（短い凍結） | 20 | 4 |
| 11 | unassigned/default |  |  |
| 12 | unassigned/default |  |  |
| 13 | unassigned/default |  |  |
| 14 | unassigned/default |  |  |
| 15 | unassigned/default |  |  |

## Evidence warning

The complete item-level records are in `battle_state_catalog.json`. A name is
not marked display-safe merely because it appears here: setter storage, lifetime,
descriptor fallback and final consumer must be traced independently.
