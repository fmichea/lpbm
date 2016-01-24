import pytest

import lpbm.lib.slugify as mod


@pytest.mark.parametrize('text,slug', [
    ('Foo Bar!', 'foo-bar'),
    ('Étape 1: YEAH!', 'etape-1-yeah'),
])
def test_slugify(text, slug):
    assert mod.slugify(text) == slug
