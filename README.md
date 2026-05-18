# 🚀 Project Setup Guide

> **Computer Vision · MongoDB · Python** — A compute-intensive vision pipeline with flexible local and cloud database support.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Method 1 — Automated Setup (Recommended)](#method-1--automated-setup-recommended)
- [Method 2 — Manual Setup](#method-2--manual-setup)
- [Database Configuration](#database-configuration)
- [Environment Variables](#environment-variables)
- [Performance Notes](#performance-notes)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before getting started, ensure the following are installed on your system:

| Tool | Purpose | Download |
|------|---------|----------|
| **Python 3.8+** | Core runtime | [python.org](https://python.org) |
| **MongoDB Compass** *(optional)* | Local database GUI | [mongodb.com/compass](https://www.mongodb.com/products/compass) |
| **PowerShell / pwsh** | Automated setup script | Pre-installed on Windows; `brew install --cask powershell` on macOS |

> ⚠️ **Note:** This project uses computer vision algorithms that are computationally intensive. A modern CPU (or GPU) with sufficient RAM is strongly recommended. Processing times will vary based on your hardware specifications.

---

## Quick Start

Choose the method that best fits your workflow:

```
Method 1  →  Automated  →  Run setup.ps1 (fastest)
Method 2  →  Manual     →  venv + pip install
```

---

## Method 1 — Automated Setup (Recommended)

A single PowerShell script handles the entire environment setup automatically.

### 🪟 Windows

Open **Terminal** or **CMD** and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

### 🐧 Linux / macOS

First, verify that `pwsh` (PowerShell Core) is installed:

```bash
pwsh --version
```

If not installed:
```bash
# Ubuntu / Debian
sudo apt-get install -y powershell

# macOS (Homebrew)
brew install --cask powershell
```

Then run the setup script:

```bash
pwsh ./setup.ps1
```

---

## Method 2 — Manual Setup

If you prefer full control or the automated script fails, follow these steps:

### Step 1 — Create a Virtual Environment

```bash
python -m venv venv
```

### Step 2 — Activate the Virtual Environment

**Windows:**
```powershell
./venv/Scripts/Activate
```

**Linux / macOS:**
```bash
source ./venv/bin/activate
```

> ✅ You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 3 — Install Required Packages

```bash
pip install -r requirements.txt
```

---

## Database Configuration

This project supports both **local** and **cloud (Atlas)** MongoDB instances.

### 🖥️ Local MongoDB

Install and run [MongoDB Compass](https://www.mongodb.com/products/compass) on your machine. No API key is required for local connections.

### ☁️ MongoDB Atlas (Cloud)

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Obtain your **connection string / API key**
3. Add it to your `.env` file (see below)

### Config File

All database settings are centrally managed in:

```
database/config.py
```

This file is designed for easy modification — update the connection string, database name, or collection names here without touching the rest of the codebase.

---

## Environment Variables

Create a `.env` file in the project root and configure it as follows:

```env
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017        # Local
# MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/  # Atlas (Cloud)

MONGO_DB_NAME=your_database_name

# Add other project-specific keys below
```

> 🔒 Never commit your `.env` file to version control. It is already listed in `.gitignore`.

---

## Performance Notes

This project includes **computer vision algorithms** which are resource-intensive by nature.

| Factor | Recommendation |
|--------|---------------|
| **CPU** | Multi-core processor (4+ cores recommended) |
| **RAM** | 8 GB minimum; 16 GB+ for larger workloads |
| **GPU** | Optional but significantly speeds up processing |
| **Storage** | SSD recommended for faster I/O during processing |

> ⏳ **Please be patient during processing.** Execution time depends entirely on your hardware. This is expected behaviour and not a bug.

---

## Troubleshooting

### `pwsh` not found (Linux)
```bash
sudo apt-get install -y powershell   # Debian/Ubuntu
```

### Virtual environment activation fails (Windows)
Run this in PowerShell before activating:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MongoDB connection refused
- Ensure MongoDB service is running: `sudo systemctl start mongod`
- Check your `MONGO_URI` in the `.env` file

### Packages fail to install
Upgrade pip first, then retry:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
├── database/
│   └── config.py          # ← Database settings (edit here)
├── venv/                  # Virtual environment (auto-generated)
├── requirements.txt       # Python dependencies
├── setup.ps1              # Automated setup script
├── .env                   # Environment variables (create manually)
└── README.md
```

---

<div align="center">

Made with ❤️ — Configure once, run anywhere.

</div>
