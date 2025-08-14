from django import template
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from django.utils.safestring import mark_safe

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

def pygments_css(selector=".pygments", style="default"):
	formatter = HtmlFormatter(cssclass=selector.lstrip("."), style=style)
	return formatter.get_style_defs(selector)
