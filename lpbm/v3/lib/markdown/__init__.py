import markdown


def extract_title(filename):
    with open(filename) as fd:
        return fd.readline().strip()


def do_markdown(text, code=True):
    if not code:
        tmp = text.splitlines()
        for idx, line in enumerate(tmp):
            if line.startswith('\t:::') or line.startswith('    :::'):
                tmp[idx] = ''
        text = '\n'.join(tmp)
        return markdown.markdown(text, extensions=[
            'lpbm.v3.lib.markdown.extensions.collapser(output_html=False)',
        ])
    return markdown.markdown(text, extensions=[
        'lpbm.v3.lib.markdown.extensions.collapser',
        'markdown.extensions.codehilite(linenums=True)',
    ])
