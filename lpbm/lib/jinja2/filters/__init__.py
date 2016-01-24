from lpbm.lib.slugify import slugify as _slugify

from lpbm.lib.jinja2.filters.markdown import do_markdown  # noqa


def do_sorted(value):
    return sorted(value)


def do_slugify(value):
    return _slugify(value)
