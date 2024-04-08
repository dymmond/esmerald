# Check if VIRTUAL_ENV is set and set the PREFIX accordingly
if ($env:VIRTUAL_ENV -ne '') {
    $PREFIX = "$env:VIRTUAL_ENV\Scripts\"
} elseif (Test-Path '.venv') {
    $PREFIX = ".venv\Scripts\"
}

# Enable verbose output.
$VerbosePreference = "Continue"

if (-not $env:GITHUB_ACTIONS) {
    & .\scripts\lint.ps1
}

$env:ESMERALD_SETTINGS_MODULE = 'tests.settings.TestSettings'

& "${PREFIX}pytest" $env:ARGS

Remove-Item Env:\ESMERALD_SETTINGS_MODULE
