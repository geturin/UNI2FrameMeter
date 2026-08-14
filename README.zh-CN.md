# UNI2 Frame Meter

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

一个用于《UNDER NIGHT IN-BIRTH II Sys:Celes》训练模式的帧条显示工具。它会在游戏画面底部显示双方每一帧的行动状态，帮助玩家直观查看招式的发生、攻击判定、收招、硬直差、无敌和取消窗口。

## 示范视频

[在哔哩哔哩观看](https://www.bilibili.com/video/BV13ugM6vE3d/)

## 主要功能

- 双行帧条：上方为 1P，下方为 2P。
- 显示发生、攻击判定、收招和行动受限时间。
- 可选显示取消属性、无敌属性和场上有效飞行道具。
- 同一帧存在多个属性时，以多层颜色同时显示。
- 自动标注连续颜色区间的帧数。
- 双方恢复自由后保留结果，方便停止操作后仔细查看。
- 独立透明叠加层，不修改游戏文件，不写入游戏内存。

## 系统要求

- Windows 10 或 Windows 11
- Steam 版 UNDER NIGHT IN-BIRTH II Sys:Celes
- 游戏使用窗口化或无边框窗口模式

程序不绑定特定游戏版本。新增角色、平衡调整和招式数据更新通常无需更新本工具。如果游戏引擎发生不兼容改动，程序会停止并显示错误，而不会继续读取错误数据。

## 安装与运行

1. 下载并解压发布包。
2. 保持以下两个文件位于同一目录：

```text
UNI2FrameMeter.exe
frame_semantics.json
```

3. 启动游戏并进入训练模式。
4. 双击 `UNI2FrameMeter.exe`。
5. 回到游戏，帧条会显示在游戏窗口底部。

帧条只在游戏位于前台且没有最小化时显示。关闭 `UNI2 Frame Display` 控制窗口即可退出工具。

## 如何阅读帧条

- 上行为 1P，下行为 2P。
- 每个格子代表一个游戏帧。
- 最近记录到的格子右侧有白色标记线。
- 第一层颜色连续不变时，1P 的持续帧数显示在帧条上方，2P 显示在下方。
- 双方都可以行动且场上没有有效飞行道具时，帧条停止刷新并保留当前结果。
- 短暂停顿后再次行动，实际经过的时间会显示为空白格，不会把两次行动直接连接。
- 默认连续空闲 60F 后，下一次行动会从左侧开始一段新记录。
- 帧条写满后会循环覆盖，并使用一段黑色空格区分新旧内容。

基础颜色分别表示行动受限、发生、攻击判定和收招。取消、无敌、飞行道具等附加属性会在同一格中分层显示；具体颜色可在配置文件中修改。

## 控制窗口

运行工具后会出现一个简洁的控制窗口。勾选或取消项目即可实时显示或隐藏相应属性。

- 修改会立即生效。
- 选择会自动保存到 `frame_semantics.json`。
- 灰色项目表示该功能尚未开放，暂时不能启用。
- 关闭控制窗口会同时关闭帧条。

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
- 确认 `frame_semantics.json` 与 EXE 位于同一目录。

### 更新游戏后无法启动

一般的角色和平衡更新不会造成影响。如果程序提示无法识别当前游戏结构，请等待兼容更新，并在反馈时附上游戏版本号和完整错误信息。

### Windows 显示安全警告

未签名的个人发布程序可能触发 SmartScreen。请只从本项目的正式发布页下载，并自行核对发布页提供的 SHA-256。

## 安全与免责声明

本工具是外部只读叠加程序，不注入 DLL，不修改游戏文件或游戏内存。建议仅在训练模式中使用。

本项目是非官方社区工具，与 FRENCH-BREAD、Arc System Works 或其他权利方无关联。《UNDER NIGHT IN-BIRTH》及相关名称归其各自权利方所有。
