# Determine Python executable from the provided `-p` option or use the default.
if ($args[0] -eq "-p") {
    $PYTHON = $args[1]
} else {
    $PYTHON = "py"
}

$VENV = ".venv"

# Enable verbose output.
$VerbosePreference = "Continue"

# Check if the VIRTUAL_ENV variable is set
if ($env:VIRTUAL_ENV -ne $null) {
    $PIP = Join-Path $env:VIRTUAL_ENV "Scripts\pip.exe"
} else {
    # Create a virtual environment if VIRTUAL_ENV is not set
    & $PYTHON -m venv $VENV | Out-Null
    $PIP = Join-Path $VENV "Scripts\pip.exe"
}

# Install or upgrade pip
& $PYTHON -m pip install --upgrade pip

# Install required packages
& $PIP install -e .[dev,test,doc,templates,jwt,encoders,schedulers,ipython,ptpython]
