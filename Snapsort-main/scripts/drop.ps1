# PowerShell drop script for Windows
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("jio", "airtel", "lab")]
    [string]$Target
)

$root = "$PSScriptRoot\.."

switch ($Target) {
    "jio" {
        $src = (Get-ChildItem -Path "$root\mock\_demo_drops\Screenshot*.png" | Select-Object -First 1).FullName
        $dest = "$root\mock\Screenshots"
    }
    "airtel" {
        $src = (Get-ChildItem -Path "$root\mock\_demo_drops\Airtel_Bill_*.pdf" | Select-Object -First 1).FullName
        $dest = "$root\mock\Downloads"
    }
    "lab" {
        $src = "$root\mock\_demo_drops\Apollo_followup.pdf"
        $dest = "$root\mock\Downloads"
    }
}

Copy-Item -Path $src -Destination $dest -Force
Write-Host "Dropped $(Split-Path $src -Leaf) into $(Split-Path $dest -Leaf)"
