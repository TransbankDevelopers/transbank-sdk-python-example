from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from django.utils.safestring import mark_safe
import json
import datetime
import decimal

register = template.Library()

FORMATTER = HtmlFormatter(cssclass="pygments")

@register.filter
def highlight_code(code, lang=""):
    if not code:
        return ""
    try:
        lexer = get_lexer_by_name(lang, stripall=False) if lang else guess_lexer(code)
    except Exception:
        try:
            lexer = guess_lexer(code)
        except Exception:
            from pygments.lexers.special import TextLexer
            lexer = TextLexer()
    html = highlight(code, lexer, FORMATTER)
    return mark_safe(html)

@register.filter(name="prettyjson")
def prettyjson(value, indent=2):
    def _default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        if isinstance(o, decimal.Decimal):
            return float(o)
        try:
            return o.__dict__
        except Exception:
            return str(o)

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, ensure_ascii=False, sort_keys=True, indent=int(indent))
        except Exception:
            return json.dumps(value, ensure_ascii=False, indent=int(indent))

    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=int(indent), default=_default)
    except Exception:
        return json.dumps(str(value), ensure_ascii=False, indent=int(indent))
