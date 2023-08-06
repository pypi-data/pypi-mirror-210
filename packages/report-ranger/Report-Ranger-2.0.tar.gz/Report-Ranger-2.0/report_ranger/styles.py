from secrets import choice
import string
import logging
import re

log = logging.getLogger(__name__)


def test_color(color):
    """ Return true if color is a hex color value such as a1b2c3"""
    return re.search("[0-9a-fA-F]{6}", color)


class TableStyles:
    def __init__(self):
        self.styles = {}
        self.aliases = {}

    def addstyle(self, name, options):
        """Add a style to the style list.

        Style options can include:
        - alias: 'alias'
        - color: 'color_name'
        - bgcolor: 'color_name'
        - bold: bool
        - italic: bool
        - uppercase: bool
        - alignment: l/left|c/center/centre|r/right
        """

        if 'alias' in options:
            self.aliases[options['alias']] = name

        defaults = {
            'bold': False,
            'italic': False,
            'uppercase': False,
            'alignment': '',
            'color': None,
            'bgcolor': None,
            'size': None
        }

        for default in defaults:
            if default not in options:
                options[default] = defaults[default]

        alignmentaliases = {
            'l': 'l', 'c': 'c', 'r': 'r',
            'left': 'l',
            'center': 'c',
            'centre': 'c',
            'right': 'r'
        }
        if options['alignment'] in alignmentaliases:
            options['alignment'] = alignmentaliases[options['alignment']]
        else:
            options['alignment'] = ''

        options['name'] = name

        self.styles[name] = options

    def addstyles(self, styles):
        for style in styles:
            self.addstyle(style)

    def getstyle(self, name):
        if type(name) is not str:
            return None
        if name in self.styles:
            return self.styles[name]
        if name in self.aliases:
            return self.styles[self.aliases[name]]
        return None

    def getstyles(self):
        return self.styles


class ColorList:
    def __init__(self):
        self.colors = {}

    def addcolor(self, name, color):
        if name != None:
            self.colors[name] = color
            return name
        else:
            # See if it's already there
            for c in self.colors:
                if self.colors[c] == color:
                    return c

            # Give it a random name
            newname = None
            while not newname or newname in self.colors:
                newname = ''.join(
                    [choice(string.ascii_letters) for _ in range(5)])
            self.colors[newname] = color
            return newname

    def addcolors(self, colors):
        for name in colors:
            self.colors[name] = colors[name]

    def getcolor(self, name):
        if name in self.colors:
            return self.colors[name]
        else:
            return None

    def getcolors(self):
        return self.colors
