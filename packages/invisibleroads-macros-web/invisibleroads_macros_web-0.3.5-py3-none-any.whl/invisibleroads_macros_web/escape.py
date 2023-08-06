def escape_quotes_html(x):
    try:
        x = x.replace('"', '&#34;').replace("'", '&#39;')
    except AttributeError:
        pass
    return x


def escape_quotes_js(x):
    try:
        x = x.replace('"', '\\"').replace("'", "\\'")
    except AttributeError:
        pass
    return x
