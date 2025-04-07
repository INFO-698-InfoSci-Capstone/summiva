from backend.utils.html_processor import get_or_fetch_html


def get_raw_text(url: str | None, text: str | None) -> str:
    if url:
        return get_or_fetch_html(url)
    if text:
        return text
    raise ValueError("Neither URL nor text provided.")
