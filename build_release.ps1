param(
    [string]$Version = "v0.6.0"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $projectRoot "release"
$packageName = "UNI2FrameMeter-$Version"
$packageDir = Join-Path $releaseRoot $packageName
$workDir = Join-Path $projectRoot "build"
$specDir = Join-Path $workDir "spec"
$pyInstallerDist = Join-Path $workDir "pyinstaller-dist"
$nativeDir = Join-Path $workDir "native"
$overlaySource = Get-Content -Raw -LiteralPath (Join-Path $projectRoot "src\uni2_overlay.py")
if ($overlaySource -notmatch ('BUILD_ID\s*=\s*"' + [regex]::Escape($Version) + '"')) {
    throw "Release version does not match the overlay BUILD_ID: $Version"
}

foreach ($name in @("uni2-frame-meter.dll", "uni2-frame-meter-host.exe")) {
    if (!(Test-Path -LiteralPath (Join-Path $nativeDir $name))) {
        throw "Missing build/native/$name. Run build_native.py with the 32-bit MinGW compiler first."
    }
}

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "UNI2FrameMeter" `
    --add-data "$(Join-Path $projectRoot 'frame_semantics.json');." `
    --workpath (Join-Path $workDir "pyinstaller") `
    --specpath $specDir `
    --distpath $pyInstallerDist `
    (Join-Path $projectRoot "src\uni2_overlay.py")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed: $LASTEXITCODE" }

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -Recurse -Force -LiteralPath $packageDir
}
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
Copy-Item -Force -LiteralPath (Join-Path $pyInstallerDist "UNI2FrameMeter.exe") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "frame_semantics.json") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.md") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.zh-CN.md") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.ja.md") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "LICENSE") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "vendor/minhook/LICENSE.txt") -Destination (Join-Path $packageDir "MinHook-LICENSE.txt")
Copy-Item -Force -LiteralPath (Join-Path $nativeDir "uni2-frame-meter.dll") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $nativeDir "uni2-frame-meter-host.exe") -Destination $packageDir
Get-ChildItem -LiteralPath (Join-Path $projectRoot "licenses") -Filter "*-LICENSE.txt" -File | ForEach-Object {
    Copy-Item -Force -LiteralPath $_.FullName -Destination $packageDir
}

$receipt = [ordered]@{}
Get-ChildItem -LiteralPath $packageDir -File | Sort-Object Name | ForEach-Object {
    $receipt[$_.Name] = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
}
$receipt | ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $packageDir "SHA256.json")

$zipPath = Join-Path $releaseRoot "$packageName-win-x64.zip"
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -Force -LiteralPath $zipPath
}
Compress-Archive -Path (Join-Path $packageDir "*") -DestinationPath $zipPath
$zipHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
"$zipHash  $([IO.Path]::GetFileName($zipPath))" | Set-Content -Encoding ASCII -LiteralPath (Join-Path $releaseRoot "SHA256SUMS.txt")

Write-Output "Release directory: $packageDir"
Write-Output "Release archive:   $zipPath"
