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

# Install required packages
& $PIP install -e .[dev,test,doc,templates,jwt,encoders,schedulers,ipython,ptpython]

# Path to the activate script of the Python virtual environment
$activateScript = ".\.venv\Scripts\Activate.ps1"

# Check if the activate.ps1 file exists
if (Test-Path $activateScript) {
    # Run the activate script
    . $activateScript
    Write-Host "Virtual environment activated."
} else {
    Write-Host "Failed to find the activation script for the Python virtual environment."
}

# Install or upgrade pip
& $PYTHON -m pip install --upgrade pip