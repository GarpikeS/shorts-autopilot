param(
    [string]$Destination = (Join-Path $HOME ".codex\skills")
)

$ErrorActionPreference = "Stop"
$source = Join-Path (Split-Path $PSScriptRoot -Parent) "skills"
New-Item -ItemType Directory -Path $Destination -Force | Out-Null

Get-ChildItem -LiteralPath $source -Directory | ForEach-Object {
    $target = Join-Path $Destination $_.Name
    if (Test-Path -LiteralPath $target) {
        throw "Skill already exists: $target"
    }
    Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse
    Write-Output "Installed $($_.Name) to $target"
}
