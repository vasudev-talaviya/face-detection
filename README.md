# Face Detection Attendance API

A FastAPI backend for face detection, registration, recognition, and attendance tracking using InsightFace and MongoDB. A Vite React application is available in `frontend/` for UI development.

## Features

- Image-based face detection and recognition
- Multiple distinct face templates per registered person
- Attendance submission with duplicate prevention for registered users per day
- Attendance correction audit records and summary reporting
- Configurable CORS, trusted-host, image-size, and request-size protection
- Structured API layers for routes, services, validation, shared utilities, and database operations

## Backend Setup

Use Python 3.10 or later and a running MongoDB instance.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

The API starts at `http://localhost:8000`; interactive documentation is available at `/docs` unless it is disabled through configuration. For direct ASGI development startup from `backend/`, use `uvicorn app.main:app --reload`.

## Configuration

Create `.env` in the project root:

```env
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=face_detection
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TRUSTED_HOSTS=localhost,127.0.0.1
MAX_REQUEST_BYTES=15728640
MAX_IMAGE_BYTES=10485760
API_DOCS_ENABLED=true
API_KEY=replace-with-a-random-secret-for-deployed-use
```

Set `CORS_ORIGINS=*` only for temporary local testing. When `API_KEY` is configured, every `/api/` route except `/api/health` requires it in the `X-API-Key` request header. In deployed environments, set explicit browser origins and trusted hosts.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | API liveness response |
| `POST` | `/api/faces/detect` | Detect and match faces in a base64 image |
| `POST` | `/api/users` | Register a face template or append one to an existing user |
| `GET` | `/api/users` | List registered users and template counts |
| `DELETE` | `/api/users/{user_id}` | Delete one registered user |
| `POST` | `/api/attendance/scan` | Detect faces with attendance state and thumbnails |
| `POST` | `/api/attendance` | Confirm attendance entries |
| `GET` | `/api/attendance/today` | Retrieve today's attendance |
| `GET` | `/api/attendance?date=YYYY-MM-DD` | Retrieve attendance for a date |
| `GET` | `/api/attendance/corrections` | Retrieve correction reporting |

The scan/detect endpoints accept an image data URL or plain base64 image string. The normal detection response includes an embedding so an unknown face can be submitted to registration. Legacy paths such as `/api/detect`, `/api/register`, and the former attendance action paths remain callable during migration but are omitted from API documentation.

## Backend Structure

```text
backend/
|-- app/
|   |-- main.py               # FastAPI factory and ASGI application export
|   |-- api/
|   |   |-- router.py         # Shared /api router registration
|   |   |-- dependencies.py   # Repository/service dependency construction
|   |   |-- routes/           # Health, face detection, user, and attendance endpoints
|   |   `-- schemas/          # HTTP request validation
|   |-- core/                 # Settings, middleware, and API exceptions
|   |-- db/
|   |   |-- mongo.py          # MongoDB connection lifecycle
|   |   `-- models/           # Collection models and shared persisted field validation
|   |-- repositories/         # All MongoDB reads and writes
|   |-- services/             # Attendance, user, and detection workflows
|   |-- ml/                   # Face detector and similarity matching
|   `-- utils/                # Image encoding and date helpers
|-- scripts/                  # Optional command-line helpers
|-- tests/                    # Isolated repository tests
|-- main.py                   # Local Uvicorn launcher
`-- requirements.txt
```

## Design Notes

- Model loading is deferred until a detection endpoint is used, so health checks and API documentation do not initialize InsightFace.
- Route handlers do not perform database operations; persistence is isolated under `app/repositories/`.
- HTTP request schemas describe client payloads; MongoDB collection models and their shared validated fields live under `app/db/models/`.
- MongoDB client construction is lazy and is shut down with the FastAPI lifespan.
- Invalid images and invalid object IDs return client errors rather than generic server errors.
- Known-user attendance submission creates a unique partial MongoDB index and uses an atomic insert-if-not-present operation for the user/date pair.
- Adding an already stored template to an existing person is idempotent rather than creating duplicate embedding entries.
- Face embeddings are biometric data. Enable `API_KEY` at minimum, and use HTTPS and appropriate retention controls before exposing this API beyond a trusted development environment.
