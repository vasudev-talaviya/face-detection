# setup.ps1 - Windows PowerShell
# Run with: .\setup.ps1

$REPO_URL     = "https://github.com/vasudev-talaviya/face-detection.git"
$VENV_NAME    = "venv"
$PROJECT_NAME = ($REPO_URL.TrimEnd("/").Split("/")[-1]).Replace(".git", "")
$HASH_FILE    = ".requirements.hash"

# --------------------------------------------------
# STEP 1 - CLONE
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 1] Clone Repository" -ForegroundColor Cyan

if (Test-Path $PROJECT_NAME) {
    Write-Host "  [SKIP] Already cloned." -ForegroundColor Yellow
} else {
    Write-Host "  Cloning..."
    git clone $REPO_URL
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Clone failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Cloned." -ForegroundColor Green
}

Set-Location $PROJECT_NAME
Write-Host "  [DIR] $(Get-Location)"

# --------------------------------------------------
# STEP 2 - CREATE VENV
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 2] Virtual Environment" -ForegroundColor Cyan

if (Test-Path $VENV_NAME) {
    Write-Host "  [SKIP] venv already exists." -ForegroundColor Yellow
} else {
    Write-Host "  Creating venv..."
    python -m venv $VENV_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] venv creation failed." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] venv created." -ForegroundColor Green
}

# --------------------------------------------------
# STEP 3 - VERIFY PATHS
# --------------------------------------------------
$PYTHON = "$VENV_NAME\Scripts\python.exe"
$PIP    = "$VENV_NAME\Scripts\pip.exe"

Write-Host ""
Write-Host "[STEP 3] Verify Paths" -ForegroundColor Cyan

if (-not (Test-Path $PYTHON)) {
    Write-Host "  [ERROR] Python not found at: $PYTHON" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $PIP)) {
    Write-Host "  [ERROR] pip not found at: $PIP" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] python -> $PYTHON" -ForegroundColor Green

# --------------------------------------------------
# STEP 4 - ACTIVATE VENV IN THIS TERMINAL
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 4] Activating venv in this terminal..." -ForegroundColor Cyan
& "$VENV_NAME\Scripts\Activate.ps1"
Write-Host "  [OK] venv is now active in this terminal!" -ForegroundColor Green

# --------------------------------------------------
# STEP 5 - UPGRADE PIP
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 5] Upgrade pip" -ForegroundColor Cyan
python -m pip install --upgrade pip --quiet
Write-Host "  [OK] pip up to date." -ForegroundColor Green

# --------------------------------------------------
# STEP 6 - INSTALL REQUIREMENTS (skip if unchanged)
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 6] Install Requirements" -ForegroundColor Cyan

$REQ_FILE = Join-Path (Get-Location) "requirements.txt"

if (-not (Test-Path $REQ_FILE)) {
    Write-Host "  [WARN] requirements.txt not found at: $REQ_FILE" -ForegroundColor Yellow
} else {
    # FIX: Use built-in Get-FileHash with full path — no .NET path mismatch
    $currentHash = (Get-FileHash -Path $REQ_FILE -Algorithm MD5).Hash
    $savedHash   = ""

    $HASH_FULL = Join-Path (Get-Location) $HASH_FILE
    if (Test-Path $HASH_FULL) {
        $savedHash = (Get-Content $HASH_FULL).Trim()
    }

    if ($currentHash -eq $savedHash) {
        Write-Host "  [SKIP] requirements.txt unchanged. No reinstall needed." -ForegroundColor Yellow
        Write-Host "         Delete $HASH_FILE to force reinstall."
    } else {
        if ($savedHash -eq "") {
            Write-Host "  [NEW] First install - installing all packages..."
        } else {
            Write-Host "  [CHANGED] requirements.txt changed - reinstalling..."
        }

        pip install -r $REQ_FILE
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] pip install failed." -ForegroundColor Red
            exit 1
        }

        # Save new hash
        $currentHash | Out-File -FilePath $HASH_FULL -Encoding utf8 -NoNewline
        Write-Host "  [OK] Packages installed in venv (NOT global)." -ForegroundColor Green
    }
}

# --------------------------------------------------
# STEP 7 - RUN PROJECT
# --------------------------------------------------
Write-Host ""
Write-Host "[STEP 7] Run Project" -ForegroundColor Cyan

if (Test-Path "main.py") {
    python main.py
} else {
    Write-Host "  [WARN] main.py not found, skipping." -ForegroundColor Yellow
}

# --------------------------------------------------
# DONE
# --------------------------------------------------
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETE - venv is ACTIVE here" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  python -> $(python --version)"
Write-Host "  pip    -> $(pip --version)"
Write-Host ""
Write-Host "  Run [deactivate] to exit the venv." -ForegroundColor Yellow
Write-Host ""
