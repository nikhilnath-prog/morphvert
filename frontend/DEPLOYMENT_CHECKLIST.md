# Morphvert Frontend Deployment Checklist

## Environment
- Set `VITE_API_URL` to the deployed FastAPI origin.
- Confirm the backend CORS allowlist includes the frontend origin.
- Keep local `.env.development` and production `.env.production` values separate.

## Build
- Run `npm run build` from `frontend/`.
- Verify the generated frontend bundle uses the correct API base URL.
- Check that history, download, and conversion flows still work after build.

## Backend
- Start the API on port `8000` for local development.
- Confirm `/api/v1/files/upload`, `/api/v1/convert/*`, `/api/v1/pdf/*`, and `/api/v1/download/{file_id}` are reachable.
- Ensure `http://localhost:5173` is allowed by CORS in development.

## Verification
- Upload a PDF and confirm the progress bar completes.
- Run PDF to DOCX and download the generated file.
- Run PDF to Images and confirm every generated file has a working download link.
- Run Merge PDF and Split PDF with multiple files.
- Open Conversion History and confirm items load from the backend.