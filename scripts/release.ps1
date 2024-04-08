$VERSION_FILE = "esmerald\__init__.py"

$PREFIX = ""

if ($env:VIRTUAL_ENV -ne '') {
    $PREFIX = "$env:VIRTUAL_ENV\Scripts\"
} elseif (Test-Path 'venv') {
    $PREFIX = ".\.venv\Scripts\"
}

if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_ACTIONS)) {
    git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git config --local user.name "GitHub Action"

    $VERSION = (Select-String -Path $VERSION_FILE -Pattern '__version__').Line -replace '.*"([^"]+)".*', '$1'

    if ("refs/tags/$VERSION" -ne $env:GITHUB_REF) {
        Write-Host "GitHub Ref '$($env:GITHUB_REF)' did not match package version '$VERSION'"
        exit 1
    }
}

$VerbosePreference = "Continue"

& "${PREFIX}twine" upload dist\*
