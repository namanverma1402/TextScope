# TextScope GenAI setup

## 1. Create a Gemini API key
Create a key through Google AI Studio. Keep it private; do not paste it into chat, browser code, or GitHub.

## 2. Configure locally
Install dependencies with `pip install -r requirements.txt`. Set `GEMINI_API_KEY` in your shell environment (or use a local .env loader if you add one). Example PowerShell session:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY_HERE"
python app.py
```

Open `http://127.0.0.1:5000/genai`.

## 3. Configure Render
Open the TextScope web service in Render, go to Environment, and add:
- Key: `GEMINI_API_KEY`
- Value: your private Gemini API key

Optional:
- `GEMINI_MODEL` = `gemini-2.5-flash`

Save changes and redeploy/restart the service. Do not put secrets in source files or commit a real `.env` file.

## Features
- Summarize a TXT, PDF, DOCX, or pasted text.
- Compare two documents for similarities, differences, and unique details.
- Uses the existing text extraction helpers. Scanned PDFs without an OCR text layer may return little or no content.

## Limits and privacy
- Each document is limited to 200,000 characters at the form level; the first 80,000 characters per document are sent to the model.
- Text sent to Gemini is processed by Google's API under the applicable account terms and settings. Do not submit sensitive or confidential documents unless authorized.
- Model outputs may be incomplete or incorrect. Verify important information against the original.
- API availability, quotas, and billing depend on your Google AI Studio / Gemini account.
