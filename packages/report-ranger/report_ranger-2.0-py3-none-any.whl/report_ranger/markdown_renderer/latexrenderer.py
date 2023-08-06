import mistune
import re
import logging

log = logging.getLogger(__name__)


class LatexTableRenderer(mistune.HTMLRenderer):
    NAME = 'latex'
    IS_TREE = False

    def _escape_latex(self, text):
        ''' Escape the given text for display in Latex output

        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
        '''
        conv = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'{\textasciitilde}',
            '^': r'\^',
            '\\': r'{\textbackslash}',
            '<': r'{\textless}',
            '>': r'{\textgreater}',
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(
            conv.keys(), key=lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)

    def _escape_latex_codespan(self, text):
        ''' Escape the given text for codespans in latex. This has different rules to elsewhere.
        '''
        sepchar = None
        for char in "!\"'()*,-./:;_":
            if char not in text:
                sepchar = char
                break
        if not sepchar:
            return None
        conv = {
            '&': r'\&',
            '%': r'\%',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\~',
            '\\': r'\\\\'
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(
            conv.keys(), key=lambda item: - len(item))))
        return sepchar + regex.sub(lambda match: conv[match.group()], text) + sepchar

    def __init__(self, escape=True):
        super(LatexTableRenderer, self).__init__()
        self._escape = escape

    def text(self, text):
        return self._escape_latex(text)

    def link(self, link, text=None, title=None):
        if text is None or text == '':
            return '\\url{{{}}}'.format(self._escape_latex(link))

        s = '\\href{' + \
            self._escape_latex(link) + '}{' + self._escape_latex(text) + '}'
        return s

    def image(self, src, alt="", title=None):
        s = '\\begin{{figure}}'
        s += '\\centering'
        s += '\\includegraphics{{{}}}}'.format(self._escape_latex(src))
        s += '\\caption{{{}}}'.format(self._escape_latex(alt))
        s += '\\end{{figure}}'
        return s

    def emphasis(self, text):
        return '\\emph{' + text + '}'

    def strong(self, text):
        return '\\textbf{' + text + '}'

    def codespan(self, text):
        code = '\\passthrough{\\lstinline' + \
            self._escape_latex_codespan(text) + '}'
        if code != None:
            return code
        return self.block_code(text)

    def linebreak(self):
        return ' \\\\ '

    def inline_html(self, html):
        return self._escape_latex(html)

    def paragraph(self, text):
        return text + ' \\\\ '

    def heading(self, text, level):
        # TODO DOES NOT PROPERLY DO HEADINGS
        return text

    def newline(self):
        return ''

    def thematic_break(self):
        # TODO NO THEMATIC BREAK
        return ''

    def block_text(self, text):
        return text

    def block_code(self, code, info=None):
        code = code.replace('\n', '^^J\n')
        code = code.replace('{', '\{')
        code = code.replace('}', '\}')
        return f"""\\begin{{lstlisting}}^^J
{code}^^J\\end{{lstlisting}}"""

    def block_quote(self, text):
        return text

    def block_html(self, html):
        return html

    def block_error(self, html):
        return html

    def list(self, text, ordered, level, start=None):
        if ordered:
            return "\n\\begin{{enumerate}}\n{}\\end{{enumerate}}".format(text)
        else:
            return "\n\\begin{{varwidth}}[t]{{\\linewidth}}\n\\begin{{itemize}}[topsep = 0pt, parsep = 0pt]\n{}\\strut\\end{{itemize}}\end{{varwidth}}\n".format(text)

    def list_item(self, text, level):
        return " \item {}\n".format(text)
