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

# Execute python -m build command using PREFIX
& "${PREFIX}python" -m build

# Execute twine check dist/* command using PREFIX
& "${PREFIX}twine" check dist\*
