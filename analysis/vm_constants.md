# UNI2 VM constant catalog

Generated from the pinned executable's VM registration strings. `value` is
decoded from the registration instruction when its form is recognized; blank
values remain unresolved and must not be guessed.

Total constants: 622

| Group | Count | Used by extracted scripts | Values decoded |
|---|---:|---:|---:|
| `ungrouped` | 78 | 4 | 40 |
| `GuardFlag` | 42 | 7 | 42 |
| `HanteiFlag` | 34 | 3 | 34 |
| `HitCheckFlag` | 32 | 4 | 32 |
| `eCMF` | 32 | 0 | 32 |
| `eComMoveFlag` | 32 | 32 | 31 |
| `CharaPrio` | 29 | 9 | 29 |
| `AtkFlag` | 25 | 0 | 25 |
| `ObjFlags` | 19 | 17 | 18 |
| `CatchFlag` | 15 | 8 | 15 |
| `libm` | 11 | 0 | 0 |
| `InterruptType` | 10 | 0 | 10 |
| `ImpactFlag` | 9 | 3 | 9 |
| `SkillCount` | 9 | 0 | 9 |
| `GetPos` | 8 | 8 | 8 |
| `HitType` | 8 | 3 | 8 |
| `PAniFrame` | 8 | 0 | 8 |
| `AsFlag` | 7 | 4 | 7 |
| `Exist` | 7 | 4 | 7 |
| `ThrowRelease` | 7 | 5 | 7 |
| `ThrowType` | 7 | 0 | 7 |
| `eComState` | 7 | 7 | 7 |
| `Position` | 6 | 6 | 6 |
| `SkillType` | 6 | 6 | 6 |
| `CancelFlag` | 5 | 5 | 5 |
| `CatchSuccess` | 5 | 3 | 5 |
| `ClearFlag` | 5 | 4 | 5 |
| `HC` | 5 | 5 | 5 |
| `Hantei` | 5 | 5 | 5 |
| `MODE` | 5 | 0 | 5 |
| `NetworkVsMode` | 5 | 0 | 5 |
| `PosState` | 5 | 5 | 5 |
| `StatusFlag1` | 5 | 0 | 5 |
| `Vector` | 5 | 5 | 5 |
| `eNetworkBattleMode` | 5 | 0 | 5 |
| `eWinType` | 5 | 0 | 5 |
| `Direction` | 4 | 4 | 4 |
| `ExistMode` | 4 | 3 | 4 |
| `FrameFlagEx` | 4 | 0 | 4 |
| `Han6Hantei` | 4 | 0 | 4 |
| `MvStFlag` | 4 | 1 | 4 |
| `NetworkVsControlType` | 4 | 0 | 4 |
| `defBtlFinish` | 4 | 0 | 4 |
| `eComButton` | 4 | 4 | 4 |
| `CharaMoveMode` | 3 | 2 | 3 |
| `DataType` | 3 | 2 | 3 |
| `LiberateType` | 3 | 0 | 3 |
| `PAniFlag` | 3 | 0 | 3 |
| `SeType` | 3 | 2 | 2 |
| `SpGaugeMode` | 3 | 1 | 3 |
| `Status` | 3 | 0 | 3 |
| `StatusFlag0` | 3 | 0 | 3 |
| `get` | 3 | 0 | 0 |
| `set` | 3 | 0 | 0 |
| `Angle` | 2 | 1 | 2 |
| `CamUpdateFlag` | 2 | 2 | 2 |
| `KOMode` | 2 | 0 | 2 |
| `ObjProcFlag` | 2 | 1 | 2 |
| `ObjProcFlags` | 2 | 2 | 2 |
| `ObjType` | 2 | 2 | 2 |
| `PartnerFlag` | 2 | 0 | 2 |
| `SpCommandFlag` | 2 | 0 | 2 |
| `SpGauge` | 2 | 0 | 2 |
| `State` | 2 | 0 | 2 |
| `VecFlag` | 2 | 2 | 2 |
| `eComSkillType` | 2 | 2 | 2 |
| `initialize` | 2 | 0 | 0 |
| `invalid` | 2 | 0 | 0 |
| `lock` | 2 | 0 | 0 |
| `register` | 2 | 0 | 0 |
| `unlock` | 2 | 0 | 0 |
| `CaptureHitFlag` | 1 | 0 | 1 |
| `MoveCode0` | 1 | 0 | 1 |
| `PCGaugeType` | 1 | 1 | 1 |
| `PrioType` | 1 | 0 | 1 |
| `c` | 1 | 0 | 0 |
| `charsize` | 1 | 0 | 1 |
| `com` | 1 | 0 | 0 |
| `configure` | 1 | 0 | 0 |
| `controlfp` | 1 | 0 | 0 |
| `crt` | 1 | 0 | 0 |
| `eMessageNo` | 1 | 0 | 1 |
| `except` | 1 | 0 | 0 |
| `floatsize` | 1 | 0 | 1 |
| `initterm` | 1 | 0 | 0 |
| `intsize` | 1 | 0 | 1 |
| `pdata` | 1 | 0 | 1 |
| `seh` | 1 | 0 | 0 |
| `version` | 1 | 0 | 1 |

## Angle

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Angle_AngleAdd` | `0x1` | 1 | `0x491385` |
| `_Angle_PositionAdd` | `0x2` | 0 | `0x49139F` |

## AsFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_AsFlag_ChainShift` | `0x2` | 3 | `0x491817` |
| `_AsFlag_DamageEx` | `0x100` | 1 | `0x491899` |
| `_AsFlag_ExCancel` | `0x1` | 7 | `0x4917FD` |
| `_AsFlag_GuardRev` | `0x4` | 4 | `0x491831` |
| `_AsFlag_Guard_Air` | `0x20` | 0 | `0x491865` |
| `_AsFlag_Guard_Crouch` | `0x40` | 0 | `0x49187F` |
| `_AsFlag_Guard_Stand` | `0x10` | 0 | `0x49184B` |

## AtkFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_AtkFlag_ArmorBreak` | `0x8000` | 0 | `0x497AAF` |
| `_AtkFlag_AttackStop` | `0x2000000` | 0 | `0x497A4B` |
| `_AtkFlag_ChgCounterVec` | `0x10` | 0 | `0x4978A2` |
| `_AtkFlag_ChgHitFlagVec` | `0x4000000` | 0 | `0x497A64` |
| `_AtkFlag_ChgReflexHitVec` | `0x4000` | 0 | `0x49796A` |
| `_AtkFlag_ComboEnd` | `0x4` | 0 | `0x497889` |
| `_AtkFlag_GuardStop` | `0x10000` | 0 | `0x497983` |
| `_AtkFlag_HitYure` | `0x40` | 0 | `0x4978D4` |
| `_AtkFlag_HpCut` | `0x1` | 0 | `0x497857` |
| `_AtkFlag_NoAirUkemi` | `0x80` | 0 | `0x4978ED` |
| `_AtkFlag_NoBoundCorrect` | `0x20000` | 0 | `0x49799C` |
| `_AtkFlag_NoBoundCorrectPlus` | `0x100000` | 0 | `0x4979E7` |
| `_AtkFlag_NoBurst` | `0x20000000` | 0 | `0x497A96` |
| `_AtkFlag_NoCounter` | `0x40000` | 0 | `0x4979B5` |
| `_AtkFlag_NoFirstAttack` | `0x1000` | 0 | `0x497951` |
| `_AtkFlag_NoGroundUkemi` | `0x100` | 0 | `0x497906` |
| `_AtkFlag_NoHitPlus` | `0x20` | 0 | `0x4978BB` |
| `_AtkFlag_NoHitStop` | `0x400` | 0 | `0x497938` |
| `_AtkFlag_NoKo` | `0x2` | 0 | `0x497870` |
| `_AtkFlag_NoPrio` | `0x200000` | 0 | `0x497A00` |
| `_AtkFlag_NoWallUkemi` | `0x800000` | 0 | `0x497A19` |
| `_AtkFlag_SwingPlus` | `0x1000000` | 0 | `0x497A32` |
| `_AtkFlag_TeamHit` | `0x200` | 0 | `0x49791F` |
| `_AtkFlag_TimeCorrect` | `0x8000000` | 0 | `0x497A7D` |
| `_AtkFlag_VectorSp` | `0x80000` | 0 | `0x4979CE` |

## CamUpdateFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CamUpdateFlag_NoX` | `0x1` | 2 | `0x477637` |
| `_CamUpdateFlag_NoY` | `0x2` | 3 | `0x477650` |

## CancelFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CancelFlag_Always` | `0x2` | 31 | `0x49172D` |
| `_CancelFlag_Damage` | `0x3` | 3 | `0x491747` |
| `_CancelFlag_Hit` | `0x1` | 9 | `0x491713` |
| `_CancelFlag_Invalid` | `0xFF` | 1 | `0x491761` |
| `_CancelFlag_None` | `0x0` | 30 | `0x4916F9` |

## CaptureHitFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CaptureHitFlag_Parent` | `0x1` | 0 | `0x491EC0` |

## CatchFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CatchFlag_AtkAirGuard` | `0x2` | 1 | `0x491AEE` |
| `_CatchFlag_AtkAirShield` | `0x200` | 1 | `0x491B8D` |
| `_CatchFlag_AtkAllGuard` | `0x7` | 7 | `0x491B69` |
| `_CatchFlag_AtkCrouchGuard` | `0x4` | 2 | `0x491AFD` |
| `_CatchFlag_AtkCrouchShield` | `0x400` | 2 | `0x491B9F` |
| `_CatchFlag_AtkGroundGuard` | `0x5` | 0 | `0x491B0C` |
| `_CatchFlag_AtkGroundShield` | `0x500` | 0 | `0x491BB1` |
| `_CatchFlag_AtkNoGuard` | `0x8` | 0 | `0x491B1B` |
| `_CatchFlag_AtkNoGuardThrow` | `0x10` | 0 | `0x491B2A` |
| `_CatchFlag_AtkStandGuard` | `0x1` | 6 | `0x491ADF` |
| `_CatchFlag_AtkStandShield` | `0x100` | 5 | `0x491B7B` |
| `_CatchFlag_Invalid_Through_ExceptBound` | `0x10000` | 12 | `0x491BC3` |
| `_CatchFlag_StateAir` | `0x40` | 0 | `0x491B48` |
| `_CatchFlag_StateCrouch` | `0x80` | 0 | `0x491B5A` |
| `_CatchFlag_StateStand` | `0x20` | 0 | `0x491B39` |

## CatchSuccess

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CatchSuccess_FlagHit_Enemy` | `0x8` | 7 | `0x491BFF` |
| `_CatchSuccess_HitSub` | `0x1` | 8 | `0x491BD2` |
| `_CatchSuccess_HitSub_Enemy` | `0x2` | 8 | `0x491BE1` |
| `_CatchSuccess_HitSub_None` | `0x4` | 0 | `0x491BF0` |
| `_CatchSuccess_NoMuteki` | `0x10000` | 0 | `0x491C11` |

## CharaMoveMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CharaMoveMode_Disable` | `0x2` | 10 | `0x491C3E` |
| `_CharaMoveMode_Enable` | `0x0` | 3 | `0x491C20` |
| `_CharaMoveMode_Limit` | `0x1` | 0 | `0x491C2F` |

## CharaPrio

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CharaPrio_Far` | `0x2` | 5 | `0x4918E7` |
| `_CharaPrio_Far_Layer_0` | `0xD` | 0 | `0x4919EF` |
| `_CharaPrio_Far_Layer_1` | `0xE` | 0 | `0x4919FE` |
| `_CharaPrio_Far_Layer_2` | `0xF` | 0 | `0x491A0D` |
| `_CharaPrio_Far_Layer_3` | `0x10` | 0 | `0x491A1C` |
| `_CharaPrio_Far_Layer_4` | `0x11` | 0 | `0x491A2B` |
| `_CharaPrio_Far_Layer_5` | `0x12` | 0 | `0x491A3A` |
| `_CharaPrio_Far_Layer_6` | `0x13` | 0 | `0x491A49` |
| `_CharaPrio_Far_Layer_7` | `0x14` | 0 | `0x491A58` |
| `_CharaPrio_Far_Layer_8` | `0x15` | 0 | `0x491A67` |
| `_CharaPrio_Far_Layer_9` | `0x16` | 0 | `0x491A76` |
| `_CharaPrio_GaugeCombo_P1` | `0x1B` | 0 | `0x491AC1` |
| `_CharaPrio_GaugeHP_P1` | `0x1C` | 0 | `0x491AD0` |
| `_CharaPrio_Near` | `0x1` | 8 | `0x4918CD` |
| `_CharaPrio_Near_Layer_0` | `0x3` | 0 | `0x491901` |
| `_CharaPrio_Near_Layer_1` | `0x4` | 1 | `0x49191B` |
| `_CharaPrio_Near_Layer_2` | `0x5` | 1 | `0x491935` |
| `_CharaPrio_Near_Layer_3` | `0x6` | 1 | `0x49194F` |
| `_CharaPrio_Near_Layer_4` | `0x7` | 1 | `0x491969` |
| `_CharaPrio_Near_Layer_5` | `0x8` | 0 | `0x491983` |
| `_CharaPrio_Near_Layer_6` | `0x9` | 0 | `0x49199D` |
| `_CharaPrio_Near_Layer_7` | `0xA` | 0 | `0x4919B7` |
| `_CharaPrio_Near_Layer_8` | `0xB` | 0 | `0x4919D1` |
| `_CharaPrio_Near_Layer_9` | `0xC` | 0 | `0x4919E0` |
| `_CharaPrio_Near_P1` | `0x1A` | 0 | `0x491AB2` |
| `_CharaPrio_None` | `0x0` | 0 | `0x4918B3` |
| `_CharaPrio_Parent_BG` | `0x19` | 6 | `0x491AA3` |
| `_CharaPrio_Parent_M1` | `0x18` | 2 | `0x491A94` |
| `_CharaPrio_Parent_P1` | `0x17` | 6 | `0x491A85` |

## ClearFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ClearFlag_ChangeFrame` | `0x2` | 30 | `0x49177B` |
| `_ClearFlag_ChangeMv` | `0x1` | 445 | `0x4917AF` |
| `_ClearFlag_ChangePattern` | `0x4` | 133 | `0x491795` |
| `_ClearFlag_ComboEnd` | `0x40` | 0 | `0x4917C9` |
| `_ClearFlag_Landing` | `0x20` | 1 | `0x4917E3` |

## DataType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_DataType_Me` | `0x0` | 0 | `0x477AC4` |
| `_DataType_Parent` | `0x2` | 7 | `0x477AE2` |
| `_DataType_Player` | `0x1` | 39 | `0x477AD3` |

## Direction

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Direction_Auto` | `0xFFFFFFFF` | 78 | `0x491281` |
| `_Direction_Left` | `0x0` | 10 | `0x49129B` |
| `_Direction_Reverse` | `0xA` | 86 | `0x4912CF` |
| `_Direction_Right` | `0x1` | 17 | `0x4912B5` |

## Exist

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Exist_NoAttackHantei` | `0x400` | 0 | `0x4774C0` |
| `_Exist_NoCamera` | `0x1` | 13 | `0x477443` |
| `_Exist_NoEtcHantei` | `0x800` | 0 | `0x4774D9` |
| `_Exist_NoHantei` | `0xF00` | 34 | `0x477475` |
| `_Exist_NoKasanariHantei` | `0x100` | 36 | `0x47748E` |
| `_Exist_NoKuraiHantei` | `0x200` | 0 | `0x4774A7` |
| `_Exist_NoWall` | `0x2` | 18 | `0x47745C` |

## ExistMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ExistMode_Add` | `0x1` | 10 | `0x47750B` |
| `_ExistMode_Erase` | `0x2` | 41 | `0x477524` |
| `_ExistMode_Reverse` | `0x3` | 0 | `0x47753D` |
| `_ExistMode_Set` | `0x0` | 13 | `0x4774F2` |

## FrameFlagEx

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_FrameFlagEx_ChakutiEnd` | `0x1` | 0 | `0x49772B` |
| `_FrameFlagEx_JumpRel` | `0x4` | 0 | `0x49775D` |
| `_FrameFlagEx_LEJumpRel` | `0x8` | 0 | `0x497776` |
| `_FrameFlagEx_LoopCheck` | `0x2` | 0 | `0x497744` |

## GetPos

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_GetPos_DispCamera` | `0x4` | 14 | `0x477731` |
| `_GetPos_NoMuki` | `0x800` | 18 | `0x477795` |
| `_GetPos_Offset` | `0x100` | 16 | `0x47774A` |
| `_GetPos_ToolOffset` | `0x1000` | 2 | `0x4777AE` |
| `_GetPos_TrueCamera` | `0x1` | 5 | `0x4776FF` |
| `_GetPos_TypeScreen` | `0x400` | 1 | `0x47777C` |
| `_GetPos_TypeWall` | `0x200` | 2 | `0x477763` |
| `_GetPos_ViewCamera` | `0x2` | 11 | `0x477718` |

## GuardFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_GuardFlag_Air` | `0x2` | 0 | `0x49746F` |
| `_GuardFlag_Crouch` | `0x4` | 0 | `0x497488` |
| `_GuardFlag_GuardAir` | `0x2` | 27 | `0x47796B` |
| `_GuardFlag_GuardCrouch` | `0x4` | 26 | `0x47797A` |
| `_GuardFlag_GuardStand` | `0x1` | 2 | `0x47795C` |
| `_GuardFlag_ShAir` | `0x20` | 0 | `0x4974D3` |
| `_GuardFlag_ShCrouch` | `0x40` | 0 | `0x4974EC` |
| `_GuardFlag_ShStand` | `0x10` | 0 | `0x4974A1`, `0x4974BA` |
| `_GuardFlag_ShXAir` | `0x100000` | 0 | `0x49751E` |
| `_GuardFlag_ShXCrouch` | `0x200000` | 0 | `0x497537` |
| `_GuardFlag_ShXStand` | `0x80000` | 0 | `0x497505` |
| `_GuardFlag_ShieldAir` | `0x20` | 0 | `0x477998` |
| `_GuardFlag_ShieldCrouch` | `0x40` | 0 | `0x4779A7` |
| `_GuardFlag_ShieldStand` | `0x10` | 0 | `0x477989` |
| `_GuardFlag_ShieldXAir` | `0x100000` | 0 | `0x4779CB` |
| `_GuardFlag_ShieldXCrouch` | `0x200000` | 0 | `0x4779DD` |
| `_GuardFlag_ShieldXStand` | `0x80000` | 0 | `0x4779B9` |
| `_GuardFlag_Stand` | `0x1` | 0 | `0x497456` |
| `_GuardFlag_ThroughAir` | `0x200` | 0 | `0x477A01` |
| `_GuardFlag_ThroughBound` | `0x800` | 0 | `0x477A25` |
| `_GuardFlag_ThroughCrouch` | `0x400` | 2 | `0x477A13` |
| `_GuardFlag_ThroughDownBound` | `0x2000` | 0 | `0x477A49` |
| `_GuardFlag_ThroughExceptBound` | `0x4000` | 11 | `0x477A5B` |
| `_GuardFlag_ThroughExceptDownBound` | `0x8000` | 0 | `0x477A6D` |
| `_GuardFlag_ThroughGuardBound` | `0x1000` | 0 | `0x477A37` |
| `_GuardFlag_ThroughRemoveBound` | `0x10000` | 3 | `0x477A7F` |
| `_GuardFlag_ThroughRemoveDamage` | `0x20000` | 1 | `0x477A91` |
| `_GuardFlag_ThroughRemoveDamagePlus` | `0x40000` | 0 | `0x477AA3` |
| `_GuardFlag_ThroughRemoveGuardBound` | `0x400000` | 0 | `0x477AB5` |
| `_GuardFlag_ThroughStand` | `0x100` | 0 | `0x4779EF` |
| `_GuardFlag_XAir` | `0x200` | 0 | `0x497569` |
| `_GuardFlag_XBound` | `0x800` | 0 | `0x49759B` |
| `_GuardFlag_XCrouch` | `0x400` | 0 | `0x497582` |
| `_GuardFlag_XDown` | `0x2000` | 0 | `0x4975CD` |
| `_GuardFlag_XExceptDown` | `0x8000` | 0 | `0x4975FF` |
| `_GuardFlag_XExceptGuard` | `0x4000` | 0 | `0x4975E6` |
| `_GuardFlag_XGuard` | `0x1000` | 0 | `0x4975B4` |
| `_GuardFlag_XRemoveBound` | `0x10000` | 0 | `0x497618` |
| `_GuardFlag_XRemoveDamage` | `0x20000` | 0 | `0x497631` |
| `_GuardFlag_XRemoveDamagePlus` | `0x40000` | 0 | `0x49764A` |
| `_GuardFlag_XRemoveGuardBound` | `0x400000` | 0 | `0x497663` |
| `_GuardFlag_XStand` | `0x100` | 0 | `0x497550` |

## HC

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_HC_EnemyObj` | `0x2` | 9 | `0x4775D3` |
| `_HC_EnemyPc` | `0x1` | 25 | `0x4775BA` |
| `_HC_FavourObj` | `0x8` | 5 | `0x477605` |
| `_HC_FavourPc` | `0x4` | 5 | `0x4775EC` |
| `_HC_WithoutNoHanteiFlagObj` | `0x10` | 7 | `0x47761E` |

## Han6Hantei

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Han6Hantei_Attack` | `0x0` | 0 | `0x497DCF` |
| `_Han6Hantei_Etc` | `0x3` | 0 | `0x497E1A` |
| `_Han6Hantei_Kasanari` | `0x1` | 0 | `0x497DE8` |
| `_Han6Hantei_Kurai` | `0x2` | 0 | `0x497E01` |

