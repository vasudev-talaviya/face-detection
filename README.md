# Face Detection With Database

A Python-based face detection, recognition, and registration system built with InsightFace and MongoDB.

This repository provides both command-line and GUI workflows for:
- real-time webcam face detection
- image-based face recognition
- unknown face registration
- storing face embeddings in MongoDB

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Design](#database-design)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

---

## Overview

This project uses InsightFace to detect faces and compute face embeddings from images or webcam video.

Registered embeddings are stored in MongoDB so that the system can identify known users and register unknown faces for future recognition.

The main entrypoint is `main.py`.

- No arguments: launches the GUI
- `--test 1`: webcam mode
- `--test 2 --image <path>`: image detection and registration mode

---

## Features

- Face detection using InsightFace (`buffalo_l` model)
- Face verification with cosine similarity and vote ratio
- MongoDB-backed registration and lookup
- Tkinter GUI for camera, video, and image operations
- CLI support for quick testing
- Automatic small-face filtering for more reliable results

---

## Technology Stack

- Python 3.8+
- OpenCV (`opencv-python`)
- InsightFace
- ONNX Runtime
- NumPy
- Pillow
- Matplotlib
- MongoDB / PyMongo
- Pydantic
- python-dotenv
- Tkinter

---

## Prerequisites

Install Python 3.8 or newer.

Also install or run a MongoDB instance:
- locally via MongoDB Community Server
- or remotely via MongoDB Atlas

Optional:
- PowerShell for automated setup
- GPU for faster face detection

---

## Installation

### Automated setup (recommended)

From the `face-detection` folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

This script should create a virtual environment and install dependencies.

### Manual setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate it:

- Windows:

```powershell
./venv/Scripts/Activate
```

- macOS / Linux:

```bash
source ./venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

### Environment variables

Create a `.env` file in the project root with:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=face_detection_db
```

For MongoDB Atlas:

```env
MONGODB_URL=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE_NAME=face_detection_db
```

These values are loaded in `database/config/config.py`.

### Database collection

The project stores registered face records in the `ImageEmbedding` collection.
Each record includes:
- `name`
- `embedding`

---

## Usage

### GUI mode

Run the project without arguments:

```bash
python main.py
```

This starts the Tkinter GUI for camera, video, and image-based operations.

### CLI mode

#### Webcam / live camera mode

```bash
python main.py --test 1
```

#### Static image mode

```bash
python main.py --test 2 --image path/to/image.jpg
```

### Image registration flow

When using image mode:
- no faces found → exits with a message
- known faces found → displays registered names
- exactly one unknown face found → allows registration
- multiple unknown faces → registration is blocked

Newly detected face images are saved to `src/detected_image/detect.jpg`.

---

## Database Design

### Configuration

`database/config/config.py` loads MongoDB settings from the environment.

### Validation

`database/models/faceid.py` defines the stored record schema:
- `name: str`
- `embedding: List[List[float]]`

### Matching algorithm

`models/similarity_check.py` performs face comparison by:
- converting face embeddings into NumPy arrays
- computing cosine similarity
- using cosine distance threshold `0.60`
- requiring at least `40%` vote ratio across stored embeddings

A face is confirmed as a registered match only when both distance and vote-ratio conditions are satisfied.

---

## Project Structure

```
face-detection/
├── database/
│   ├── config/
│   │   └── config.py
│   ├── models/
│   │   └── faceid.py
│   └── operation/
│       ├── basic_oper.py
│       └── image_store.py
├── models/
│   └── similarity_check.py
├── modules/
│   ├── command/
│   │   └── CLI.py
│   └── pipeline/
│       └── face_detect.py
├── src/
│   ├── detected_image/
│   └── gui/
│       └── app.py
├── main.py
├── requirements.txt
├── setup.ps1
└── README.md
```

---

## Troubleshooting

### MongoDB connection errors
- Verify `MONGODB_URL` and `MONGODB_DATABASE_NAME` in `.env`
- Ensure MongoDB is running

### Webcam fails to open
- Close other apps using the camera
- Confirm camera permissions and device availability

### No face detected
- Use a clear frontal image
- Avoid strong blur and poor lighting

### Registration blocked for multi-face image
- Upload a single-face image for new user registration

### Dependency install issues

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Notes

- Faces smaller than `80px` are skipped to reduce false positives.
- The GUI uses Matplotlib for image display and Tkinter for controls.
- The project is intended for learning and local experimentation.

---

## License

No license file is included. Use this repository for experimentation and learning.
