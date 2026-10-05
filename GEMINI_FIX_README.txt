MORPHVERT GEMINI SUMMARIZER PATCH

What changed:
- Gemini model is configurable through backend/.env (GEMINI_MODEL).
- Defaults to gemini-3.8-flash.
- Tries stable fallback models if the selected model is unavailable or overloaded.
- Retries transient rate-limit/server-capacity errors once per model.
- Provides clearer errors for quota, model, key, and overload failures.

Setup:
1. Keep your real key only in backend/.env:
   GEMINI_API_KEY=your_actual_key
   GEMINI_MODEL=gemini-3.8-flash
2. Do not share backend/.env or put the key in frontend files.
3. From backend folder run:
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
4. Keep frontend running separately from frontend folder with npm run dev.

Note: This patch cannot remove Google-side quota limits or guarantee service availability.
If every fallback fails, inspect the backend terminal and Google AI Studio quota/key settings.
