# Check if 'dist' directory exists and remove it if it does
if (Test-Path 'dist' -PathType Container) {
    Remove-Item -Path 'dist' -Recurse -Force
}

# Check if 'site' directory exists and remove it if it does
if (Test-Path 'site' -PathType Container) {
    Remove-Item -Path 'site' -Recurse -Force
}

# Check if 'htmlcov' directory exists and remove it if it does
if (Test-Path 'htmlcov' -PathType Container) {
    Remove-Item -Path 'htmlcov' -Recurse -Force
}

# Check if 'esmerald.egg-info' directory exists and remove it if it does
if (Test-Path 'esmerald.egg-info' -PathType Container) {
    Remove-Item -Path 'esmerald.egg-info' -Recurse -Force
}

# Check if '.hypothesis' directory exists and remove it if it does
if (Test-Path '.hypothesis' -PathType Container) {
    Remove-Item -Path '.hypothesis' -Recurse -Force
}

# Check if '.mypy_cache' directory exists and remove it if it does
if (Test-Path '.mypy_cache' -PathType Container) {
    Remove-Item -Path '.mypy_cache' -Recurse -Force
}

# Check if '.pytest_cache' directory exists and remove it if it does
if (Test-Path '.pytest_cache' -PathType Container) {
    Remove-Item -Path '.pytest_cache' -Recurse -Force
}

# Check if '.ruff_cache' directory exists and remove it if it does
if (Test-Path '.ruff_cache' -PathType Container) {
    Remove-Item -Path '.ruff_cache' -Recurse -Force
}
