from lpbm.models.articles import translate_to_jekyll_markdown


def test_collapsers_are_just_removed():
    inp = '''
there is some text before the collapser.

:::lpbm::collapser::BEGIN
    some text here
:::lpbm::collapser::END

and some text after.
'''

    out = '''
there is some text before the collapser.

    some text here

and some text after.
'''

    assert translate_to_jekyll_markdown(inp) == out


def test_code_blocks_are_translated():
    inp = '''
there is some text before first code block

    this is a small
    code block

now some other text is added

    :::c
    int main = 0;

then we need to test a code block with middle lines

    :::python
    def code_here():
        a = 1

        if a != 0:
            a = 2

        b = 2
        return a - b

and some final text
'''

    out = '''
there is some text before first code block

    this is a small
    code block

now some other text is added

```c
int main = 0;
```

then we need to test a code block with middle lines

```python
def code_here():
    a = 1

    if a != 0:
        a = 2

    b = 2
    return a - b
```

and some final text
'''

    assert translate_to_jekyll_markdown(inp) == out
