import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


def normalize_newlines(text):
    """Normalize CRLF and CR newlines to just LF."""
    return re.sub("\r\n|\r", "\n", text)


def linebreaks(value):
    """Convert newlines into <p> and <br>s."""
    value = normalize_newlines(value)
    paras = re.split('\n{2,}', str(value))
    paras = ['<p>%s</p>' % p.replace('\n', '<br>') for p in paras]
    return '\n\n'.join(paras)


@register.filter
@stringfilter
def linebreaks_ignoring_pre(string):
    """Replace line breaks in plain text with appropriate HTML, ignoring <pre> elements

    This template tag is similar to the built-in linebreaks tag.
    The issue with the built-in tag is that is converts line breaks (\r\n, \r) everywhere, including inside <pre>
    elements. This behavior can break the presentation of <pre> elements when using certain syntax highlighters
    such as Prism.js, since we're expecting conventional line breaks there, instead of <p> or <br> html elements.

    This tag is similar to the built in one with the exception that it simply ignores content inside <pre></pre>.
    """

    # Find <pre>...</pre> matches in the original text and store them.
    pattern = r'(<pre>(.|\s)*?</pre>)'
    pre_matches = [x.group() for x in re.finditer(pattern, string)]

    # Normalize newlines in the original text (i.e. replace all line breaks with \n).
    string_normalized = normalize_newlines(string)

    # Convert \n\n and \n linebreaks to <p> and <br> html elements, respectively.
    string_with_html_linebreaks = linebreaks(string_normalized)

    # Replace <pre>...</pre> matches in new text with old stored matches (without html line breaks)
    result = re.sub(pattern, lambda _: pre_matches.pop(0), string_with_html_linebreaks, len(pre_matches) or -1)

    return result
