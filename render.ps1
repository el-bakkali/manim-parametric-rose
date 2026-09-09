<#
    Renders the enchanted rose and encodes it to a widely compatible MP4.

    A silent AAC track is injected because many video platforms reject audioless files.
#>
[CmdletBinding()]
param(
    [double] $Duration = 8,
    [int]    $Fps = 30,
    [int]    $RoseU = 16,
    [int]    $RoseV = 220,
    [string] $OutFile = "$PSScriptRoot\rose.mp4"
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# Cairo, not OpenGL: the OpenGL renderer has no depth sorting, so the bloom goes see-through.
$env:ROSE_DURATION = $Duration
$env:ROSE_U = $RoseU
$env:ROSE_V = $RoseV
try {
    uv run manim --write_to_movie --disable_caching `
        -r 1080,1920 --fps $Fps --media_dir media -o rose `
        enchanted.py EnchantedRose
    if ($LASTEXITCODE -ne 0) { throw "manim render failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item Env:ROSE_DURATION, Env:ROSE_U, Env:ROSE_V -ErrorAction SilentlyContinue
}

$rendered = Join-Path $PSScriptRoot "media\videos\enchanted\1920p$Fps\rose.mp4"
if (-not (Test-Path $rendered)) { throw "Expected render not found at $rendered" }

ffmpeg -v error -y -i $rendered `
    -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 `
    -map 0:v:0 -map 1:a:0 -shortest `
    -c:v libx264 -profile:v high -level 4.0 -pix_fmt yuv420p `
    -crf 18 -maxrate 10M -bufsize 15M `
    -x264-params "keyint=$($Fps * 2):min-keyint=$($Fps):scenecut=40" `
    -c:a aac -b:a 128k -ar 44100 -ac 2 `
    -movflags +faststart `
    $OutFile
if ($LASTEXITCODE -ne 0) { throw "ffmpeg encode failed with exit code $LASTEXITCODE" }

$sizeMb = [math]::Round((Get-Item $OutFile).Length / 1MB, 2)
Write-Host "`nVideo ready: $OutFile ($sizeMb MB)" -ForegroundColor Green
