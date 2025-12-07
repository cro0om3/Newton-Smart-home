from typing import Dict, Any
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import base64
import mimetypes


def render_quotation_html(context: Dict[str, Any], template_name: str = "newton_quotation_individual.html") -> str:
    """Render the quotation HTML from given context and template.

    Args:
        context: Data dictionary to pass to the template.
        template_name: Template filename located in `templates/` folder.

    Returns:
        Rendered HTML as string.
    """
    templates_dir = Path(__file__).resolve().parents[1] / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Add a simple currency filter
    def _currency(value, symbol="AED", sep=","):
        try:
            # accept numbers or strings like '1,350.00' or 'AED 1,350.00'
            if isinstance(value, str):
                # strip common currency symbols and spaces
                cleaned = value.replace(symbol, '').replace(',', '').strip()
            else:
                cleaned = value
            v = float(cleaned)
        except Exception:
            return ""
        # Format with two decimals and thousands separator
        formatted = f"{v:,.2f}"
        return f"{symbol} {formatted}"

    env.filters['currency'] = _currency
    template = env.get_template(template_name)
    # Normalize item fields so template can rely on `description`, `qty`, `unit_price`, `total`, `warranty`, `image`
    items = context.get('items', []) or []
    normalized = []
    for it in items:
        if isinstance(it, dict):
            # description mapping (many possible source keys)
            description = (
                it.get('description') or it.get('Description') or it.get('name') or it.get('Product / Device') or it.get('Item')
            )
            # quantity mapping
            qty = (
                it.get('qty') if it.get('qty') is not None else (
                    it.get('Qty') or it.get('Quantity') or it.get('quantity') or 0
                )
            )
            # unit price mapping
            unit_price = (
                it.get('unit_price') if it.get('unit_price') is not None else (
                    it.get('Unit Price (AED)') or it.get('Unit Price') or it.get('unit_price_aed') or it.get('price') or 0
                )
            )
            # total mapping (fallback to qty * unit_price)
            total = (
                it.get('total') if it.get('total') is not None else (
                    it.get('Line Total (AED)') or it.get('Amount') or None
                )
            )
            if total is None:
                try:
                    total = float(qty or 0) * float(unit_price or 0)
                except Exception:
                    total = 0
            # warranty mapping
            warranty = it.get('warranty') or it.get('Warranty') or it.get('Warranty (Years)') or ''
            # image mapping (can be URL or data URI)
            image = it.get('image') or it.get('Image') or it.get('image_url') or it.get('img') or None

            # Normalize image to a data URI when possible:
            # - If it's already a data: URI or an http(s) URL, leave as-is
            # - If it's a filesystem path that exists, read and encode to data URI
            # - If it appears to be raw base64 (no spaces and reasonably long), prefix with image/png
            try:
                if isinstance(image, str) and image:
                    s = image.strip()
                    if s.startswith('data:') or s.startswith('http://') or s.startswith('https://'):
                        image = s
                    else:
                        # If it's a local file path, convert to data URI
                        if os.path.exists(s):
                            mime, _ = mimetypes.guess_type(s)
                            mime = mime or 'image/png'
                            with open(s, 'rb') as f:
                                b = f.read()
                            b64 = base64.b64encode(b).decode('ascii')
                            image = f"data:{mime};base64,{b64}"
                        else:
                            # Heuristic: if looks like base64 (long and no whitespace), assume raw base64
                            if len(s) > 100 and all(c.isalnum() or c in '+/=' for c in s.replace('\n','')):
                                image = f"data:image/png;base64,{s}"
                            else:
                                image = s
            except Exception:
                # On any failure keep original value
                pass

            normalized_item = dict(it)  # copy all original keys
            normalized_item.update({
                'description': description or '',
                'qty': qty or 0,
                'unit_price': unit_price or 0,
                'total': total,
                'warranty': warranty,
                'image': image,
            })
            normalized.append(normalized_item)
        else:
            normalized.append({'description': str(it), 'qty': 0, 'unit_price': 0, 'total': 0, 'warranty': '', 'image': None})
    context = dict(context)
    context['items'] = normalized

    # Compute subtotal if not provided: sum of item totals
    if 'subtotal' not in context or context.get('subtotal') in (None, ''):
        try:
            context['subtotal'] = sum(float(it.get('total', 0) or 0) for it in normalized)
        except Exception:
            context['subtotal'] = 0

    # Accept Installation value from context if provided; normalize keys
    if 'Installation' not in context and 'installation' in context:
        context['Installation'] = context.get('installation')

    # Compute total_amount if missing: subtotal + Installation (numeric)
    if 'total_amount' not in context or context.get('total_amount') in (None, ''):
        try:
            inst = float(context.get('Installation') or 0)
        except Exception:
            inst = 0
        try:
            subtotal_val = float(context.get('subtotal') or 0)
        except Exception:
            subtotal_val = 0
        context['total_amount'] = subtotal_val + inst

    html = template.render(**context)
    return html


def html_to_pdf(html_str: str, output_path: str | None = None) -> bytes:
    """Convert HTML string to PDF bytes using WeasyPrint.

    Args:
        html_str: HTML content to convert.
        output_path: Optional filesystem path to save the PDF. If not provided,
            the PDF bytes are returned and no file is written.

    Returns:
        PDF content as bytes.
    """
    # Preferred: use WeasyPrint (local). If unavailable, attempt ConvertAPI fallback
    try:
        from weasyprint import HTML
        if output_path:
            HTML(string=html_str).write_pdf(output_path)
            return Path(output_path).read_bytes()
        else:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            HTML(string=html_str).write_pdf(tmp_path)
            data = tmp_path.read_bytes()
            try:
                tmp_path.unlink()
            except Exception:
                pass
            return data
    except Exception:
        # Fallback: try ConvertAPI if the caller has set CONVERTAPI_SECRET env var
        import os
        key = os.environ.get("CONVERTAPI_SECRET")
        if not key:
            raise RuntimeError(
                "No local HTML->PDF converter available and CONVERTAPI_SECRET is not set.\n"
                "Install WeasyPrint locally OR set the environment variable CONVERTAPI_SECRET to use ConvertAPI as fallback."
            )
        try:
            import convertapi
            convertapi.api_credentials = key
            # converthtml via ConvertAPI: pass HTML as file by writing tmp .html
            with tempfile.TemporaryDirectory() as tmpdir:
                html_path = Path(tmpdir) / "temp.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_str)
                result = convertapi.convert(
                    'pdf',
                    {
                        'File': str(html_path),
                        'FileName': 'quotation'
                    },
                    from_format='html'
                )
                saved = result.save_files(tmpdir)
                if not saved:
                    raise RuntimeError('ConvertAPI returned no files')
                pdf_path = saved[0]
                with open(pdf_path, 'rb') as pf:
                    pdf_bytes = pf.read()
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(pdf_bytes)
                return pdf_bytes
        except Exception as e:
            raise RuntimeError("Failed to convert HTML to PDF (weasyprint missing and ConvertAPI fallback failed).") from e
