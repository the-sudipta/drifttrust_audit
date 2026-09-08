param([Parameter(Mandatory=$true)][string]$Archive)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$stageRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.local/site-stage'))
$archivePath = [IO.Path]::GetFullPath((Join-Path $projectRoot $Archive))
if (-not $stageRoot.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Invalid staging path' }
if (-not $archivePath.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar)) { throw 'Archive must be in project' }
New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null
# Native Windows equivalent of package-site.sh, using its exact validation/staging helper.
$helper = 'C:/Users/User/.codex/plugins/cache/openai-bundled/sites/0.1.57/skills/sites-hosting/scripts/prepare-site-build.cjs'
if (-not (Test-Path -LiteralPath $helper)) { throw 'Sites prepare-site-build.cjs is unavailable' }
node $helper $projectRoot (Join-Path $stageRoot 'dist')
if ($LASTEXITCODE -ne 0) { throw 'Build staging failed' }
New-Item -ItemType Directory -Force -Path (Split-Path $archivePath) | Out-Null
tar -C $stageRoot -czf $archivePath dist
if ($LASTEXITCODE -ne 0) { throw 'Archive creation failed' }
$entries = tar -tzf $archivePath
if ($LASTEXITCODE -ne 0 -or -not ($entries -contains 'dist/.openai/hosting.json')) { throw 'Invalid archive' }
Write-Output $archivePath
