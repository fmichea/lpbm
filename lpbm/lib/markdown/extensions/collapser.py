import re

import markdown.blockprocessors
import markdown.extensions
import markdown.util


_COLLAPSER_HEADER_RE = re.compile('^\s*:::lpbm:collapser:BEGIN(?P<label>.*)$')
_COLLAPSER_FOOTER_RE = re.compile('^\s*:::lpbm:collapser:END$')


class CollapserExtension(markdown.extensions.Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'output_html': [True, 'output HTML or just clean the tags.'],
        }
        super(CollapserExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        self.md, self.md_globals = md, md_globals
        self.md.registerExtension(self)
        self.md.parser.blockprocessors.add(
            'collapser',
            CollapserBlockProcessor(self),
            '_begin',
        )


class CollapserBlockProcessor(markdown.blockprocessors.BlockProcessor):
    def __init__(self, extension):
        super(CollapserBlockProcessor, self).__init__(extension.md.parser)
        self._extension = extension

    def test(self, parent, block):
        lines = block.splitlines()
        return lines and _COLLAPSER_HEADER_RE.match(lines[0]) is not None

    def run(self, parent, blocks):
        header, label, sub_blocks = None, None, []
        while True:
            try:
                block = blocks.pop(0).splitlines()
            except IndexError:
                raise ValueError('end tag for collapser block not found.')
            if header is None:
                header = _COLLAPSER_HEADER_RE.match(block.pop(0))
                label = header.group('label').strip()
            sub_blocks.append(block)
            if block and _COLLAPSER_FOOTER_RE.match(block[-1]) is not None:
                block.pop(-1)
                break
        sub_blocks = ['\n'.join(sub_block) for sub_block in sub_blocks]
        # Now create the block and parse the sub blocks.
        if self._extension.getConfig('output_html'):
            main_div = markdown.util.etree.SubElement(parent, 'div')
            main_div.set('class', 'panel panel-default')
            header_div = markdown.util.etree.SubElement(main_div, 'div')
            header_div.set('class', 'panel-heading lpbm-collapser-heading')
            if label:
                label_div = markdown.util.etree.SubElement(header_div, 'div')
                label_span = markdown.util.etree.SubElement(label_div, 'span')
                label_span.text = label
            # collaps/elapse button.
            colel_div = markdown.util.etree.SubElement(header_div, 'div')
            colel_div.set('class', 'lpbm-collapser-button')
            col_div = markdown.util.etree.SubElement(colel_div, 'div')
            col_div.set('class', 'lpbm-collapser-button-collapse')
            col_div.text = markdown.util.AtomicString('(collapse)')
            el_div = markdown.util.etree.SubElement(colel_div, 'div')
            el_div.set('class', 'lpbm-collapser-button-elapse')
            el_div.text = markdown.util.AtomicString('(elapse)')
            # Body of the collapseable.
            body_div = markdown.util.etree.SubElement(main_div, 'div')
            body_div.set('class', 'panel-body lpbm-collapser-body')
            self.parser.parseBlocks(body_div, sub_blocks)
            return blocks
        return sub_blocks + blocks


def makeExtension(*args, **kwargs):
    return CollapserExtension(*args, **kwargs)
