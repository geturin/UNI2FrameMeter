# UNI2 Frame Meter

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

A frame timeline for the Training Mode of UNDER NIGHT IN-BIRTH II Sys:Celes. It displays both players' frame-by-frame action states at the bottom of the game window, making startup, active frames, recovery, frame advantage, invincibility, and cancel windows easier to understand.

**0.6.0 is the stable native-hook release.** A 32-bit helper loads the Frame Meter DLL into the game. The DLL observes the original battle update function and sends complete per-tick snapshots to the separate overlay through shared memory. The original game functions continue to run; no battle simulation or game-script patch is required. The native-hook build has been confirmed working in the user's Training Mode use and accepted for this release.

## Demonstration video

[Watch on YouTube](https://youtu.be/O8JgjDnPLmE)

This video demonstrates the older 0.5 overlay; the current interface and available states have changed.

## Main features

- Two-row timeline: P1 on top and P2 on the bottom.
- Displays startup, attack judgment, recovery, and periods when action is restricted.
- Optional display of cancel properties, invincibility properties, two-way guard assistance, and active projectiles.
- Multiple properties on the same frame are shown as layered colors.
- Automatically labels the length of continuous color sections.
- Preserves the result after both players become free so it can be inspected afterward.
- Uses a separate transparent overlay, fed by native game-state snapshots.

## Requirements

- Windows 10 or Windows 11 (64-bit)
- Steam version of UNDER NIGHT IN-BIRTH II Sys:Celes
- Windowed or borderless display mode

This release supports the inspected 32-bit `uni2.exe` only:

- File size: **6,921,216 bytes**.
- SHA-256: `4ebed985ecbf330ab8e495573361e49df20bb555263289d1aff5425fac9b7ed9`.

The helper checks the EXE identity, loaded-image layout, and hook entry before attaching. An unsupported EXE produces a visible error without installing a hook. Game updates can change native functions or data structures and may require a compatibility update. This replaces EXE-signature discovery and external polling with snapshots from the native update function; it does not make the tool independent of game versions.

## Installation and use

1. Download the Windows ZIP from the [latest release](https://github.com/geturin/UNI2FrameMeter/releases/latest) and extract it completely.
2. Keep these four files in the same folder:

```text
UNI2FrameMeter.exe
frame_semantics.json
uni2-frame-meter-host.exe
uni2-frame-meter.dll
```

3. Start the game and enter Training Mode.
4. Double-click `UNI2FrameMeter.exe`.
5. Return to the game. The timeline appears at the bottom of the game window.

The timeline is visible only while the game is foreground and not minimized. Close the `UNI2 Frame Meter` control window to stop capture and exit the overlay. A thin hook remains loaded in the game until the game exits. **Restart the game before upgrading the tool** so that a previous DLL is not reused.

The packaged overlay contains its Python/Tk runtime; installing Python separately is unnecessary. The 32-bit helper handles attachment to the 32-bit game, while the overlay runs as a separate 64-bit application.

Capture is limited to the game's training battle modes. Other modes continue through the original function without recording frame data.

## Reading the timeline

- The upper row is P1 and the lower row is P2.
- Every cell represents one game frame.
- A white line on the right edge marks the latest recorded cell.
- When the first color remains unchanged, its duration is shown above P1 and below P2.
- The timeline freezes and preserves the result when both players can act and neither active projectiles nor two-way guard assistance need to be displayed.
- If action resumes after a short pause, the elapsed time appears as black cells instead of joining the two actions directly.
- By default, after 60 consecutive idle frames, the next action begins a new sequence from the left.
- When the timeline fills, it wraps and uses a black gap to separate new and old content.

Cells follow the game's original elapsed battle-update counter. Paused menus and render-only calls do not advance the meter. Native slowdown and freeze intervals are included, so the displayed durations are elapsed game frames, not move-data durations with all freezes removed. Raw phase and scheduler values are retained in F8 diagnostic captures.

The base colors represent restricted action, startup, attack judgment, and recovery. Extra properties such as cancel, invincibility, and projectile state are layered in the same cell. Their colors can be changed in the config file.

The native actionable predicate replaces the older landing and guard-return shortcuts. Cancel bands describe the sampled native cancel predicates, not every character's complete command eligibility. Missing or overwritten snapshots reset the timeline and briefly show a reset message; diagnostic counters remain in F8 captures.

## Control window

A small control window opens with the tool. Check or uncheck an item to show or hide that property immediately. The square on its right shows the exact timeline color when enabled; unchecked or unavailable items have an empty square. Running tick and sequence numbers are no longer shown.

`two_way_guard` is enabled by default and marks horizontal guard-direction assistance in purple. For example, when P1 Kuon uses a relevant 623 move, the band appears on the benefiting P2 row, including while P2 can act freely; it does not indicate recovery. It applies to the opposing main character's attacks. Overhead, low, and other guard requirements still apply, and independent projectiles use their own direction properties.

- Changes take effect immediately.
- Choices are saved automatically to `frame_semantics.json`.
- Gray items are not currently available and cannot be enabled.
- `cs_cancel` remains incomplete and disabled; the display does not imply that Chain Shift is available.
- Closing the control window also closes the timeline.

### Detailed states

The new categories read native state flags, not action-name guesses:

| Display item | Meaning | Default |
| --- | --- | --- |
| Hitstun / Guardstun | Native hit or guard restraint | On |
| Down state | Native down flag during restraint, including its recovery interval | On |
| Captured | Restrained by a capture/throw | On |
| Hitstop | Positive native per-character hitstop timer | Off |
| Counter-hit vulnerable | Native vulnerability flag; not a Counter Hit result or guarantee | Off |
| Airborne / Crouching | Current native posture, including timed overrides | Off |
| Ground assault / Air assault | The game's corresponding action markers | Off |

Detailed restraint colors replace the generic action-restricted color. Turning one off restores that generic color. Other enabled properties appear as additional bands, including posture while freely actionable. Hitstop remains an extra band: it does not remove freeze frames from move durations. Counter Hit also depends on the attacking move and training settings. Down state does not distinguish hard and soft knockdowns. Full Chain Shift eligibility, dash/backdash, landing recovery, and tech-window eligibility are not claimed by these categories.

Keep your existing `frame_semantics.json` when upgrading to retain colors, choices, and timeline settings. New built-in options are merged automatically and saved on the next display change. Built-in predicate definitions follow the application version.

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
- Make sure the config, helper, and DLL are beside `UNI2FrameMeter.exe`.
- Read the error dialog if attachment fails; it identifies an unsupported game build or missing package files.

### The tool stops working after a game update

With the supplied updated EXE, the old battle-tick and entity-pool signatures no longer matched, and the character-object layout changed. The old GUI raised a startup exception before opening its window, so it appeared to crash. Its SHA-256 was recorded for diagnostics, not used to reject the build.

This version replaces that scan with a checked native-hook profile and displays failures instead of silently closing. It still requires a compatible profile after relevant game updates. Include the complete error message and EXE SHA-256 when reporting a problem. Error logs are saved under `%LOCALAPPDATA%\UNI2FrameMeter\logs`; the dialog shows the actual log path.

### Windows shows a security warning

Unsigned personal releases may trigger SmartScreen. Download only from this project's official release page and compare the file SHA-256 with the value published there.

## Building from source

First build the 32-bit helper and DLL with Python 3 and the i686 MinGW-w64 C/C++ compilers, for example on Linux:

```bash
python3 build_native.py --cc i686-w64-mingw32-gcc-posix --cxx i686-w64-mingw32-g++-posix
```

Then use 64-bit Python 3.12 on Windows. Keep the two generated native files in `build/native`, install PyInstaller, and package the overlay:

```powershell
python -m pip install PyInstaller==6.16.0
./build_release.ps1
```

The ZIP is written to `release`. The [release workflow](.github/workflows/release.yml) performs the native build and Windows packaging in separate jobs; no game installation is needed for packaging.

## Safety and disclaimer

This version **injects a DLL and installs detours in the game's running memory**. It leaves the EXE and game resource files on disk unchanged and reads game state for display while the original battle functions execute normally. Use in Training Mode is recommended. Compatibility with anti-cheat systems or online play is not guaranteed.

The user reported normal operation in Training Mode and accepted this version for stable release. This does not establish exhaustive accuracy for every character or move. State categories are based on the supported EXE's native fields; development checks use owned fixtures and do not launch the game. Report incorrect or interrupted displays with the game EXE's SHA-256.

This is an unofficial community project and is not affiliated with FRENCH-BREAD, Arc System Works, or any other rights holder. UNDER NIGHT IN-BIRTH and related names belong to their respective owners.

The project is distributed under the [MIT License](LICENSE), copyright geturin. MinHook and its bundled disassembler use the [BSD 2-Clause License](vendor/minhook/LICENSE.txt); their notices are included in the release package. Game code and assets are not included.
