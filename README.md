# TextScope — Text Similarity & AI Writing Analysis

A local Flask application with two separate tools:

1. **Text similarity:** Compare text against pasted reference material or uploaded TXT, PDF, and DOCX files using TF-IDF word/bigram and character n-gram cosine similarity.
2. **Experimental AI-writing analysis:** An optional Hugging Face text classifier that estimates whether writing resembles its learned generated-text examples. It is an experimental signal, not a dependable AI detector.

## Run the core app on Windows
1. Install Python 3.10+ and enable **Add Python to PATH**.
2. Extract this folder and open PowerShell in it.
3. Run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python app.py
   ```
4. Open **http://127.0.0.1:5000**. Stop the server with Ctrl+C.

If PowerShell activation is blocked, use Command Prompt and run `.venv\Scripts\activate.bat`.

## Enable AI-writing analysis (optional)
The text-similarity feature works without these extra packages. AI analysis uses the public `openai-community/roberta-base-openai-detector` model and requires a first-time model download plus PyTorch/Transformers. This can be a large download and needs an internet connection on first use.

In the activated virtual environment, run:
```powershell
pip install -r requirements-ai.txt
```
Restart `python app.py`, select **AI writing analysis**, paste text, and click **Analyze writing**. The first analysis may take a while while the model downloads and loads.

## Important limitations
- The AI detector is an older GPT-2-era classifier. It is not validated as a general-purpose detector for modern AI systems, paraphrased text, mixed-authorship writing, or every language.
- The displayed model confidence is confidence in its predicted class, **not the percentage of a document written by AI**. It is not calibrated proof of authorship. False positives and false negatives are possible.
- Sentence-level outputs are exploratory and especially unreliable for short passages.
- Similarity scores are not proof of plagiarism. Scanned PDFs need OCR, which is not included.
- Uploaded files are processed in memory and not intentionally saved by this app. Flask's built-in server is for local development only; do not expose it publicly as-is.

## Resume wording (only after testing)
**TextScope — Text Similarity & AI Writing Analysis | Python, Flask, scikit-learn, Transformers**
- Built a Flask web app to compare submitted text against multiple TXT/PDF/DOCX reference documents using TF-IDF and character n-gram similarity.
- Integrated an experimental pretrained text classifier for AI-writing signals with exploratory sentence-level outputs and explicit uncertainty warnings.

Only list the AI-analysis bullet after installing the optional dependencies and verifying that model inference runs on your machine. Be ready to explain the detector's limitations.
