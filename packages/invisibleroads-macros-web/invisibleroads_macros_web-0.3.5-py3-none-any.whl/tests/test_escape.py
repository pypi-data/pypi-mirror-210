from invisibleroads_macros_web.escape import (
    escape_quotes_html,
    escape_quotes_js)


def test_escape_quotes_html():
    assert escape_quotes_html(1) == 1
    assert escape_quotes_html('"' + "'") == '&#34;&#39;'


def test_escape_quotes_js():
    assert escape_quotes_js(1) == 1
    assert escape_quotes_js('"' + "'") == '\\"' + "\\'"
