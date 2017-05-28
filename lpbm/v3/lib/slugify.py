import string
import unicodedata

SLUG_CHARS_DISPLAY = '[a-z0-9-]'


_SLUG_CHARS = string.ascii_lowercase + string.digits + '-'
_SLUG_SIZE = 80


def slugify(text):
    '''Returns the slug of a string (that can be used in an URL for example.'''
    slug = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    slug = slug.decode('utf-8').lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c in _SLUG_CHARS)
    return slug[:_SLUG_SIZE]