## Hantei

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Hantei_Attack` | `0x3` | 17 | `0x4775A1` |
| `_Hantei_Error` | `0xFF8B344F` | 63 | `0x477669` |
| `_Hantei_Etc` | `0x2` | 88 | `0x477588` |
| `_Hantei_Kasanari` | `0x0` | 12 | `0x477556` |
| `_Hantei_Kurai` | `0x1` | 23 | `0x47756F` |

## HanteiFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_HanteiFlag_Body` | `0x2` | 0 | `0x497AE1` |
| `_HanteiFlag_FireBall` | `0x8` | 0 | `0x497B13` |
| `_HanteiFlag_FlagEx00` | `0x20` | 0 | `0x497B5E` |
| `_HanteiFlag_FlagEx01` | `0x40` | 0 | `0x497B77` |
| `_HanteiFlag_FlagEx02` | `0x80` | 0 | `0x497B90` |
| `_HanteiFlag_FlagEx03` | `0x100` | 0 | `0x497BA9` |
| `_HanteiFlag_FlagEx04` | `0x200` | 0 | `0x497BC2` |
| `_HanteiFlag_FlagEx05` | `0x400` | 0 | `0x497BDB` |
| `_HanteiFlag_FlagEx06` | `0x800` | 0 | `0x497BF4` |
| `_HanteiFlag_FlagEx07` | `0x1000` | 0 | `0x497C0D` |
| `_HanteiFlag_FlagEx08` | `0x2000` | 0 | `0x497C26` |
| `_HanteiFlag_FlagEx09` | `0x4000` | 0 | `0x497C3F` |
| `_HanteiFlag_FlagEx10` | `0x8000` | 0 | `0x497C58` |
| `_HanteiFlag_FlagEx11` | `0x10000` | 0 | `0x497C71` |
| `_HanteiFlag_FlagEx12` | `0x20000` | 0 | `0x497C8A` |
| `_HanteiFlag_FlagEx13` | `0x40000` | 0 | `0x497CA3` |
| `_HanteiFlag_FlagEx14` | `0x80000` | 0 | `0x497CBC` |
| `_HanteiFlag_FlagEx15` | `0x100000` | 0 | `0x497CD5` |
| `_HanteiFlag_FlagEx16` | `0x200000` | 0 | `0x497CEE` |
| `_HanteiFlag_FlagEx17` | `0x400000` | 0 | `0x497D07` |
| `_HanteiFlag_FlagEx18` | `0x800000` | 0 | `0x497D20` |
| `_HanteiFlag_FlagEx19` | `0x1000000` | 0 | `0x497D39` |
| `_HanteiFlag_FlagEx20` | `0x2000000` | 0 | `0x497D52` |
| `_HanteiFlag_FlagEx21` | `0x4000000` | 0 | `0x497D6B` |
| `_HanteiFlag_FlagEx22` | `0x8000000` | 0 | `0x497D84` |
| `_HanteiFlag_FlagEx23` | `0x10000000` | 0 | `0x497D9D` |
| `_HanteiFlag_FlagEx24` | `0x20000000` | 0 | `0x497DB6` |
| `_HanteiFlag_Head` | `0x1` | 0 | `0x497AC8` |
| `_HanteiFlag_Legs` | `0x4` | 0 | `0x497AFA` |
| `_HanteiFlag_NoMukiChange` | `0x4` | 41 | `0x4776B4` |
| `_HanteiFlag_Offset` | `0x2` | 9 | `0x47769B` |
| `_HanteiFlag_Reverse` | `0x40000000` | 0 | `0x497B45` |
| `_HanteiFlag_Throw` | `0x10` | 0 | `0x497B2C` |
| `_HanteiFlag_Tool` | `0x1` | 24 | `0x477682` |

## HitCheckFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_HitCheckFlag_Body` | `0x2` | 24 | `0x491CA7` |
| `_HitCheckFlag_Dive` | `0x40` | 0 | `0x491CE3` |
| `_HitCheckFlag_FireBall` | `0x8` | 108 | `0x491CC5` |
| `_HitCheckFlag_FlagEx00` | `0x20` | 0 | `0x491D04` |
| `_HitCheckFlag_FlagEx01` | `0x40` | 0 | `0x491D13` |
| `_HitCheckFlag_FlagEx02` | `0x80` | 0 | `0x491D25` |
| `_HitCheckFlag_FlagEx03` | `0x100` | 0 | `0x491D37` |
| `_HitCheckFlag_FlagEx04` | `0x200` | 0 | `0x491D49` |
| `_HitCheckFlag_FlagEx05` | `0x400` | 0 | `0x491D5B` |
| `_HitCheckFlag_FlagEx06` | `0x800` | 0 | `0x491D6D` |
| `_HitCheckFlag_FlagEx07` | `0x1000` | 0 | `0x491D7F` |
| `_HitCheckFlag_FlagEx08` | `0x2000` | 0 | `0x491D91` |
| `_HitCheckFlag_FlagEx09` | `0x4000` | 0 | `0x491DA3` |
| `_HitCheckFlag_FlagEx10` | `0x8000` | 0 | `0x491DB5` |
| `_HitCheckFlag_FlagEx11` | `0x10000` | 0 | `0x491DC7` |
| `_HitCheckFlag_FlagEx12` | `0x20000` | 0 | `0x491DD9` |
| `_HitCheckFlag_FlagEx13` | `0x40000` | 0 | `0x491DEB` |
| `_HitCheckFlag_FlagEx14` | `0x80000` | 0 | `0x491DFD` |
| `_HitCheckFlag_FlagEx15` | `0x100000` | 0 | `0x491E0F` |
| `_HitCheckFlag_FlagEx16` | `0x200000` | 0 | `0x491E21` |
| `_HitCheckFlag_FlagEx17` | `0x400000` | 0 | `0x491E33` |
| `_HitCheckFlag_FlagEx18` | `0x800000` | 0 | `0x491E45` |
| `_HitCheckFlag_FlagEx19` | `0x1000000` | 0 | `0x491E57` |
| `_HitCheckFlag_FlagEx20` | `0x2000000` | 0 | `0x491E69` |
| `_HitCheckFlag_FlagEx21` | `0x4000000` | 0 | `0x491E7B` |
| `_HitCheckFlag_FlagEx22` | `0x8000000` | 0 | `0x491E8D` |
| `_HitCheckFlag_FlagEx23` | `0x10000000` | 0 | `0x491E9F` |
| `_HitCheckFlag_FlagEx24` | `0x20000000` | 0 | `0x491EB1` |
| `_HitCheckFlag_Head` | `0x1` | 166 | `0x491C98` |
| `_HitCheckFlag_Legs` | `0x4` | 169 | `0x491CB6` |
| `_HitCheckFlag_Reverse` | `0x40000000` | 0 | `0x491CF5` |
| `_HitCheckFlag_Throw` | `0x10` | 0 | `0x491CD4` |

## HitType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_HitType_Damage` | `0x2` | 32 | `0x4911CB` |
| `_HitType_FlagSousai` | `0x10` | 0 | `0x491219` |
| `_HitType_Guard` | `0x1` | 4 | `0x4911E5` |
| `_HitType_Hit` | `0x7` | 18 | `0x4911B1` |
| `_HitType_Partner` | `0x40` | 0 | `0x491267` |
| `_HitType_Player` | `0x20` | 0 | `0x49124D` |
| `_HitType_Sousai` | `0x4` | 0 | `0x4911FF` |
| `_HitType_SuperArmor` | `0x8` | 0 | `0x491233` |

## ImpactFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ImpactFlag_IsBound` | `0x1` | 1 | `0x49160F` |
| `_ImpactFlag_IsBound_Old` | `0x100` | 0 | `0x4916DF` |
| `_ImpactFlag_IsCapture` | `0x10` | 1 | `0x491691` |
| `_ImpactFlag_IsCounter` | `0x80` | 0 | `0x491643` |
| `_ImpactFlag_IsDangerHP` | `0x40` | 0 | `0x49165D` |
| `_ImpactFlag_IsFirstAttack` | `0x20` | 0 | `0x491677` |
| `_ImpactFlag_IsGuard` | `0x2` | 1 | `0x491629` |
| `_ImpactFlag_IsHitNoPlus` | `0x400` | 0 | `0x4916C5` |
| `_ImpactFlag_IsSuperArmor` | `0x200` | 0 | `0x4916AB` |

