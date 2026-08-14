param(
    [string]$Version = "v0.5"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$releaseRoot = Join-Path $projectRoot "release"
$packageName = "UNI2FrameMeter-$Version"
$packageDir = Join-Path $releaseRoot $packageName
$workDir = Join-Path $projectRoot "build"
$specDir = Join-Path $workDir "spec"
$pyInstallerDist = Join-Path $workDir "pyinstaller-dist"

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --console `
    --name "UNI2FrameMeter" `
    --workpath (Join-Path $workDir "pyinstaller") `
    --specpath $specDir `
    --distpath $pyInstallerDist `
    (Join-Path $projectRoot "src\uni2_overlay.py")

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -Recurse -Force -LiteralPath $packageDir
}
New-Item -ItemType Directory -Force -Path $packageDir | Out-Null
Copy-Item -Force -LiteralPath (Join-Path $pyInstallerDist "UNI2FrameMeter.exe") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "frame_semantics.json") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.md") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.zh-CN.md") -Destination $packageDir
Copy-Item -Force -LiteralPath (Join-Path $projectRoot "README.ja.md") -Destination $packageDir

$zipPath = Join-Path $releaseRoot "$packageName-win-x64.zip"
if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -Force -LiteralPath $zipPath
}
Compress-Archive -Path (Join-Path $packageDir "*") -DestinationPath $zipPath

Write-Output "Release directory: $packageDir"
Write-Output "Release archive:   $zipPath"
