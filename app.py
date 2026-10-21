from pathlib import Path
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from similarity import compare_documents, extract_text_from_file
from genai_tools import generate_document_insight

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
ALLOWED = {'.txt', '.pdf', '.docx'}
MAX_CHARS = 200_000


def render_page(**kwargs):
    defaults = dict(mode='similarity', results=None, ai_result=None, error=None,
                    query='', reference_text='', warnings=[])
    defaults.update(kwargs)
    return render_template('index.html', **defaults)


@app.get('/')
def index():
    mode = request.args.get('mode', 'similarity')
    if mode not in {'similarity', 'ai', 'genai'}:
        mode = 'similarity'
    return render_page(mode=mode)


@app.route('/genai', methods=['GET', 'POST'])
def genai():
    if request.method == 'GET':
        return render_template('genai.html', result=None, error=None, task='summary', warnings=[])
    task = request.form.get('task', 'summary')
    if task not in {'summary', 'compare'}:
        task = 'summary'
    primary = request.form.get('document_text', '').strip()
    secondary = request.form.get('comparison_text', '').strip()
    warnings = []
    for field_name, target in [('document_file', 'primary'), ('comparison_file', 'secondary')]:
        uploaded = request.files.get(field_name)
        if not uploaded or not uploaded.filename:
            continue
        suffix = Path(secure_filename(uploaded.filename)).suffix.lower()
        if suffix not in ALLOWED:
            warnings.append(f'{uploaded.filename}: unsupported file type. Use TXT, PDF or DOCX.')
            continue
        try:
            extracted = extract_text_from_file(uploaded, suffix).strip()
            if target == 'primary' and not primary:
                primary = extracted
            elif target == 'secondary' and not secondary:
                secondary = extracted
        except Exception:
            warnings.append(f'{uploaded.filename}: unable to read this file.')
    if not primary:
        return render_template('genai.html', result=None, error='Paste or upload a document to analyze.', task=task, warnings=warnings), 400
    if task == 'compare' and not secondary:
        return render_template('genai.html', result=None, error='For comparison, add a second document.', task=task, document_text=primary, warnings=warnings), 400
    if len(primary) > MAX_CHARS or len(secondary) > MAX_CHARS:
        return render_template('genai.html', result=None, error='Each document is limited to 200,000 characters.', task=task, warnings=warnings), 400
    try:
        result = generate_document_insight(task, primary, secondary)
        return render_template('genai.html', result=result, error=None, task=task, document_text=primary, comparison_text=secondary, warnings=warnings)
    except ValueError as exc:
        return render_template('genai.html', result=None, error=str(exc), task=task, document_text=primary, comparison_text=secondary, warnings=warnings), 400
    except Exception:
        app.logger.exception('GenAI document analysis failed')
        return render_template('genai.html', result=None, error='GenAI request failed. Check the API key, quota, and server logs, then try again.', task=task, document_text=primary, comparison_text=secondary, warnings=warnings), 502


@app.post('/compare')
def compare():
    query = request.form.get('query', '').strip()
    ref_text = request.form.get('reference_text', '').strip()
    warnings, refs = [], []
    if len(query) > MAX_CHARS or len(ref_text) > MAX_CHARS:
        return render_page(results=None, error='Text limit is 200,000 characters per field.', query=query[:MAX_CHARS], reference_text=ref_text[:MAX_CHARS]), 400
    if ref_text:
        refs.append({'name': 'Pasted reference', 'text': ref_text})
    for f in request.files.getlist('reference_files'):
        if not f or not f.filename:
            continue
        name = secure_filename(f.filename)
        suffix = Path(name).suffix.lower()
        if suffix not in ALLOWED:
            warnings.append(f'{name}: unsupported file type. Use TXT, PDF or DOCX.')
            continue
        try:
            extracted = extract_text_from_file(f, suffix)
            if extracted.strip():
                refs.append({'name': name, 'text': extracted[:MAX_CHARS]})
            else:
                warnings.append(f'{name}: no readable text found. Scanned PDFs may need OCR.')
        except Exception:
            warnings.append(f'{name}: unable to read file; check it is valid and not password-protected.')
    error = None
    if not query:
        error = 'Enter the text you want to check.'
    elif not refs:
        error = 'Add reference text or upload at least one TXT, PDF or DOCX file.'
    if error:
        return render_page(results=None, error=error, query=query, reference_text=ref_text, warnings=warnings), 400
    results = compare_documents(query, refs)
    return render_page(results=results, query=query, reference_text=ref_text, warnings=warnings)


@app.post('/analyze-ai')
def analyze_ai():
    query = request.form.get('query', '').strip()
    try:
        from ai_detector import analyze_ai_text
        ai_result = analyze_ai_text(query)
        return render_page(mode='ai', ai_result=ai_result, query=query)
    except (ValueError, RuntimeError) as exc:
        return render_page(mode='ai', error=str(exc), query=query), 400
    except Exception:
        return render_page(mode='ai', error='AI analysis failed unexpectedly. Check the terminal for details.', query=query), 500


@app.errorhandler(413)
def too_large(_error):
    return render_page(error='Upload too large. Total request limit is 12 MB.'), 413


if __name__ == '__main__':
    # Local development only; do not expose Flask debug server publicly.
    app.run(debug=True)
