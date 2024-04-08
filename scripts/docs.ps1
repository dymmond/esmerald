# Initialize PREFIX variable
$PREFIX = ""

# Check if VIRTUAL_ENV variable is set
if ($env:VIRTUAL_ENV -ne '') {
    $PREFIX = "$env:VIRTUAL_ENV\Scripts\"
}
# Check if 'venv' directory exists
elseif (Test-Path 'venv') {
    $PREFIX = ".\venv\Scripts\"
}

# Enable verbose output
$VerbosePreference = "Continue"

# Execute mkdocs serve command using PREFIX
& "${PREFIX}mkdocs" serve
