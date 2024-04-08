# Path to the version file
$VERSION_FILE = "esmerald\__init__.py"

# Get the version number from the version file
$VERSION = Select-String -Path $VERSION_FILE -Pattern '__version__' | ForEach-Object { $_.Line -match '\d+(\.\d+)+' | Out-Null; $matches[0] }

Write-Host $VERSION

Write-Host "Installing dependencies"
py -m pip install --upgrade pip
pip install mkdocs mkautodoc mkdocs-material griffe-typingdoc mdx-include pyyaml mkdocs-markdownextradata-plugin mkdocstrings[python] httpx starlette lilya mike a2wsgi mkdocs-meta-descriptions-plugin

Write-Host "Running version generator for version $VERSION"
mike deploy --update-aliases $VERSION latest

Write-Host "Setting default latest to version $VERSION"
mike set-default latest