## InterruptType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_InterruptType_BlastCharge` | `0x8` | 0 | `0x4915DB` |
| `_InterruptType_DrawMotion` | `0x3` | 0 | `0x491559` |
| `_InterruptType_Jem` | `0x7` | 0 | `0x4915C1` |
| `_InterruptType_Judge` | `0x2` | 0 | `0x49153F` |
| `_InterruptType_Ko_Atk` | `0x0` | 0 | `0x49150B` |
| `_InterruptType_Ko_Def` | `0x1` | 0 | `0x491525` |
| `_InterruptType_LoseMotion` | `0x5` | 0 | `0x49158D` |
| `_InterruptType_SupportCharge` | `0x6` | 0 | `0x4915A7` |
| `_InterruptType_TM_MoonDriveReset` | `0x9` | 0 | `0x4915F5` |
| `_InterruptType_WinMotion` | `0x4` | 0 | `0x491573` |

## KOMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_KOMode_ToEndWait` | `0xD0` | 0 | `0x477AF4` |
| `_KOMode_ToEndWait_Fade` | `0xD1` | 0 | `0x477B06` |

## LiberateType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_LiberateType_Combo` | `0x2` | 0 | `0x477B33` |
| `_LiberateType_Max` | `0x1` | 0 | `0x477B24` |
| `_LiberateType_Normal` | `0x0` | 0 | `0x477B15` |

## MODE

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_MODE_TYPE__ARCADE` | `0x1` | 0 | `0x451409` |
| `_MODE_TYPE__BOSS_RUSH` | `0x2` | 0 | `0x451422` |
| `_MODE_TYPE__BOSS_RUSH_BATTLE` | `0x3` | 0 | `0x45143B` |
| `_MODE_TYPE__ETC` | `0x0` | 0 | `0x4513F0` |
| `_MODE_TYPE__VERSUS` | `0x4` | 0 | `0x451454` |

## MoveCode0

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_MoveCode0_NoMoveBasicAction` | `0x1000000` | 0 | `0x491F77` |

## MvStFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_MvStFlag_CounterAtk` | `0x1` | 1 | `0x491C5C` |
| `_MvStFlag_CounterDef` | `0x2` | 0 | `0x491C6B` |
| `_MvStFlag_DangerHPAtk` | `0x8` | 0 | `0x491C7A` |
| `_MvStFlag_DangerHPDef` | `0x4` | 0 | `0x491C89` |

## NetworkVsControlType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_NetworkVsControlType_Controller` | `0x0` | 0 | `0x491F38` |
| `_NetworkVsControlType_None` | `0xFF` | 0 | `0x491F65` |
| `_NetworkVsControlType_NotController` | `0x1` | 0 | `0x491F47` |
| `_NetworkVsControlType_Spectator` | `0x2` | 0 | `0x491F56` |

## NetworkVsMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_NetworkVsMode_None` | `0xFF`, `0x24A` | 0 | `0x4616A6`, `0x491F29` |
| `_NetworkVsMode_PlayerMatch` | `0x3` | 0 | `0x491F1A` |
| `_NetworkVsMode_RankMatch` | `0x2` | 0 | `0x491F0B` |
| `_NetworkVsMode_VsPlayerMatch` | `0x1` | 0 | `0x491EFC` |
| `_NetworkVsMode_VsRankMatch` | `0x0` | 0 | `0x491EED` |

## ObjFlags

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ObjFlags_EraseParentDamage` | `0x1` | 46 | `0x4771EB` |
| `_ObjFlags_EraseParentPatChange` | `0x20` | 198 | `0x477268` |
| `_ObjFlags_FromParentStop` | `0x8` | 30 | `0x4772FE` |
| `_ObjFlags_MoveTimeStop` | `0x400000` | 0 | `0x477394` |
| `_ObjFlags_MoveTimeStopAll` | `0x10000000` | 99 | `0x47729A` |
| `_ObjFlags_MukiXPosMove` | `0x2000` | 5 | `0x4772CC` |
| `_ObjFlags_NoCamera` | `0x800000` | 65 | `0x477362` |
| `_ObjFlags_NoGround` | `0x40` | 299 | `0x47737B` |
| `_ObjFlags_NoRender` | `0x20000000` | 92 | `0x477204` |
| `_ObjFlags_NoRenderBlackOut` | `0x200000` | 12 | `0x47721D` |
| `_ObjFlags_NoRenderOrder` | `0x100000` | 29 | `0x477236` |
| `_ObjFlags_NoRenderOrderPlus` | `0x40000000` | 0 | `0x47724F` |
| `_ObjFlags_ParentMove` |  | 99 | `0x4771CB` |
| `_ObjFlags_ParentMuki` | `0x1000` | 12 | `0x4772B3` |
| `_ObjFlags_PatChangeNoLanding` | `0x4000` | 5 | `0x477281` |
| `_ObjFlags_RenderShadow` | `0x10000` | 17 | `0x4772E5` |
| `_ObjFlags_ToParentHitBack` | `0x8000` | 23 | `0x477330` |
| `_ObjFlags_ToParentHitStatus` | `0x40000` | 50 | `0x477349` |
| `_ObjFlags_ToParentStop` | `0x80000` | 39 | `0x477317` |

## ObjProcFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ObjProcFlag_EraseParentDelete` | `0x8` | 3 | `0x4773F8` |
| `_ObjProcFlag_UnEraseDamageEx` | `0x4` | 0 | `0x4773DF` |

## ObjProcFlags

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ObjProcFlags_EraseChangeParentMv` | `0x2` | 53 | `0x4773C6` |
| `_ObjProcFlags_EraseParentNull` | `0x1` | 10 | `0x4773AD` |

## ObjType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ObjType_Blade` | `0x3` | 5 | `0x47742A` |
| `_ObjType_FireBall` | `0x2` | 20 | `0x477411` |

## PAniFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PAniFlag_JpEqual` | `0x1` | 0 | `0x4991AE` |
| `_PAniFlag_JpGrater` | `0x2` | 0 | `0x4991C4` |
| `_PAniFlag_JpLess` | `0x3` | 0 | `0x4991DD` |

## PAniFrame

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PAniFrame_IpAccel` | `0x1` | 0 | `0x49920F` |
| `_PAniFrame_IpAccelEx` | `0x3` | 0 | `0x499241` |
| `_PAniFrame_IpAtoD` | `0x5` | 0 | `0x499273` |
| `_PAniFrame_IpDecel` | `0x2` | 0 | `0x499228` |
| `_PAniFrame_IpDecelEx` | `0x4` | 0 | `0x49925A` |
| `_PAniFrame_IpDtoA` | `0x6` | 0 | `0x49928C` |
| `_PAniFrame_IpNone` | `0x7` | 0 | `0x4992A5` |
| `_PAniFrame_IpNormal` | `0x0` | 0 | `0x4991F6` |

## PCGaugeType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PCGaugeType_Eltnum` | `0x2` | 1 | `0x491C4D` |

## PartnerFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PartnerFlag_ToParentHitStatus` | `0x1` | 0 | `0x491ECF` |
| `_PartnerFlag_ToParentHitStop` | `0x2` | 0 | `0x491EDE` |

## PosState

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PosState_Air` | `0x2` | 116 | `0x49112F`, `0x4964EA` |
| `_PosState_Always` | `0x7` | 18 | `0x49117D`, `0x496535` |
| `_PosState_Crouch` | `0x4` | 3 | `0x491149`, `0x496503` |
| `_PosState_Ground` | `0x5` | 104 | `0x491163`, `0x49651C` |
| `_PosState_Stand` | `0x1`, `0xA` | 3 | `0x491115`, `0x4964CA` |

## Position

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Position_Add` | `0x8` | 90 | `0x491351` |
| `_Position_CaptureChara` | `0x1` | 9 | `0x4912E9` |
| `_Position_CaptureShift` | `0x2` | 32 | `0x491303` |
| `_Position_ChangeMuki` | `0x4` | 99 | `0x491337` |
| `_Position_NoMoveChild` | `0x10` | 4 | `0x49136B` |
| `_Position_ToolShift` | `0x2` | 236 | `0x49131D` |

