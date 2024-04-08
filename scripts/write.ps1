# Loop through all .py files in the current directory and its subdirectories
Get-ChildItem -Path . -Recurse -Filter '*.py' -File | ForEach-Object {
    # Check if the file path contains 'venv' or '.venv', and skip those files
    if ($_.FullName -notmatch '\\venv\\|\\.venv\\') {
        # Skip __init__.py and __main__.py files
        if ($_.Name -ne '__init__.py' -and $_.Name -ne '__main__.py') {
            # Display the file path
            Write-Host $_.FullName
            # Add "from __future__ import annotations" to the beginning of the file
            (Get-Content $_.FullName) | Foreach-Object {
                $_ -replace '^', 'from __future__ import annotations`n'
            } | Set-Content $_.FullName
        }
    }
}
