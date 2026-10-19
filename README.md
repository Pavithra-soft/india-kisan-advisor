# India Kisan Advisor

Mobile-first farmer advisory app with an **accuracy-first** backend: verified facts, deterministic fertilizer math, abstention when evidence is weak, and signed daily sync bundles for offline use.

**Not related to India Talent Scout** — this is a separate repository.

## Structure

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI API (`/health`, `/qa`, `/fertilizer/recommend`, `/diagnose`, `/sync/bundle`) |
| `mobile/` | Expo (React Native) app for Android & iOS |
| `docs/` | Accuracy design and release report |

## Backend (local)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

Tests:

```bash
cd backend && pytest -q
```

## Mobile app

```bash
cd mobile
npm install
```

Set the API URL for your device:

- **iOS Simulator**: `http://127.0.0.1:8090` (default in `app.json` → `extra.apiUrl`)
- **Android Emulator**: `http://10.0.2.2:8090`
- **Physical phone**: `export EXPO_PUBLIC_API_URL=http://<your-laptop-LAN-IP>:8090`

```bash
npx expo start
```

Then press `a` (Android) or `i` (iOS), or scan the QR code with Expo Go.

### App features

- **Ask** — grounded Q&A with confidence and citations  
- **Fertilizer** — soil-test-based calculator (no LLM doses)  
- **Diagnose** — camera upload (restricted until vision models pass field gates)  
- **Settings** — region/crops profile + **offline sync** (`/sync/bundle`)

## Deploy API

Use `backend/Dockerfile` on any container host. Set `AGRI_BUNDLE_SECRET` and tighten `CORS_ORIGINS` for production.

## Accuracy docs

- Design: [`docs/agri-accuracy-design.md`](docs/agri-accuracy-design.md)  
- Baseline metrics: [`docs/agri-accuracy-report.md`](docs/agri-accuracy-report.md)