## PrioType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_PrioType_` | `0x7` | 0 | `0x491197` |

## SeType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SeType_All` |  | 0 | `0x481C87` |
| `_SeType_Normal` | `0xFFFFFFFF` | 30 | `0x481CA7` |
| `_SeType_Player` | `0x0` | 43 | `0x481CC0` |

## SkillCount

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SkillCount_Assult` | `0x0` | 0 | `0x4778C1` |
| `_SkillCount_ChainShift` | `0x1` | 0 | `0x4778DA` |
| `_SkillCount_Sp` | `0x3` | 0 | `0x477902` |
| `_SkillCount_SpEx` | `0x4` | 0 | `0x477911` |
| `_SkillCount_SpIFW` | `0x5` | 0 | `0x477920` |
| `_SkillCount_SpIFWX` | `0x6` | 0 | `0x47792F` |
| `_SkillCount_Throw` | `0x7` | 0 | `0x47793E` |
| `_SkillCount_ThrowRecover` | `0x8` | 0 | `0x47794D` |
| `_SkillCount_VeilOff` | `0x2` | 0 | `0x4778F3` |

## SkillType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SkillType_ChainShift` | `0x8` | 3 | `0x4965CB` |
| `_SkillType_Ex` | `0x4` | 3 | `0x4965B2` |
| `_SkillType_ExSpecial` | `0x6` | 1 | `0x496599` |
| `_SkillType_None` | `0x0` | 11 | `0x49654E` |
| `_SkillType_Normal` | `0x1` | 5 | `0x496567` |
| `_SkillType_Special` | `0x2` | 12 | `0x496580` |

## SpCommandFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SpCommandFlag_2AB` | `0x0` | 0 | `0x496616` |
| `_SpCommandFlag_BC` | `0x1` | 0 | `0x49662F` |

## SpGauge

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SpGauge_UseAll` | `0xFFFFFFFF` | 0 | `0x4776CD` |
| `_SpGauge_UseBuffer` | `0xFFFFFFFE` | 0 | `0x4776E6` |

## SpGaugeMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_SpGaugeMode_Liberate` | `0x1` | 0 | `0x4777E0` |
| `_SpGaugeMode_Normal` | `0x0` | 1 | `0x4777C7` |
| `_SpGaugeMode_OverLiberate` | `0x2` | 0 | `0x4777F9` |

## State

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_State_Guard` | `0x1` | 0 | `0x4965E4` |
| `_State_GuardCancel` | `0x2` | 0 | `0x4965FD` |

## Status

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Status_Air` | `0x1` | 0 | `0x497424` |
| `_Status_Crouch` | `0x2` | 0 | `0x49743D` |
| `_Status_Stand` | `0x0` | 0 | `0x49740E` |

## StatusFlag0

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_StatusFlag0_GuardA` | `0x400` | 0 | `0x4977C1` |
| `_StatusFlag0_GuardC` | `0x200` | 0 | `0x4977A8` |
| `_StatusFlag0_GuardS` | `0x100` | 0 | `0x49778F` |

## StatusFlag1

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_StatusFlag1_ChainShift` | `0x8` | 0 | `0x49780C` |
| `_StatusFlag1_ExCancel` | `0x1` | 0 | `0x4977DA` |
| `_StatusFlag1_GuardRev` | `0x80000000` | 0 | `0x497825` |
| `_StatusFlag1_HitEraseDisable` | `0x10` | 0 | `0x49783E` |
| `_StatusFlag1_JumpCancel` | `0x4` | 0 | `0x4977F3` |

## ThrowRelease

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ThrowRelease_NoAttackHit` | `0x40` | 64 | `0x477844` |
| `_ThrowRelease_NoBurst` | `0x4000` | 0 | `0x4778A8` |
| `_ThrowRelease_NoGroundRecover` | `0x10` | 110 | `0x477812` |
| `_ThrowRelease_NoVec` | `0x1` | 0 | `0x477876` |
| `_ThrowRelease_NoVecTimeHosei` | `0x10000` | 6 | `0x47788F` |
| `_ThrowRelease_NoWallRecover` | `0x20` | 18 | `0x47782B` |
| `_ThrowRelease_ReverseVec` | `0x2` | 8 | `0x47785D` |

## ThrowType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_ThrowType_Center` | `0x4` | 0 | `0x4976AE` |
| `_ThrowType_HitNageMuteki` | `0x8` | 0 | `0x4976C7` |
| `_ThrowType_IsDone` | `0x1` | 0 | `0x49767C` |
| `_ThrowType_Kasanari` | `0x2` | 0 | `0x497695` |
| `_ThrowType_NoRecover` | `0x10` | 0 | `0x4976E0` |
| `_ThrowType_NoRecoverEx` | `0x20` | 0 | `0x4976F9` |
| `_ThrowType_TypeBlow` | `0x40` | 0 | `0x497712` |

## VecFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_VecFlag_Add` | `0x1` | 29 | `0x4913B9` |
| `_VecFlag_NoMuki` | `0x2` | 11 | `0x4913D3` |

## Vector

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_Vector_Bound` | `0x40000000` | 22 | `0x491407` |
| `_Vector_Div` | `0x20000000` | 157 | `0x491421` |
| `_Vector_DivKeep` | `0x8000000` | 27 | `0x491455` |
| `_Vector_Keep` | `0x10000000` | 48 | `0x49143B` |
| `_Vector_Normal` | `0x80000000` | 342 | `0x4913ED` |

## c

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_c_exit` |  | 0 |  |

## charsize

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_charsize_` | `0xFF` | 0 | `0x77477` |

## com

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_com_base_` |  | 0 | `0x16D0D8`, `0x47394F` |

## configure

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_configure_narrow_argv` |  | 0 |  |

## controlfp

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_controlfp_s` |  | 0 |  |

## crt

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_crt_atexit` |  | 0 |  |

## defBtlFinish

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_defBtlFinish_ExSpecial` | `0x3` | 0 | `0x451535` |
| `_defBtlFinish_None` | `0x0` | 0 | `0x4514EA` |
| `_defBtlFinish_Normal` | `0x1` | 0 | `0x451503` |
| `_defBtlFinish_Special` | `0x2` | 0 | `0x45151C` |

