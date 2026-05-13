import io
import zipfile


def inline_report(html: str, tables_js: str, metadata_js: str) -> str:
    html = html.replace(
        '<script src="javascript/metadata.js"></script>',
        f"<script>{metadata_js}</script>",
    )
    html = html.replace(
        '<script src="javascript/tables.js"></script>',
        f"<script>{tables_js}</script>",
    )
    return html


def bundle_zip(name: str, html: str, tables_js: str, metadata_js: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{name}/{name}.html", html)
        z.writestr(f"{name}/javascript/tables.js", tables_js)
        z.writestr(f"{name}/javascript/metadata.js", metadata_js)
    return buf.getvalue()
