if ($env:VIRTUAL_ENV -ne '') {
    $PREFIX = "$env:VIRTUAL_ENV\Scripts\"
} elseif (Test-Path '.venv') {
    $PREFIX = ".venv\Scripts\"
}

$SOURCE_FILES = "esmerald", "tests", "docs_src"
$EXCLUDE = "__init__.py"

$VerbosePreference = "Continue"

& "${PREFIX}mypy" esmerald
& "${PREFIX}ruff" check $SOURCE_FILES --fix --line-length 99
& "${PREFIX}black" $SOURCE_FILES --line-length 99
