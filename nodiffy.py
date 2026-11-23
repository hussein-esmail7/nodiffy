#!/usr/bin/env python3
"""
nodiffy: fetches pages, extracts content with defuddle, diffs against the
previously saved snapshot (.txt, UTF-8), and emails a formatted unified diff
when something changed.
"""

# Libraries that are preinstalled
import difflib
import hashlib
import datetime
import html
import os
import requests

# Libraries that require installation
import pydefuddle # pip install pydefuddle
import yaml # pip install pyyaml
import yagmail # pip install yagmail

# ----------------------------------------------------------------------------
# GLOBAL VARIABLES -----------------------------------------------------------
# ----------------------------------------------------------------------------
PROGRAM_NAME = "nodiffy"
__author__ = "Hussein Esmail"
__version__ = "0.1.0"
__email__ = "contact@husseinesmail.xyz"
SNAPSHOT_DIR = "snapshots" 
BOOL_PRINTS = True
EMAIL_FORMAT = "html"  # "html" or "text"
MAX_DIFF_LINES = 500
URLS = [] # Updated in main() via the urls.yaml file
EMAIL_ADDRESS_FROM = "" # Updated in main() via the secrets.yaml file
EMAIL_APPEARANCE = "" # Updated in main() via the secrets.yaml file
EMAIL_ADDRESS_FROM_PASSWORD = "" # Updated in main() via the secrets.yaml file


# ----------------------------------------------------------------------------
# FETCHING -------------------------------------------------------------------
# ----------------------------------------------------------------------------
def fetch_page_text(url: str) -> str:
    """Fetch a page and return its defuddled markdown."""
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; PageMonitor/1.0)"},
        timeout=30,
    )
    response.raise_for_status()

    html_content = response.text
    markdown = pydefuddle.defuddle(html=html_content, url=url).markdown
    if not markdown or not markdown.strip():
        raise ValueError(f"defuddle returned no content for {url}")
    return markdown


