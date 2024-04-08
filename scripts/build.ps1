# Initialize PREFIX variable
$PREFIX = ""

# Check if VIRTUAL_ENV variable is set
if ($env:VIRTUAL_ENV -ne '') {
    $PREFIX = "$env:VIRTUAL_ENV\Scripts\"
}
# Check if 'venv' directory exists
elseif (Test-Path 'venv') {
    $PREFIX = ".\.venv\Scripts\"
}
# Otherwise, leave PREFIX as empty string

# Enable verbose output
$VerbosePreference = "Continue"

# Check if 'build' package is installed, if not, install it
if (-not (Get-Module -ListAvailable -Name build)) {
    Write-Host "Installing 'build' package..."
    & "${PREFIX}pip" install build
}

# Check if 'twine' package is installed, if not, install it
if (-not (Get-Module -ListAvailable -Name twine)) {
    Write-Host "Installing 'twine' package..."
    & "${PREFIX}pip" install twine
}

# Execute python -m build command using PREFIX
& "${PREFIX}python" -m build

# Execute twine check dist/* command using PREFIX
& "${PREFIX}twine" check dist\*
