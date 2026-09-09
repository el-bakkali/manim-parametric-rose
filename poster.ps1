<#
    Builds poster.jpg: renders a still of the scene, then typesets the maths over it.

    MathTex shells out to LaTeX, so MiKTeX must be installed (see README).
#>
[CmdletBinding()]
param(
    [int] $RoseU = 16,
    [int] $RoseV = 220
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# A freshly installed MiKTeX is not on PATH in an already-open shell.
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'Machine')

$env:ROSE_U = $RoseU
$env:ROSE_V = $RoseV
try {
    uv run manim -s -r 1080,1920 --media_dir media -o poster-src enchanted.py EnchantedRose
    if ($LASTEXITCODE -ne 0) { throw "scene render failed with exit code $LASTEXITCODE" }
}
finally {
    Remove-Item Env:ROSE_U, Env:ROSE_V -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Force -Path docs | Out-Null
Copy-Item media\images\enchanted\poster-src.png docs\poster-src.png -Force

uv run manim -s -r 1080,1920 --media_dir media -o poster poster.py Poster
if ($LASTEXITCODE -ne 0) { throw "poster render failed with exit code $LASTEXITCODE" }

ffmpeg -v error -y -i media\images\poster\poster.png -q:v 2 poster.jpg
if ($LASTEXITCODE -ne 0) { throw "jpeg encode failed with exit code $LASTEXITCODE" }

$sizeKb = [math]::Round((Get-Item poster.jpg).Length / 1KB, 1)
Write-Host "`nPoster ready: poster.jpg ($sizeKb KB)" -ForegroundColor Green
