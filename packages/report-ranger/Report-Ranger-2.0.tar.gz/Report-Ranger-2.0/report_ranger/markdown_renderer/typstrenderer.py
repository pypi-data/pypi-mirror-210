import mistune
import re
import logging

log = logging.getLogger(__name__)


class TypstRenderer(mistune.HTMLRenderer):
    NAME = 'typst'
    IS_TREE = False
    ordered = False
    escape_text = False

    def escape(self, text):
        ''' Escape the given text for display in Typst output

        :param text: a plain text message
        :return: the message escaped to appear correctly in Typst
        '''
        conv = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '[': r'\[',
            ']': r'\]',
            '@': r'\@',
            '*': r'\*',
            '\\': r'\\'
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(
            conv.keys(), key=lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)



    def __init__(self, escape=True):
        super(TypstRenderer, self).__init__()
        self.escape_text = escape

    def text(self, text):
        return self.escape(text) if self.escape_text == True else text

    def link(self, link, text=None, title=None):
        if text is None or text == '':
            return f'#link("{link}")'

        return f'#link("{link}")[{text}]'

    def image(self, src, alt="", title=None):
        if alt != "":
            return f'#figure(image("{src}"), caption: [{alt}])'
        else:
            return f'#image("{src}")'

    def emphasis(self, text):
        return f'_{text}_'

    def strong(self, text):
        return f'*{text}*'

    def codespan(self, text):
        return self.block_code(text)

    def linebreak(self):
        return '\n\n'

    def inline_html(self, html):
        return html

    def paragraph(self, text):
        return text + '\n\n'

    def heading(self, text, level):
        return '=' * level + f' {text}\n\n'

    def newline(self):
        return '\n'

    def thematic_break(self):
        return ''

    def block_text(self, text):
        return text

    def block_code(self, code, info=None):
        return f'```\n{code}\n```'

    def block_quote(self, text):
        return text

    def block_html(self, html):
        return html

    def block_error(self, html):
        return html

    def list(self, text, ordered, level, start=None):
        self.ordered = ordered
        return f'{text}\n'

    def list_item(self, text, level):
        if self.ordered:
            return level*'+' + f' {text}\n'
        return level*'-' + f' {text}\n'