## eCMF

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eCMF_AirEnd` | `0x1000` | 0 | `0x16DADB` |
| `_eCMF_AirNext` | `0x100` | 0 | `0x16DA77` |
| `_eCMF_ButtonHold` | `0x80000000` | 0 | `0x16DCB6` |
| `_eCMF_CancelEnd` | `0x30000` | 0 | `0x16DB71` |
| `_eCMF_CancelNext` | `0xC0000` | 0 | `0x16DBBC` |
| `_eCMF_DamageEnd` | `0x80` | 0 | `0x16DA5E` |
| `_eCMF_DamageNext` | `0x8` | 0 | `0x16D9FA` |
| `_eCMF_DamageObjNext` | `0x20` | 0 | `0x16DA2C` |
| `_eCMF_EnemyAirEnd` | `0x2000000` | 0 | `0x16DC52` |
| `_eCMF_EnemyAirNext` | `0x800000` | 0 | `0x16DC20` |
| `_eCMF_EnemyBoundNext` | `0x100000` | 0 | `0x16DBD5` |
| `_eCMF_EnemyGroundEnd` | `0x4000000` | 0 | `0x16DC6B` |
| `_eCMF_EnemyGroundNext` | `0x1000000` | 0 | `0x16DC39` |
| `_eCMF_GroundEnd` | `0x2000` | 0 | `0x16DAF4` |
| `_eCMF_GroundNext` | `0x200` | 0 | `0x16DA90` |
| `_eCMF_GuardEnd` | `0x400000` | 0 | `0x16DC07` |
| `_eCMF_GuardNext` | `0x200000` | 0 | `0x16DBEE` |
| `_eCMF_HitEnd` | `0x40` | 0 | `0x16DA45` |
| `_eCMF_HitNext` | `0x4` | 0 | `0x16D9E1` |
| `_eCMF_HitObjNext` | `0x10` | 0 | `0x16DA13` |
| `_eCMF_MoveEnd` | `0x1` | 0 | `0x16D9AF` |
| `_eCMF_MoveableEnd` | `0x4000` | 0 | `0x16DB0D` |
| `_eCMF_MoveableNext` | `0x400` | 0 | `0x16DAA9` |
| `_eCMF_MovedisableEnd` | `0x8000` | 0 | `0x16DB26` |
| `_eCMF_MovedisableNext` | `0x800` | 0 | `0x16DAC2` |
| `_eCMF_NmCancelEnd` | `0x10000` | 0 | `0x16DB3F` |
| `_eCMF_NmCancelNext` | `0x40000` | 0 | `0x16DB8A` |
| `_eCMF_NoHitstopNext` | `0x8000000` | 0 | `0x16DC84` |
| `_eCMF_SpCancelEnd` | `0x20000` | 0 | `0x16DB58` |
| `_eCMF_SpCancelNext` | `0x80000` | 0 | `0x16DBA3` |
| `_eCMF_StickHold` | `0x40000000` | 0 | `0x16DC9D` |
| `_eCMF_ThroughEnd` | `0x2` | 0 | `0x16D9C8` |

## eComButton

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eComButton_A` | `0x1` | 93 | `0x16DD01` |
| `_eComButton_B` | `0x2` | 94 | `0x16DD1A` |
| `_eComButton_C` | `0x4` | 117 | `0x16DD33` |
| `_eComButton_D` | `0x8` | 52 | `0x16DD4C` |

## eComMoveFlag

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eComMoveFlag_AirEnd` | `0x1000` | 1 | `0x16D7BB` |
| `_eComMoveFlag_AirNext` | `0x100` | 7 | `0x16D757` |
| `_eComMoveFlag_ButtonHold` | `0x80000000` | 51 | `0x16D996` |
| `_eComMoveFlag_CancelEnd` | `0x30000` | 1 | `0x16D851` |
| `_eComMoveFlag_CancelNext` | `0xC0000` | 1 | `0x16D89C` |
| `_eComMoveFlag_DamageEnd` | `0x80` | 7 | `0x16D73E` |
| `_eComMoveFlag_DamageNext` | `0x8` | 9 | `0x16D6DA` |
| `_eComMoveFlag_DamageObjNext` | `0x20` | 2 | `0x16D70C` |
| `_eComMoveFlag_EnemyAirEnd` | `0x2000000` | 5 | `0x16D932` |
| `_eComMoveFlag_EnemyAirNext` | `0x800000` | 1 | `0x16D900` |
| `_eComMoveFlag_EnemyBoundNext` | `0x100000` | 9 | `0x16D8B5` |
| `_eComMoveFlag_EnemyGroundEnd` | `0x4000000` | 5 | `0x16D94B` |
| `_eComMoveFlag_EnemyGroundNext` | `0x1000000` | 1 | `0x16D919` |
| `_eComMoveFlag_GroundEnd` | `0x2000` | 1 | `0x16D7D4` |
| `_eComMoveFlag_GroundNext` | `0x200` | 3 | `0x16D770` |
| `_eComMoveFlag_GuardEnd` | `0x400000` | 3 | `0x16D8E7` |
| `_eComMoveFlag_GuardNext` | `0x200000` | 1 | `0x16D8CE` |
| `_eComMoveFlag_HitEnd` | `0x40` | 15 | `0x16D725` |
| `_eComMoveFlag_HitNext` | `0x4` | 28 | `0x16D6C1` |
| `_eComMoveFlag_HitObjNext` | `0x10` | 1 | `0x16D6F3` |
| `_eComMoveFlag_MoveEnd` |  | 308 | `0x16D688` |
| `_eComMoveFlag_MoveableEnd` | `0x4000` | 16 | `0x16D7ED` |
| `_eComMoveFlag_MoveableNext` | `0x400` | 16 | `0x16D789` |
| `_eComMoveFlag_MovedisableEnd` | `0x8000` | 1 | `0x16D806` |
| `_eComMoveFlag_MovedisableNext` | `0x800` | 1 | `0x16D7A2` |
| `_eComMoveFlag_NmCancelEnd` | `0x10000` | 2 | `0x16D81F` |
| `_eComMoveFlag_NmCancelNext` | `0x40000` | 2 | `0x16D86A` |
| `_eComMoveFlag_NoHitstopNext` | `0x8000000` | 2 | `0x16D964` |
| `_eComMoveFlag_SpCancelEnd` | `0x20000` | 2 | `0x16D838` |
| `_eComMoveFlag_SpCancelNext` | `0x80000` | 2 | `0x16D883` |
| `_eComMoveFlag_StickHold` | `0x40000000` | 146 | `0x16D97D` |
| `_eComMoveFlag_ThroughEnd` | `0x2` | 15 | `0x16D6A8` |

## eComSkillType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eComSkillType_Interrupt` | `0x1` | 15 | `0x16DCCF` |
| `_eComSkillType_NoInterrupt` | `0x2` | 7 | `0x16DCE8` |

## eComState

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eComState_Attack` | `0x100` | 1 | `0x16DDFB` |
| `_eComState_Bound` | `0x6` | 3 | `0x16DDC9` |
| `_eComState_Chance` | `0x80` | 1 | `0x16DDE2` |
| `_eComState_Damage` | `0x4` | 32 | `0x16DD97` |
| `_eComState_Grapped` | `0x8` | 1 | `0x16DDB0` |
| `_eComState_Guard` | `0x2` | 16 | `0x16DD7E` |
| `_eComState_MoveAble` | `0x1` | 7 | `0x16DD65` |

## eMessageNo

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eMessageNo_Default` | `0xFFFFFFFF` | 0 | `0x4513DA` |

## eNetworkBattleMode

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eNetworkBattleMode_CasualMatch` | `0x1` | 0 | `0x4414A1` |
| `_eNetworkBattleMode_None` | `0xFFFFFFFF` | 0 | `0x441472` |
| `_eNetworkBattleMode_Offline` | `0x0` | 0 | `0x441488` |
| `_eNetworkBattleMode_PlayerMatch` | `0x3` | 0 | `0x4414D3` |
| `_eNetworkBattleMode_RankMatch` | `0x2` | 0 | `0x4414BA` |

## eWinType

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_eWinType_DoubleKo` | `0x3` | 0 | `0x4514B8` |
| `_eWinType_MissionEnd` | `0x4` | 0 | `0x4514D1` |
| `_eWinType_None` | `0x0` | 0 | `0x45146D` |
| `_eWinType_NormalKo` | `0x1` | 0 | `0x451486` |
| `_eWinType_Timeup` | `0x2` | 0 | `0x45149F` |

## except

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_except_handler4_common` |  | 0 |  |

## floatsize

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_floatsize_` | `0xFF` | 0 | `0x774B8` |

## get

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_get_heap_handle` |  | 0 |  |
| `_get_narrow_winmain_command_line` |  | 0 |  |
| `_get_stream_buffer_pointers` |  | 0 |  |

## initialize

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_initialize_narrow_environment` |  | 0 |  |
| `_initialize_onexit_table` |  | 0 |  |

## initterm

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_initterm_e` |  | 0 |  |

## intsize

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_intsize_` | `0xFF` | 0 | `0x77499` |

