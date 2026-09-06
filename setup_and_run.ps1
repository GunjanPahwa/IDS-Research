# Setup ids_research conda env and launch UWF ZeekData preprocessing
# Run from project root: .\setup_and_run.ps1

$CONDA = "$env:USERPROFILE\AppData\Local\miniconda3\Scripts\conda.exe"
$PROJECT = $PSScriptRoot

if (-not (Test-Path $CONDA)) {
    Write-Error "conda not found at $CONDA. Ensure Miniconda is installed."
    exit 1
}

# Initialise conda for this shell session
(& $CONDA "shell.powershell" "hook") | Out-String | Invoke-Expression

# Create environment if it doesn't exist
$envExists = (& $CONDA env list) | Select-String "ids_research"
if (-not $envExists) {
    Write-Host "Creating ids_research environment (Python 3.11)..."
    & $CONDA create -n ids_research python=3.11 -y
} else {
    Write-Host "ids_research environment already exists."
}

# Install/update dependencies
Write-Host "Installing dependencies..."
& $CONDA run -n ids_research pip install -r "$PROJECT\requirements.txt"

# Verify key packages
Write-Host "Verifying environment..."
& $CONDA run -n ids_research python -c "import pandas, numpy, pyarrow, polars, sklearn, scipy, joblib; print('All packages OK')"

# Launch preprocessing for UWF ZeekData (background, survives shell closure)
$logFile = "$PROJECT\logs\uwf_preprocessing_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -ItemType Directory -Force -Path "$PROJECT\logs" | Out-Null

Write-Host "Launching preprocessing in background. Log: $logFile"
$condaRun = "$env:USERPROFILE\AppData\Local\miniconda3\Scripts\conda.exe"
$pythonArgs = "run -n ids_research python `"$PROJECT\scratch\run_full_preprocessing.py`""

# Use Start-Process with -WindowStyle Hidden so it detaches from this shell
Start-Process -FilePath $condaRun -ArgumentList $pythonArgs `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError "$logFile.err" `
    -WindowStyle Hidden -PassThru | 
    ForEach-Object { Write-Host "Preprocessing PID: $($_.Id). Monitor: Get-Content '$logFile' -Wait" }
