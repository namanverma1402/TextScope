"""Gemini-powered document insights for TextScope.

The API key is read only from the server environment; never expose it to the browser.
"""
import os


def generate_document_insight(task, primary_text, secondary_text=""):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GenAI is not configured yet. Add GEMINI_API_KEY to your environment "
            "or Render service settings, then restart/redeploy."
        )
    if not primary_text.strip():
        raise ValueError("Add readable document text before running the analysis.")
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("GenAI dependency is missing. Install requirements.txt and redeploy.") from exc

    # Keep request size predictable and avoid sending unbounded user input to the provider.
    primary = primary_text[:80000]
    secondary = secondary_text[:80000]
    truncated = len(primary_text) > len(primary) or len(secondary_text) > len(secondary)
    if task == "compare":
        if not secondary_text.strip():
            raise ValueError("Add a second document to compare.")
        instruction = (
            "Compare the two documents carefully. Return a readable report with these headings: "
            "Executive summary, Key similarities, Key differences, Important details unique to Document A, "
            "Important details unique to Document B, and Caveats. Use concise bullets. "
            "Only state claims supported by the provided text. If information is missing or ambiguous, say so."
        )
        prompt = f"{instruction}\n\nDOCUMENT A:\n{primary}\n\nDOCUMENT B:\n{secondary}"
    else:
        instruction = (
            "Summarize the document for a busy reader. Use these headings: "
            "TL;DR, Key points, Important names/dates/numbers, and Questions or caveats. "
            "Be faithful to the source, do not invent facts, and mark uncertainty explicitly."
        )
        prompt = f"{instruction}\n\nDOCUMENT:\n{primary}"

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        contents=prompt,
        config={"temperature": 0.2, "max_output_tokens": 1800},
    )
    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise RuntimeError("The AI provider returned an empty response. Please try again.")
    if truncated:
        text += "\n\nNote: Input exceeded the per-document processing limit; only the first 80,000 characters of each document were analyzed."
    return text
