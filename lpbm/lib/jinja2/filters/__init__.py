import lpbm.tools

from lpbm.lib.jinja2.filters.markdown import do_markdown  # noqa


def do_sorted(value):
    return sorted(value)


def do_slugify(value):
    return lpbm.tools.slugify(value)