# ----------------------------------------------------------------------------
# FILE HELPERS ---------------------------------------------------------------
# ----------------------------------------------------------------------------
def read_txt(path: str) -> list[str]:
    """Read a .txt file as UTF-8 and return its lines without line endings."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def write_txt(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def snapshot_paths(url: str) -> tuple[str, str]:
    """Stable previous/current file paths for a URL."""
    slug = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return (
        os.path.join(SNAPSHOT_DIR, f"{slug}_previous.txt"),
        os.path.join(SNAPSHOT_DIR, f"{slug}_current.txt"),
    )


# ----------------------------------------------------------------------------
# DIFF + FORMATTING ----------------------------------------------------------
# ----------------------------------------------------------------------------
def make_diff(old_lines: list[str], new_lines: list[str],
              old_label: str, new_label: str, context: int = 3) -> list[str]:
    """Return unified diff lines (no trailing newlines)."""
    return list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=old_label,
            tofile=new_label,
            lineterm="",
            n=context,
        )
    )


def diff_stats(diff_lines: list[str]) -> tuple[int, int]:
    """Count added and removed lines, ignoring the ---/+++ headers."""
    added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
    return added, removed


def format_diff_text(diff_lines: list[str], max_lines: int = 500) -> str:
    added, removed = diff_stats(diff_lines)
    out = [f"Summary: +{added} added, -{removed} removed", "=" * 60, ""]
    out.extend(diff_lines[:max_lines])
    if len(diff_lines) > max_lines:
        out.append("")
        out.append(f"... diff truncated ({len(diff_lines) - max_lines} more lines) ...")
    return "\n".join(out)


def format_diff_html(diff_lines: list[str], max_lines: int = 500) -> str:
    styles = {
        "add": "background:#e6ffec;color:#116329;",
        "del": "background:#ffebe9;color:#82071e;",
        "hunk": "background:#ddf4ff;color:#0550ae;",
        "file": "color:#57606a;font-weight:bold;",
        "ctx": "color:#24292f;",
    }
    base = "margin:0;padding:0 8px;white-space:pre-wrap;word-break:break-word;"

    added, removed = diff_stats(diff_lines)
    rows = []
    for line in diff_lines[:max_lines]:
        if line.startswith(("---", "+++")):
            kind = "file"
        elif line.startswith("@@"):
            kind = "hunk"
        elif line.startswith("+"):
            kind = "add"
        elif line.startswith("-"):
            kind = "del"
        else:
            kind = "ctx"
        rows.append(f'<div style="{base}{styles[kind]}">{html.escape(line) or "&nbsp;"}</div>')

    if len(diff_lines) > max_lines:
        rows.append(
            f'<div style="{base}color:#57606a;font-style:italic;">'
            f"... diff truncated ({len(diff_lines) - max_lines} more lines) ...</div>"
        )

    return (
        '<div style="font-family:Segoe UI,Arial,sans-serif;">'
        f'<p><b>Summary:</b> <span style="color:#116329;">+{added}</span> / '
        f'<span style="color:#82071e;">-{removed}</span></p>'
        '<div style="font-family:Consolas,Menlo,monospace;font-size:13px;'
        'border:1px solid #d0d7de;border-radius:6px;padding:8px 0;overflow-x:auto;">'
        + "\n".join(rows)
        + "</div></div>"
    )


def build_email_body(
    url: str,
    old_file: str,
    new_file: str,
    fmt: str = "text",
    max_lines: int = 500,
) -> str | None:
    """Diff two .txt files and return the email body ("text" or "html"),
    or None if the files have identical content."""
    old_lines = read_txt(old_file)
    new_lines = read_txt(new_file)

    diff_lines = make_diff(
        old_lines, new_lines,
        old_label=f"{url} (previous)",
        new_label=f"{url} (current)",
    )
    if not diff_lines:
        return None

    old_file_ctime_obj = datetime.datetime.fromtimestamp(os.path.getmtime(old_file))
    old_file_ctime = old_file_ctime_obj.strftime("%Y %m %d (%a) %I:%M %p")
    old_file_time_since = str((datetime.datetime.today() - old_file_ctime_obj).days) + " days"

    if fmt == "html":
        return (
            f'<p>The content at <a href="{html.escape(url)}">{html.escape(url)}</a> '
            f"has changed since the last check ({old_file_ctime}, {old_file_time_since}).</p>"
            + format_diff_html(diff_lines, max_lines)
        )

    return (
        f"The content at {url} has changed since the last check.\n\n"
        + format_diff_text(diff_lines, max_lines)
    )


# def send_email(to, to_appearance, subject, message):
#     import yagmail
#     yag = yagmail.SMTP({EMAIL_ADDRESS_FROM: to_appearance}, EMAIL_ADDRESS_FROM_PASSWORD) # pyright: ignore[reportArgumentType]
#     yag.send(to, subject, message)


# ----------------------------------------------------------------------------
# MAIN CODE ------------------------------------------------------------------
# ----------------------------------------------------------------------------
def check_url(url: str, emails_to: list[str], fmt: str = EMAIL_FORMAT) -> None:
    with open("secrets.yaml") as f2:
        config_secrets = yaml.safe_load(f2)
    EMAIL_ADDRESS_FROM = str(config_secrets["EMAIL_ADDRESS_FROM"])
    EMAIL_APPEARANCE = str(config_secrets["EMAIL_APPEARANCE"])
    EMAIL_ADDRESS_FROM_PASSWORD = str(config_secrets["EMAIL_ADDRESS_FROM_PASSWORD"])
    previous_path, current_path = snapshot_paths(url) # Get the path names
    write_txt(current_path, fetch_page_text(url)) # Fetch and save the current version as a .txt file
    if not os.path.exists(previous_path): # First run: no baseline yet, so save it and stop
        os.replace(current_path, previous_path)
        print(f"[baseline saved] {url}")
        return
    body = build_email_body(url, previous_path, current_path, fmt=fmt, max_lines=MAX_DIFF_LINES) # Diff previous vs. current and build the body
    if body is None: # If no lines changed
        os.remove(current_path)
        if BOOL_PRINTS:
            print(f"[unchanged] {url}")
        return
    added, removed = diff_stats(make_diff(read_txt(previous_path), read_txt(current_path), "prev", "curr")) # Line number quantities
    # Changed: email first. if sending fails, the old baseline is kept and you'll be alerted next run)
    url_pretty = url.replace('https://', '').replace('http://', '')
    subject = f"Page changed: {url_pretty} (+{added}/-{removed})"
    for email_to_i in emails_to:
        yag = yagmail.SMTP({EMAIL_ADDRESS_FROM: EMAIL_APPEARANCE}, EMAIL_ADDRESS_FROM_PASSWORD) # pyright: ignore[reportArgumentType]
        yag.send(email_to_i, subject, body)
        if BOOL_PRINTS:
            print(f"[changed, emailed] {email_to_i} regarding {url_pretty}")
    os.replace(current_path, previous_path) # Promote current to previous for the next run
    

def main() -> None:
    with open("urls.yaml") as f1:
        config_urls = yaml.safe_load(f1)    
    URLS = [[t["url"], t["emails"]] for t in config_urls["targets"]]

    os.makedirs(SNAPSHOT_DIR, exist_ok=True) # exist_ok: Do nothing if the directory already exists (no error raised)
    for url in URLS:
        # url[0]: Website to watch
        # url[1]: List of emails to send changes to
        try:
            check_url(url[0], url[1])
        except Exception as e:
            # One bad site shouldn't stop the others
            print(f"[error] {url[0]}: {e}")


if __name__ == "__main__":
    main()