<#
.SYNOPSIS
  크래프트 앱 6종(VectorCraft·PhotoCraft·EffectCraft·DesignCraft·FilmCraft·SoundCraft)을
  윈도우에 portable로 설치하고, 이 저장소의 .mcp.json을 생성한다.

.DESCRIPTION
  - GitHub 릴리스(storytold/<app>)에서 최신 windows-<arch>-portable.zip을 받아
    %LOCALAPPDATA%\ArtCraft\<app>\ 에 푼다 (관리자 권한 불필요). zip 안에 <app>-cli.exe가 같이 있다.
  - 이미 C:\Program Files\<App>\<app>-cli.exe (MSI 설치) 또는 portable 폴더가 있으면 그걸 쓴다.
  - .mcp.json은 headless 모드 + 파일 접근을 이 저장소 폴더로 제한 (filmcraft는 옵션이 없어 제한 없음).

.EXAMPLE
  Set-ExecutionPolicy -Scope Process Bypass
  .\setup\windows\install-craft.ps1
  .\setup\windows\install-craft.ps1 -Only vectorcraft,photocraft   # 일부만
  .\setup\windows\install-craft.ps1 -Force                         # 받아 둔 것도 다시 설치
  .\setup\windows\install-craft.ps1 -McpOnly                       # 설치 건너뛰고 .mcp.json만 다시 생성
#>
param(
  [string[]]$Only = @("vectorcraft", "photocraft", "effectcraft", "designcraft", "filmcraft", "soundcraft"),
  [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "ArtCraft"),
  [switch]$Force,
  [switch]$McpOnly
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DisplayName = @{
  vectorcraft = "VectorCraft"; photocraft = "PhotoCraft"; effectcraft = "EffectCraft"
  designcraft = "DesignCraft"; filmcraft = "FilmCraft"; soundcraft = "SoundCraft"
}
$arch = switch ($env:PROCESSOR_ARCHITECTURE) {
  "ARM64" { "arm64" }
  "AMD64" { "x64" }
  default { "x86" }
}
Write-Host "저장소: $RepoRoot"
Write-Host "아키텍처: $arch · 설치 폴더: $InstallRoot"

function Find-Cli([string]$app) {
  $candidates = @(
    (Join-Path $InstallRoot "$app\$app-cli.exe"),
    (Join-Path $env:ProgramFiles "$($DisplayName[$app])\$app-cli.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\$($DisplayName[$app])\$app-cli.exe")
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  return $null
}

function Install-App([string]$app) {
  $existing = Find-Cli $app
  if ($existing -and -not $Force) {
    Write-Host "  [$app] 이미 있음: $existing" -ForegroundColor DarkGray
    return $existing
  }
  $rel = Invoke-RestMethod "https://api.github.com/repos/storytold/$app/releases/latest" -Headers @{ "User-Agent" = "claude-harness-setup" }
  $asset = $rel.assets | Where-Object { $_.name -like "*-windows-$arch-portable.zip" } | Select-Object -First 1
  if (-not $asset) { throw "[$app] $($rel.tag_name) 릴리스에 windows-$arch-portable.zip 이 없음" }

  $dest = Join-Path $InstallRoot $app
  $tmpZip = Join-Path $env:TEMP $asset.name
  Write-Host "  [$app] $($rel.tag_name) 다운로드 ($([math]::Round($asset.size / 1MB)) MB)…"
  Invoke-WebRequest $asset.browser_download_url -OutFile $tmpZip -UseBasicParsing

  $tmpDir = Join-Path $env:TEMP "$app-extract"
  if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
  Expand-Archive $tmpZip -DestinationPath $tmpDir -Force
  # zip 안에 '<app>-<ver>-windows-<arch>-portable\' 한 겹이 있으면 벗긴다
  $inner = Get-ChildItem $tmpDir -Directory | Select-Object -First 1
  $src = if ($inner -and (Test-Path (Join-Path $inner.FullName "$app-cli.exe"))) { $inner.FullName } else { $tmpDir }
  if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item (Join-Path $src "*") $dest -Recurse -Force
  Remove-Item $tmpZip, $tmpDir -Recurse -Force -ErrorAction SilentlyContinue

  $cli = Join-Path $dest "$app-cli.exe"
  if (-not (Test-Path $cli)) { throw "[$app] 압축 해제 후 $app-cli.exe 가 없음 — zip 구성이 바뀌었는지 확인" }
  Write-Host "  [$app] 설치 완료: $cli" -ForegroundColor Green
  return $cli
}

# 1) 설치
$clis = @{}
foreach ($app in $Only) {
  if (-not $DisplayName.ContainsKey($app)) { Write-Warning "모르는 앱: $app"; continue }
  try {
    $clis[$app] = if ($McpOnly) { Find-Cli $app } else { Install-App $app }
    if (-not $clis[$app]) { Write-Warning "[$app] CLI를 못 찾음 — -McpOnly 없이 다시 실행" }
  } catch {
    Write-Warning "[$app] 실패: $($_.Exception.Message)"
  }
}

# 2) .mcp.json 생성 (JSON 안에서는 경로를 / 로 — 이스케이프 문제 없음)
$rootSlash = $RepoRoot -replace "\\", "/"
$servers = [ordered]@{}
foreach ($app in $Only) {
  $cli = $clis[$app]
  if (-not $cli) { continue }
  $cliSlash = $cli -replace "\\", "/"
  $args = @("mcp")
  if ($app -ne "filmcraft") {
    $args += @("--automation-read-root", $rootSlash, "--automation-write-root", $rootSlash)
  }
  $servers[$app] = [ordered]@{ type = "stdio"; command = $cliSlash; args = $args; env = @{} }
}
$mcp = [ordered]@{ mcpServers = $servers }
$mcpPath = Join-Path $RepoRoot ".mcp.json"
# PS 5.1의 Set-Content -Encoding UTF8 은 BOM을 붙여 JSON 파서가 깨짐 → BOM 없이 쓴다
[IO.File]::WriteAllText($mcpPath, ($mcp | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding $false))
Write-Host ""
Write-Host ".mcp.json 생성: $mcpPath ($($servers.Count)개 서버)" -ForegroundColor Green

# 3) 크래프트 작업 폴더
foreach ($d in @("vector", "photo", "effect", "design", "film", "sound", "out")) {
  New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "craft\$d") | Out-Null
}

# 4) 신원 + 공유 메모리 링크 (python 있을 때만, 없으면 안내)
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  Write-Host ""
  Write-Host "신원 설정 + 메모리 링크 (setup\common\link_memory.py):"
  & $py.Source (Join-Path $RepoRoot "setup\common\link_memory.py")
} else {
  Write-Warning "python 이 없음 → https://www.python.org/downloads/ 설치('Add python.exe to PATH' 체크) 후  python setup\common\link_memory.py  실행 (커밋 신원 + 공유 메모리 링크)"
}

Write-Host ""
Write-Host "다음 단계:"
Write-Host "  1. 이 폴더에서 claude 를 (다시) 실행하면 MCP 서버 승인 창이 뜸 → 전부 허용"
Write-Host "  2. 세션 시작 훅이 [하네스] 블록을 찍음 → '메모리: … 연결됨' 확인. /mcp 입력 → 6종이 connected 인지 확인"
Write-Host "  3. 안 되는 게 있으면 .claude\STATE.md '환경 준비'에 증상 적어 두기"
