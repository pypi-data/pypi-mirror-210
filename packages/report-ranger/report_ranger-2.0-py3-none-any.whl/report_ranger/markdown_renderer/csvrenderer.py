import mistune
import re


class CSVRenderer(mistune.HTMLRenderer):
    NAME = 'csv'
    IS_TREE = False

    # This set of data structures is a bit 'special'.
    #
    # We want the template to be able to refer to headings and get all the text from under that header. Usually you could do this with a tree, but
    # I chose a different way here. Instead of a tree, it has a dict and a list. The dict gives the headings from every level and the list gives the current
    # headings in play. When the renderer gets a new piece of text, it adds it to all the headings currently in play. This means it's very easy to get
    # and refer to all the text from the headings without having to traverse a tree.

    def _add_text(self, text):

        for heading in self.heading_levels:
            if heading != '' and heading in self.heading_text:
                self.heading_text[heading] += text

    def heading(self, text, level):
        # This is brought to the top as it relates to the above heading structures

        if len(self.heading_levels) < level:
            self.heading_levels += [''] * \
                (level - len(self.heading_levels)) + [text]
        else:
            self.heading_levels = self.heading_levels[:level - 1] + [text]

        for heading in self.heading_levels[-1:]:
            if heading != '' and heading in self.heading_text:
                self.heading_text[heading] += '#' * level + ' ' + text

        self.heading_text[text] = ''

        return '#' * level + ' ' + text

    def __init__(self, escape=True):
        self.heading_levels = []  # The current headings in play
        self.heading_text = {}  # The current heading text
        super(CSVRenderer, self).__init__()

    def text(self, text):
        return text

    def link(self, link, text=None, title=None):
        self._add_text(text)
        return text

    def image(self, src, alt="", title=None):
        self._add_text(alt)
        return alt

    def emphasis(self, text):
        self._add_text(text)
        return text

    def strong(self, text):
        self._add_text(text)
        return text

    def codespan(self, text):
        self._add_text(text)
        return text

    def linebreak(self):
        self._add_text('\n\n')
        return '\n\n'

    def inline_html(self, html):
        self._add_text(self._escape_csv(html))
        return self._escape_csv(html)

    def paragraph(self, text):
        self._add_text(text + '\n\n')
        return text + '\n\n'

    def newline(self):
        self._add_text('\n\n')
        return '\n\n'

    def thematic_break(self):
        # TODO NO THEMATIC BREAK
        return '\n\n'

    def block_text(self, text):
        return text

    def block_code(self, code, info=None):
        return code

    def block_quote(self, text):
        return text

    def block_html(self, html):
        return html

    def block_error(self, html):
        return html

    def list(self, text, ordered, level, start=None):
        return text

    def list_item(self, text, level):
        return '  ' * level + '- ' + text + '\n'
