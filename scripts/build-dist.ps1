#requires -Version 7
<#
.SYNOPSIS
  Rebuild dist/*.zip from the working tree, or verify they match it (-Check).
.DESCRIPTION
  Entry order is fixed, timestamps are fixed (1980-01-01), and CRLF is normalized to LF so the
  archive does not depend on core.autocrlf. Only tracked files are bundled; content is read from
  the working tree. -Check compares entry names (in order) and uncompressed bytes, not zip bytes,
  because the deflate stream can differ between .NET/zlib versions.
#>
[CmdletBinding()]
param([switch]$Check)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$skillDir = 'skills/asd-ste100-zh-tw'
$stamp = [DateTimeOffset]::new(1980, 1, 1, 0, 0, 0, [TimeSpan]::Zero)

$tracked = @(git -C $root ls-files)
if ($LASTEXITCODE -ne 0 -or $tracked.Count -eq 0) { throw 'git ls-files failed' }

# Ordinal, case-insensitive order: agents/, LICENSE, references/, SKILL.md (matches the shipped layout).
[string[]]$skillFiles = @($tracked | Where-Object { $_.StartsWith("$skillDir/") })
[Array]::Sort($skillFiles, [StringComparer]::OrdinalIgnoreCase)

$pluginTop = @('README.md', 'LICENSE', 'plugin.json', '.claude-plugin/plugin.json',
    '.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json')

# zip path (relative to dist) -> list of @{ Entry; Source }
$packages = [ordered]@{
    'asd-ste100-style-plugin.zip' = @(
        $pluginTop | ForEach-Object { @{ Entry = "asd-ste100-style/$_"; Source = $_ } }
        $skillFiles | ForEach-Object { @{ Entry = "asd-ste100-style/$_"; Source = $_ } })
    'asd-ste100-zh-tw.zip'        = @(
        $skillFiles | ForEach-Object { @{ Entry = 'asd-ste100-zh-tw/' + $_.Substring($skillDir.Length + 1); Source = $_ } })
}

function Read-Normalized([string]$rel) {
    if ($rel -notin $tracked) { throw "not a tracked file: $rel" }
    $path = Join-Path $root $rel
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "missing in working tree: $rel" }
    $bytes = [IO.File]::ReadAllBytes($path)
    $text = [Text.UTF8Encoding]::new($false).GetString($bytes).Replace("`r`n", "`n")
    , [Text.UTF8Encoding]::new($false).GetBytes($text)
}

$distDir = Join-Path $root 'dist'
$failed = $false

foreach ($zipName in $packages.Keys) {
    $items = $packages[$zipName]
    $zipPath = Join-Path $distDir $zipName
    $expected = [ordered]@{}
    foreach ($i in $items) { $expected[$i.Entry] = Read-Normalized $i.Source }

    if ($Check) {
        if (-not (Test-Path -LiteralPath $zipPath)) { Write-Error "MISSING $zipName"; $failed = $true; continue }
        $zip = [IO.Compression.ZipFile]::OpenRead($zipPath)
        try {
            $actualNames = @($zip.Entries | ForEach-Object FullName)
            $expectedNames = @($expected.Keys)
            if (($actualNames -join "`n") -cne ($expectedNames -join "`n")) {
                Write-Host "FAIL $zipName entry list/order differs"
                Compare-Object $expectedNames $actualNames | ForEach-Object { Write-Host "  $($_.SideIndicator) $($_.InputObject)  (<= expected, => on disk)" }
                $failed = $true
            }
            foreach ($e in $zip.Entries) {
                if (-not $expected.Contains($e.FullName)) { continue }
                $ms = [IO.MemoryStream]::new(); $s = $e.Open(); $s.CopyTo($ms); $s.Dispose()
                $a = $ms.ToArray(); $b = $expected[$e.FullName]
                if (-not [Linq.Enumerable]::SequenceEqual([byte[]]$a, [byte[]]$b)) {
                    Write-Host "FAIL $zipName bytes differ: $($e.FullName) (zip $($a.Length) B, working tree $($b.Length) B)"
                    $failed = $true
                }
            }
        } finally { $zip.Dispose() }
        if (-not $failed) { Write-Host "OK   $zipName ($($expected.Count) entries)" }
        continue
    }

    $tmp = "$zipPath.tmp"
    if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp }
    $fs = [IO.File]::Create($tmp)
    $zip = [IO.Compression.ZipArchive]::new($fs, [IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($name in $expected.Keys) {
            $entry = $zip.CreateEntry($name, [IO.Compression.CompressionLevel]::Optimal)
            $entry.LastWriteTime = $stamp
            $s = $entry.Open(); $s.Write($expected[$name], 0, $expected[$name].Length); $s.Dispose()
        }
    } finally { $zip.Dispose(); $fs.Dispose() }
    Move-Item -LiteralPath $tmp -Destination $zipPath -Force
    Write-Host "built $zipName ($($expected.Count) entries)"
}

if ($failed) { exit 1 }
