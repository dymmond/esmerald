# Loop through all .py files in the current directory and its subdirectories
foreach ($file in Get-ChildItem -Path . -Recurse -Filter '*.py' -File) {
    # Skip __init__.py and __main__.py files
    if ($file.Name -ne '__init__.py' -and $file.Name -ne '__main__.py') {
        # Display the file path
        Write-Host $file.FullName
        # Add "from __future__ import annotations" to the beginning of the file
        (Get-Content $file.FullName) | Foreach-Object {
            $_ -replace '^', 'from __future__ import annotations`n'
        } | Set-Content $file.FullName
    }
}
