# UNI2 Frame Meter

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

A frame timeline for the Training Mode of UNDER NIGHT IN-BIRTH II Sys:Celes. It displays both players' frame-by-frame action states at the bottom of the game window, making startup, active frames, recovery, frame advantage, invincibility, and cancel windows easier to understand.

## Demonstration video

[Watch on YouTube](https://youtu.be/O8JgjDnPLmE)

## Main features

- Two-row timeline: P1 on top and P2 on the bottom.
- Displays startup, attack judgment, recovery, and periods when action is restricted.
- Optional display of cancel properties, invincibility properties, and active projectiles.
- Multiple properties on the same frame are shown as layered colors.
- Automatically labels the length of continuous color sections.
- Preserves the result after both players become free so it can be inspected afterward.
- Uses a separate transparent overlay and does not modify game files or game memory.

## Requirements

- Windows 10 or Windows 11
- Steam version of UNDER NIGHT IN-BIRTH II Sys:Celes
- Windowed or borderless display mode

The tool is not locked to a specific game version. New characters, balance changes, and move-data updates normally require no tool update. If an incompatible engine change occurs, the program stops with an error instead of continuing with invalid data.

## Installation and use

1. Download and extract the release package.
2. Keep these two files in the same folder:

```text
UNI2FrameMeter.exe
frame_semantics.json
```

3. Start the game and enter Training Mode.
4. Double-click `UNI2FrameMeter.exe`.
5. Return to the game. The timeline appears at the bottom of the game window.

The timeline is visible only while the game is foreground and not minimized. Close the `UNI2 Frame Display` control window to exit the tool.

## Reading the timeline

- The upper row is P1 and the lower row is P2.
- Every cell represents one game frame.
- A white line on the right edge marks the latest recorded cell.
- When the first color remains unchanged, its duration is shown above P1 and below P2.
- The timeline freezes and preserves the result when both players can act and no active projectile remains.
- If action resumes after a short pause, the elapsed time appears as black cells instead of joining the two actions directly.
- By default, after 60 consecutive idle frames, the next action begins a new sequence from the left.
- When the timeline fills, it wraps and uses a black gap to separate new and old content.

The base colors represent restricted action, startup, attack judgment, and recovery. Extra properties such as cancel, invincibility, and projectile state are layered in the same cell. Their colors can be changed in the config file.

## Control window

A small control window opens with the tool. Check or uncheck an item to show or hide that property immediately.

- Changes take effect immediately.
- Choices are saved automatically to `frame_semantics.json`.
- Gray items are not currently available and cannot be enabled.
- Closing the control window also closes the timeline.

## Editing the config file

`frame_semantics.json` is located beside the program. It is a standard JSON file. Edit it while the tool is closed and keep a backup before making changes.

### Timeline settings

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

- `length_frames`: number of cells in the timeline.
- `idle_reset_frames`: idle frames before the next action begins a new sequence.
- `wrap_gap_frames`: black cells separating new and old content after wrapping.
- `max_width_pixels`: maximum timeline width.
- `current_frame_border_color`: color of the latest-frame marker.
- `show_primary_run_counts`: enables continuous-section frame counts.
- `primary_run_count_color`: color of the count text.
- `primary_run_count_font_size`: size of the count text.

### Changing colors and order

Each state is defined under `tokens`:

```json
"attack": {
  "order": 50,
  "color": "#f0ad38"
}
```

- `color` uses the `#RRGGBB` format.
- A lower `order` value places the color higher in the cell.
- Properties that are absent or hidden do not leave empty layers.

### Optional display items

Optional items are listed under `external_attributes`:

```json
{
  "token": "full_invincible",
  "display": true,
  "status": "confirmed",
  "description": "..."
}
```

- Set `display` to `true` to show the item or `false` to hide it.
- Items with `status` set to `confirmed` can be changed.
- Items with `status` set to `incomplete` cannot currently be enabled.
- `description` is informational and does not need to be changed.

The control window can also change these `display` options directly.

## Troubleshooting

### The timeline does not appear

- Make sure Training Mode is open.
- Make sure the game is foreground and not minimized.
- Use windowed or borderless mode instead of exclusive fullscreen.
- Make sure `frame_semantics.json` is beside the EXE.

### The tool stops working after a game update

Normal character and balance updates should not cause a problem. If the tool reports that it cannot recognize the current game structure, wait for a compatibility update and include the game version and complete error message in your report.

### Windows shows a security warning

Unsigned personal releases may trigger SmartScreen. Download only from this project's official release page and compare the file SHA-256 with the value published there.

## Safety and disclaimer

This is an external, read-only overlay. It does not inject a DLL or modify game files or game memory. Use in Training Mode is recommended.

This is an unofficial community project and is not affiliated with FRENCH-BREAD, Arc System Works, or any other rights holder. UNDER NIGHT IN-BIRTH and related names belong to their respective owners.
