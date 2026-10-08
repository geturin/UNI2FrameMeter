# UNI2 Frame Meter

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

一个用于《UNDER NIGHT IN-BIRTH II Sys:Celes》训练模式的帧条显示工具。它会在游戏画面底部显示双方每一帧的行动状态，帮助玩家直观查看招式的发生、攻击判定、收招、硬直差、无敌和取消窗口。

**0.6.0-rc.2 是原生 hook 候选版。** 32 位辅助程序将帧条 DLL 加载到游戏中；DLL 在原生战斗更新函数处采集每 tick 的完整快照，通过共享内存传给独立叠加窗口。原游戏函数照常执行，不模拟战斗，也不需要修改游戏脚本。上一候选版已经用户确认可在训练模式正常运作；本版新增色带仍需实机确认。

## 示范视频

[在哔哩哔哩观看](https://www.bilibili.com/video/BV13ugM6vE3d/)

视频展示的是旧版 0.5 的帧条功能，不代表新版 hook 已通过实机验证。

## 主要功能

- 双行帧条：上方为 1P，下方为 2P。
- 显示发生、攻击判定、收招和行动受限时间。
- 可选显示取消属性、无敌属性、双向防御辅助和场上有效飞行道具。
- 同一帧存在多个属性时，以多层颜色同时显示。
- 自动标注连续颜色区间的帧数。
- 双方恢复自由后保留结果，方便停止操作后仔细查看。
- 独立透明叠加层，通过原生游戏状态快照获取数据。

## 系统要求

- Windows 10 或 Windows 11（64 位）
- Steam 版 UNDER NIGHT IN-BIRTH II Sys:Celes
- 游戏使用窗口化或无边框窗口模式

此候选版支持已分析的 32 位 `uni2.exe`：

- 文件大小：**6,921,216 字节**。
- SHA-256：`4ebed985ecbf330ab8e495573361e49df20bb555263289d1aff5425fac9b7ed9`。

辅助程序会在挂钩前检查 EXE 指纹、装载映像和函数入口。不支持的 EXE 会显示错误，不安装挂钩。游戏更新可能改变原生函数或数据结构，仍需兼容适配；这次以原生更新函数的快照替换旧版的 EXE 特征定位与外部轮询采样，并不意味着不再依赖游戏版本。

## 安装与运行

1. 从 [Releases](https://github.com/geturin/UNI2FrameMeter/releases) 下载候选 ZIP，并完整解压。
2. 保持以下四个文件位于同一目录：

```text
UNI2FrameMeter.exe
frame_semantics.json
uni2-frame-meter-host.exe
uni2-frame-meter.dll
```

3. 启动游戏并进入训练模式。
4. 双击 `UNI2FrameMeter.exe`。
5. 回到游戏，帧条会显示在游戏窗口底部。

帧条只在游戏位于前台且没有最小化时显示。关闭 `UNI2 Frame Meter` 控制窗口会停止采集并退出叠加窗口；薄挂钩仍留在游戏进程中，直到游戏退出。**升级工具前请重启游戏**，避免复用已经载入的旧 DLL。

发布包已包含 Python/Tk 运行环境，无需另装 Python。32 位辅助程序负责注入 32 位游戏，帧条窗口作为独立的 64 位应用运行。

采集仅在游戏的训练战斗模式中启用；其他模式照常执行原函数，不记录帧数据。

## 如何阅读帧条

- 上行为 1P，下行为 2P。
- 每个格子代表一个游戏帧。
- 最近记录到的格子右侧有白色标记线。
- 第一层颜色连续不变时，1P 的持续帧数显示在帧条上方，2P 显示在下方。
- 双方都可以行动，且没有需要显示的有效飞行道具或双向防御辅助时，帧条停止刷新并保留当前结果。
- 短暂停顿后再次行动，实际经过的时间会显示为空白格，不会把两次行动直接连接。
- 默认连续空闲 60F 后，下一次行动会从左侧开始一段新记录。
- 帧条写满后会循环覆盖，并使用一段黑色空格区分新旧内容。

基础颜色分别表示行动受限、发生、攻击判定和收招。取消、无敌、飞行道具等附加属性会在同一格中分层显示；具体颜色可在配置文件中修改。

每格按游戏原生战斗更新的经过帧计数记录；暂停菜单与仅渲染调用不会推进帧条。原生慢动作与停帧经过的时间会保留，因此色带长度表示实际经过的游戏帧，不是剔除全部停帧后的招式固有帧数。F8 诊断记录同时保留原生回合阶段与调度字段。

可行动状态改用已核实的原生判定，移除了旧版缺少新版依据的落地与防御返回快捷规则。取消色带表示采样到的原生取消条件，不代表每个角色完整的指令输入资格。快照缺失或覆盖时会清空本段并短暂提示重置；诊断计数保留在 F8 记录中。

## 控制窗口

运行工具后会出现一个简洁的控制窗口。勾选或取消项目即可实时显示或隐藏相应属性。右侧方块在勾选时显示与帧条完全相同的颜色；未勾选或不可用时为空框。不再显示持续增长的 tick 和 sequence 数字。

`two_way_guard` 默认开启，以紫色标记双向防御辅助。例如 1P KUON 使用相关 623 招式时，标记显示在受益的 2P 帧条上；2P 即使可以自由行动也会显示，这段颜色不代表硬直。它表示对手本体攻击的左右防御方向辅助，仍需满足中段、下段等原有防御条件；独立飞行道具的方向属性另行决定。

- 修改会立即生效。
- 选择会自动保存到 `frame_semantics.json`。
- 灰色项目表示该功能尚未开放，暂时不能启用。
- `cs_cancel` 仍未完成，保持灰色不可选；帧条不据此判断当前能否使用 Chain Shift。
- 关闭控制窗口会同时关闭帧条。

### 细分状态

新增分类读取原生状态字段，不靠动作名称猜测：

| 项目 | 含义 | 默认 |
| --- | --- | --- |
| Hitstun / Guardstun | 原生受击／防御受制状态 | 开 |
| Down state | 受制期间的原生倒地标志，包含其恢复区间 | 开 |
| Captured | 被投技或其他拘束捕获 | 开 |
| Hitstop | 角色自身的原生停帧计时为正 | 关 |
| Counter-hit vulnerable | 当前原生 CH 易受标志；不表示已发生或必然发生 CH | 关 |
| Airborne / Crouching | 原生空中／蹲姿，包括定时覆盖 | 关 |
| Ground assault / Air assault | 游戏的地面／空中 Assault 动作标志 | 关 |

四种受制状态细分原来的行动受限颜色；取消勾选后回到通用行动受限颜色。其余属性作为额外色带，包括可自由行动时的姿势。Hitstop 不替换招式主色，也不从色带时长扣除停帧。最终 CH 还受攻击方招式和训练设置影响。Down state 不区分硬／软倒地；这些分类不声称判断完整 CS 资格、dash／backdash、着地恢复或受身窗口。

升级时保留原有 `frame_semantics.json`，可保留颜色、选择及帧条设置。新增内置选项会自动合并，下次修改勾选时保存；内置判定定义随程序版本更新。

## 修改配置文件

`frame_semantics.json` 位于程序同一目录。它是普通 JSON 文件，建议在工具关闭时编辑，并在修改前保留备份。

### 帧条设置

```json
"timeline": {
  "length_frames": 120,
  "idle_reset_frames": 60,
  "wrap_gap_frames": 5,
  "max_width_pixels": 1440,
  "current_frame_border_color": "#ffffff",
  "show_primary_run_counts": true,
  "primary_run_count_color": "#ffffff",
  "primary_run_count_font_size": 9
}
```

- `length_frames`：帧条包含多少个格子。
- `idle_reset_frames`：双方连续空闲多少帧后开始新记录。
- `wrap_gap_frames`：循环覆盖时用于区分新旧内容的空白格数。
- `max_width_pixels`：帧条最大宽度。
- `current_frame_border_color`：最新帧标记线颜色。
- `show_primary_run_counts`：是否显示连续区间的帧数。
- `primary_run_count_color`：帧数文字颜色。
- `primary_run_count_font_size`：帧数文字大小。

### 修改颜色和排列顺序

每种状态都在 `tokens` 中定义：

```json
"attack": {
  "order": 50,
  "color": "#f0ad38"
}
```

- `color` 使用 `#RRGGBB` 格式。
- `order` 数值越小，该颜色越靠上显示。
- 没有出现或已经隐藏的属性不会留下空层。

### 设置可选显示项目

可选项目位于 `external_attributes`：

```json
{
  "token": "full_invincible",
  "display": true,
  "status": "confirmed",
  "description": "..."
}
```

- `display` 为 `true` 时显示，为 `false` 时隐藏。
- `status` 为 `confirmed` 的项目可以修改。
- `status` 为 `incomplete` 的项目暂时不能启用。
- `description` 只是项目说明，不需要修改。

也可以直接使用控制窗口修改这些 `display` 选项。

## 常见问题

### 帧条没有出现

- 确认已经进入训练模式。
- 确认游戏位于前台且没有最小化。
- 使用窗口化或无边框窗口，不要使用独占全屏。
- 确认配置、辅助程序和 DLL 均与 `UNI2FrameMeter.exe` 位于同一目录。
- 挂钩失败时请查看错误对话框，其中会说明游戏版本不支持或发布包文件缺失等原因。

### 更新游戏后无法启动

对本次提供的更新版 EXE，旧版的战斗 tick 与角色池特征已无法匹配，角色对象结构也有变化。旧 GUI 在创建窗口前抛出启动异常，因此表现为闪退。旧版只是记录 SHA-256 供诊断，并不是因指纹不符而拒绝启动。

此候选版以经过检查的原生挂钩配置替代旧扫描，并可见地报告失败；涉及原生函数或结构的更新仍需适配。反馈问题时请附上完整错误信息和 EXE SHA-256。错误日志保存于 `%LOCALAPPDATA%\UNI2FrameMeter\logs`，对话框会显示实际日志路径。

### Windows 显示安全警告

未签名的个人发布程序可能触发 SmartScreen。请只从本项目的正式发布页下载，并自行核对发布页提供的 SHA-256。

## 从源码构建

先使用 Python 3 与 i686 MinGW-w64 C/C++ 编译器构建 32 位辅助程序和 DLL，例如在 Linux 上执行：

```bash
python3 build_native.py --cc i686-w64-mingw32-gcc-posix --cxx i686-w64-mingw32-g++-posix
```

然后在 Windows 使用 64 位 Python 3.12。将生成的两个原生文件保留在 `build/native`，安装 PyInstaller 后打包：

```powershell
python -m pip install PyInstaller==6.16.0
./build_release.ps1
```

ZIP 输出到 `release`。仓库的 [发布工作流](.github/workflows/release.yml) 分别执行原生编译与 Windows 打包；构建发布包无需安装游戏。

## 安全与免责声明

此版本**注入 DLL，并在游戏运行内存中安装 detour 跳转**。磁盘上的 EXE 和游戏资源文件不修改；采集游戏状态用于显示，原生战斗函数仍照常执行。建议仅在训练模式使用，不保证与反作弊系统或联机对战兼容。

上一 hook 候选版已经用户在训练模式确认正常工作。新增分类根据受支持 EXE 的原生字段实现；开发检查使用自建数据，不启动游戏。请在训练模式确认新增色带，并反馈错误或中断的显示。

本项目是非官方社区工具，与 FRENCH-BREAD、Arc System Works 或其他权利方无关联。《UNDER NIGHT IN-BIRTH》及相关名称归其各自权利方所有。

项目采用 [MIT 许可证](LICENSE)，版权归 geturin。MinHook 及其附带的反汇编器采用 [BSD 2-Clause 许可证](vendor/minhook/LICENSE.txt)，发布包随附相应声明，不包含游戏代码或素材。
