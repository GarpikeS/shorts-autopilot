param(
    [Parameter(Mandatory = $true)]
    [string]$ProfilePath,
    [int]$Port = 9223,
    [string]$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ChromePath)) {
    throw "Chrome not found: $ChromePath"
}

$resolvedProfile = [System.IO.Path]::GetFullPath($ProfilePath)
New-Item -ItemType Directory -Path $resolvedProfile -Force | Out-Null
$userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
$arguments = @(
    "--headless=new"
    "--mute-audio"
    "--disable-blink-features=AutomationControlled"
    "--remote-debugging-port=$Port"
    "--user-data-dir=$resolvedProfile"
    "--no-first-run"
    "--no-default-browser-check"
    "--disable-features=InfiniteSessionRestore"
    "--user-agent=`"$userAgent`""
    "about:blank"
)

$process = Start-Process -FilePath $ChromePath -ArgumentList $arguments -PassThru -WindowStyle Hidden
$deadline = (Get-Date).AddSeconds(20)
do {
    Start-Sleep -Milliseconds 500
    try {
        $status = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$Port/json/version" -TimeoutSec 2).StatusCode
    } catch {
        $status = $null
    }
} until ($status -eq 200 -or (Get-Date) -ge $deadline)

if ($status -ne 200) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    throw "Chrome CDP did not become ready on port $Port"
}

Write-Output "ROOT_PID=$($process.Id)"
Write-Output "CDP_URL=http://127.0.0.1:$Port"