## invalid

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_invalid_parameter_noinfo` |  | 0 |  |
| `_invalid_parameter_noinfo_noreturn` |  | 0 |  |

## libm

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_libm_sse2_acos_precise` |  | 0 |  |
| `_libm_sse2_asin_precise` |  | 0 |  |
| `_libm_sse2_atan_precise` |  | 0 |  |
| `_libm_sse2_cos_precise` |  | 0 |  |
| `_libm_sse2_exp_precise` |  | 0 |  |
| `_libm_sse2_log10_precise` |  | 0 |  |
| `_libm_sse2_log_precise` |  | 0 |  |
| `_libm_sse2_pow_precise` |  | 0 |  |
| `_libm_sse2_sin_precise` |  | 0 |  |
| `_libm_sse2_sqrt_precise` |  | 0 |  |
| `_libm_sse2_tan_precise` |  | 0 |  |

## lock

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_lock_file` |  | 0 |  |
| `_lock_locales` |  | 0 |  |

## pdata

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_pdata_` | `0x7` | 0 | `0x1167C6` |

## register

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_register_onexit_function` |  | 0 |  |
| `_register_thread_local_exe_atexit_callback` |  | 0 |  |

## seh

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_seh_filter_exe` |  | 0 |  |

## set

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_set_app_type` |  | 0 |  |
| `_set_fmode` |  | 0 |  |
| `_set_new_mode` |  | 0 |  |

## ungrouped

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_CBtlCharaTable` | `0xF` | 0 | `0x15DC6F` |
| `_CIatan2` |  | 0 |  |
| `_CIexp` |  | 0 |  |
| `_CIfmod` |  | 0 |  |
| `_CIsqrt` |  | 0 |  |
| `_CPcBoundEff` | `0xC` | 0 | `0x19CBA6` |
| `_CommandTable` | `0xD` | 0 | `0x240F93` |
| `_CxxThrowException` |  | 0 |  |
| `_D8i` |  | 0 |  |
| `_DSV` |  | 0 |  |
| `_DevPS3` | `0x0` | 0 | `0x4910AD` |
| `_DevPS4` | `0x0` | 0 | `0x4910E1` |
| `_DevPS5` | `0x0` | 0 | `0x4910FB` |
| `_DevVITA` | `0x0` | 0 | `0x4910C7` |
| `_DevWindows` | `0x1` | 0 | `0x491093` |
| `_FileType` | `0x941128` | 0 | `0x15EE7A` |
| `_LVj` |  | 0 |  |
| `_LogsFile` | `0x40F950` | 0 | `0x495CF9` |
| `_MoveTable` | `0xA` | 0 | `0x240B83` |
| `_PlatformAPM` | `0x0` | 0 | `0x491079` |
| `_PlatformType` | `0x0` | 0 | `0x49105F` |
| `_RDATA` |  | 0 |  |
| `_STR` |  | 0 |  |
| `_ValAdd` | `0x2` | 46 | `0x4914A3` |
| `_ValCheck` | `0x5` | 0 | `0x4914F1` |
| `_ValClear` | `0x3` | 3 | `0x4914BD` |
| `_ValErase` | `0x4` | 0 | `0x4914D7` |
| `_ValGet` | `0x1` | 26 | `0x491489` |
| `_ValSet` | `0x0` | 28 | `0x49146F` |
| `_add` | `0xFF` | 0 | `0x63DE1` |
| `_call` | `0xFF` | 0 | `0x64495` |
| `_callnewh` |  | 0 |  |
| `_cexit` |  | 0 |  |
| `_chg` |  | 0 | `0x24DBED`, `0x24DCBC`, `0x24EE42`, `0x24EEED` |
| `_cloned` | `0xFF` | 0 | `0x64531` |
| `_close` | `0x6` | 0 | `0x24DBDD`, `0x24DC61`, `0x24EE32`, `0x24EEA6`, `0x250CDB` |
| `_cmp` | `0xFF` | 0 | `0x643F9` |
| `_configthreadlocale` |  | 0 |  |
| `_delslot` | `0xFF` | 0 | `0x64669` |
| `_div` | `0xFF` | 0 | `0x63FB5` |
| `_errno` |  | 0 |  |
| `_except1` |  | 0 |  |
| `_exit` |  | 0 |  |
| `_fseeki64` |  | 0 |  |
| `_fsopen` |  | 0 |  |
| `_gSh` |  | 0 |  |
| `_get` | `0xFF` | 0 | `0x30331`, `0x42BA1`, `0x47371`, `0x47A91`, `0x48841`, `0x49F9E`, `0x4A161`, `0x4B4D1`, `0x4B681`, `0x4CBD1`, `0x4E1C1`, `0x4E371`, `0x4E521`, `0x4E6D1`, `0x4E881`, `0x4EA31`, `0x4EBE1`, `0x4ED91`, `0x4EF41`, `0x4F131`, `0x4F2E1`, `0x4F491`, `0x4F641`, `0x4F7F1`, `0x4F9A1`, `0x4FB51`, `0x51531`, `0x516E1`, `0x53011`, `0x531C1`, `0x53371`, `0x64225` |
| `_gmtime64` |  | 0 |  |
| `_inherited` | `0xFF` | 0 | `0x6483D` |
| `_initterm` |  | 0 |  |
| `_isDebugModeExe` |  | 0 | `0x49103E` |
| `_itoa` |  | 0 |  |
| `_jpj` |  | 0 |  |
| `_localtime64` |  | 0 |  |
| `_loop` | `0x5` | 0 | `0x24DBFD`, `0x24DC47`, `0x24EE52`, `0x24EE90`, `0x251064` |
| `_mktime64` |  | 0 |  |
| `_modulo` | `0xFF` | 0 | `0x640ED` |
| `_mul` | `0xFF` | 0 | `0x63F19` |
| `_newmember` | `0xFF` | 0 | `0x647A1` |
| `_newslot` | `0xFF` | 0 | `0x645CD` |
| `_nexti` | `0xFF` | 0 | `0x6435D` |
| `_open` | `0x5`, `0xF` | 0 | `0x24DBCD`, `0x24DC18`, `0x24DC95`, `0x24EE22`, `0x24EE69`, `0x24EECD`, `0x25084E` |
| `_purecall` |  | 0 |  |
| `_putenv` |  | 0 |  |
| `_set` | `0xFF` | 0 | `0x302F0`, `0x42B60`, `0x47330`, `0x47A50`, `0x48800`, `0x49F54`, `0x4A120`, `0x4B490`, `0x4B640`, `0x4CB90`, `0x4E180`, `0x4E330`, `0x4E4E0`, `0x4E690`, `0x4E840`, `0x4E9F0`, `0x4EBA0`, `0x4ED50`, `0x4EF00`, `0x4F0F0`, `0x4F2A0`, `0x4F450`, `0x4F600`, `0x4F7B0`, `0x4F960`, `0x4FB10`, `0x514F0`, `0x516A0`, `0x52FD0`, `0x53180`, `0x53330`, `0x64189` |
| `_setjmp3` |  | 0 |  |
| `_splitpath` |  | 0 |  |
| `_strdup` |  | 0 |  |
| `_stricmp` |  | 0 |  |
| `_strnicmp` |  | 0 |  |
| `_sub` | `0xFF` | 0 | `0x63E7D` |
| `_time64` |  | 0 |  |
| `_tostring` | `0xFF` | 0 | `0x64705` |
| `_typeof` | `0xFF` | 0 | `0x642C1` |
| `_tzset` |  | 0 |  |
| `_unm` | `0xFF` | 0 | `0x64051` |
| `_wcsdup` |  | 0 |  |
| `_xPS` |  | 0 |  |

## unlock

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_unlock_file` |  | 0 |  |
| `_unlock_locales` |  | 0 |  |

## version

| Name | Value | Script uses | Registration RVA |
|---|---:|---:|---:|
| `_version_` | `0xFF` | 0 | `0x77453` |
