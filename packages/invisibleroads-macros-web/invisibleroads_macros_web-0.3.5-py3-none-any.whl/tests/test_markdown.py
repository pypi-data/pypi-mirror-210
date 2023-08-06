from invisibleroads_macros_web.markdown import (
    get_html_from_markdown,
    remove_parent_paragraphs,
    remove_single_paragraph)


def test_get_html_from_markdown():
    html = get_html_from_markdown('x')
    assert html == '<p>x</p>'


def test_remove_single_paragraph():
    html = remove_single_paragraph('<p>x\ny</p>')
    assert html == 'x\ny'
    html = remove_single_paragraph('<p>x</p><p>y</p>')
    assert html == '<p>x</p><p>y</p>'


def test_remove_parent_paragraphs():
    html = remove_parent_paragraphs(
        '<p>x</p><p><button>\n</button></p><p>x</p>')
    assert html == '<p>x</p><button>\n</button><p>x</p>'
    html = remove_parent_paragraphs('<p><span>\n</span></p>', tags=[])
    assert html == '<p><span>\n</span></p>'
    html = remove_parent_paragraphs('<p><span>\n</span></p>', tags=['span'])
    assert html == '<span>\n</span>'
