from report_ranger.output_formatter.outputformatter import OutputFormatter, headeralias
import re
import os
import yaml
import jinja2
import mistune
from report_ranger.markdown_renderer.latexrenderer import LatexTableRenderer
from report_ranger.table import Table
import subprocess
import logging
from report_ranger.utils.mdread import process_template


log = logging.getLogger(__name__)

default_latex = {'title': '{{title}}',
                 'author': '[Author Name]',
                 'date': '{{date.strftime("%-d %B %Y")}}',
                 'subtitle': 'Prepared for {% if longclient %}{{longclient}}{% else %}{{client}}{% endif %}',
                 'template': '',
                 'lang': 'en',
                 'twoside': False,
                 'numbersections': False,
                 'titlepage': True,
                 'titlepage-text-color': '000000',
                 'titlepage-rule-height': 0,
                 'titlepage-background': 'titlepage.pdf',
                 'page-background': '',
                 'page-background-opacity': 1.0,
                 'section-background': '',
                 'section-skip': '0pt',
                 'toc': True,
                 'toc-title': 'Table of Contents',
                 'toc-own-page': True,
                 'toc-depth': 2,
                 'color-table-header': 'C72727',
                 'color-table-1': 'FFFFFF',
                 'color-table-2': 'FFFFFF',
                 'color-informational': '3366FF',
                 'color-low': 'D3EAF9',
                 'color-medium': 'FFFF00',
                 'color-high': 'FF0000',
                 'color-high-font': '000000',
                 'color-critical': '000000',
                 'color-open': 'E47676',
                 'color-open-font': '000000',
                 'color-closed': 'A9DA74',
                 'color-closed-font': '000000',
                 'color-theme': 'C72727',
                 'toc-section': True,
                 'table-styles': ''}

header_aliases = {
    'titlepage-text-colour': 'titlepage-text-color',
    'titlepage-rule-colour': 'titlepage-rule-color',
    'colour-table-header': 'color-table-header',
    'colour-table-1': 'color-table-1',
    'colour-table-2': 'color-table-2',
    'colour-informational': 'color-informational',
    'colour-informational-font': 'color-informational-font',
    'colour-low': 'color-low',
    'colour-low-font': 'color-low-font',
    'colour-medium': 'color-medium',
    'colour-medium-font': 'color-medium-font',
    'colour-high': 'color-high',
    'colour-high-font': 'color-high-font',
    'colour-critical': 'color-critical',
    'colour-critical-font': 'color-critical-font',
    'colour-theme': 'color-theme'
}

latex_default_table_options = {
    'fullwidth': True,
    'vlines': True,
    'hlines': True,
    'color-1': 'color-table-1',
    'color-2': 'color-table-2',
    'banding': True,
    'longtable': True,
    'rowhead': 1
}


def stripmdpara(text):
    if text[-4:] == ' \\\\ ':
        return text[:-4]
    else:
        return text


class LatexFormatter(OutputFormatter):
    def __init__(self, templateheaders=dict(), timer=None, watcher=None):
        OutputFormatter.__init__(self, templateheaders, timer, watcher=watcher)
        self.templatefile = self.templateheaders['latex_template']
        self.figformat = "pdf"

        # Set up latex file headers
        latexheaders = dict()

        # Put in the defaults for the latex template
        latexheaders.update(default_latex)

        # Update latex headers with what's in the template
        if "latex" in templateheaders:
            for header in header_aliases.keys():
                if header in templateheaders['latex']:
                    templateheaders['latex'][header_aliases[header]
                                           ] = templateheaders['latex'][header]
                    del templateheaders['latex'][header]

            latexheaders.update(templateheaders['latex'])

        if ('header-left' in latexheaders and latexheaders['header-left'] != '') or ('header-center' in latexheaders and latexheaders['header-center'] != '') or ('header-right' in latexheaders and latexheaders['header-right'] != ''):
            latexheaders['has-header'] = 'true'

        # Add the toc-section if there's a section
        if latexheaders['toc-section']:
            latexheaders['toc-section'] = self.newsection()
        else:
            latexheaders['toc-section'] = False

        # Add over the headers that refer to local files
        for header in ['titlepage-background', 'page-background']:
            if header in latexheaders:
                latexheaders[header] = os.path.join(
                    self.templateheaders['templatedir'], latexheaders[header])

        # Set the default table options
        self.default_table_options = latex_default_table_options

        colors = ''
        colorlist = self.colors.getcolors()
        for name, color in colorlist.items():
            colors += '\\definecolor{{rrcolor{}}}{{HTML}}{{ {} }}\n'.format(
                name, color)
        if colors != '':
            latexheaders['colors'] = colors

        # Address if there are custom table styles
        if not latexheaders['table-styles']:
            tablestyles = ''
            ts = self.tablestyles.getstyles()
            for name, style in ts.items():
                log.info("Adding style {}".format(name))

                textcolor = ''
                if style['color']:
                    textcolor = "\\textcolor{{rrcolor{}}}".format(
                        style['color'])

                cellcolor = ''
                if style['bgcolor']:
                    cellcolor = '\\cellcolor{{rrcolor{}}} '.format(
                        style['bgcolor'])
                bold = ''
                if style['bold'] == True:
                    bold = '\\bfseries '

                if style['size']:
                    s = style['size']
                    sizes = {
                        'tiny': '\\tiny',
                        'small': '\\small',
                        'normal': '',
                        'large': '\\large',
                        'Large': '\\Large',
                        'LARGE': '\\LARGE',
                        'huge': '\\huge',
                        'Huge': '\\Huge'
                    }
                    if s in sizes:
                        size = sizes[s]
                else:
                    size = ''

                if style['uppercase']:
                    uppercase = '\\MakeUppercase{{{} #1 }}'.format(size)
                else:
                    uppercase = '{} #1'.format(size)

                tablestyles += "\\newcommand*{{\\rrts{}}}[1]{{ {{ {} {} {{ {} {} }} }} }}\n".format(
                    name,
                    cellcolor,
                    textcolor,
                    bold,
                    uppercase
                )
            latexheaders['table-styles'] = tablestyles
        else:
            log.info("NO TABLE STYLES: {}".format(
                latexheaders['table-styles']))
            log.info("NO TABLE STYLES: {}".format(
                latexheaders))

        if 'default-table-options' in latexheaders:
            if type(latexheaders['default-table-options']) is dict:
                # Overlay the template defaults
                self.default_table_options.update(
                    latexheaders['default-table-options'])
            else:
                log.warn(
                    "default-table-options variable in the latex headers is not a dict, ignoring")

        self.latexheaders = latexheaders

    def escape(self, text):
        ''' Escape the given text based on the format we're working with

        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
        '''
        if type(text) is not str:
            log.warning(
                "escape function given {} which is not a string. Returning ''".format(text))
            return ""

        conv = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
            '<': r'\textless{}',
            '>': r'\textgreater{}',
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(
            conv.keys(), key=lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)

    def table(self, table, options={}, **tableargs):
        ''' This function formats the table in either latex or markdown, depending on the output. '''
        markdown = ""

        opts = self.default_table_options.copy()
        opts.update(options)

        t = Table(table, env=self.env, **tableargs)

        toptions = []
        if opts['vlines']:
            if 'vlines-options' in opts:
                toptions.append(f"vlines = {opts['vlines-options']}")
            else:
                toptions.append("vlines")
                
        if opts['hlines']:
            if 'hlines-options' in opts:
                toptions.append(f"hlines = {opts['hlines-options']}")
            else:
                toptions.append("hlines")
        if opts['rowhead'] > 0 and len(t.table) > 1:
            toptions.append("rowhead = {}".format(opts['rowhead']))

        # If there's no actual table, warn and exit
        if t.width == 0:
            log.warn("Table is now empty. Printing an empty string.")
            return ""

        lr = mistune.create_markdown(renderer=LatexTableRenderer())

        if opts['banding']:
            toptions.append("row{{odd}} = {{bg={}}}".format(opts['color-1']))
            toptions.append("row{{even}} = {{bg={}}}".format(opts['color-2']))

        colspec = []
        for c in range(len(t.table[0])):
            col = ''
            if opts['fullwidth']:

                copts = []

                if tableargs.get('colwidths'):
                    if t.colwidths[int(c)] == 0:
                        col += 'Q'
                    else:
                        col += 'X'
                        copts.append(str(t.colwidths[int(c)]))
                else:
                    col += 'X'
                if t.colalign[c] != "":
                    copts.append(t.colalign[c])

                if len(copts) > 0:
                    col += "[{}]".format(",".join(copts))
            else:
                if t.colalign[c] != "":
                    col = t.colalign[c]
                else:
                    col = 'l'

            colspec.append(col)

        toptions.append("colspec={{{}}}".format("".join(colspec)))
        if opts['longtable']:
            # Hack to remove header caption
            if 'headerhack' in opts and opts['headerhack']:
                markdown += "\\vspace{{-1.5\\baselineskip}}"
            markdown += "\\SetTblrTemplate{{head}}{{empty}}".format()
            markdown += "\\begin{{longtblr}}{{ {} }} \n".format(
                ",".join(toptions))
        else:
            markdown += "\\begin{{tblr}}{{ {} }} \n".format(",".join(toptions))

        for i in range(len(t.table)):
            for j in range(len(t.table[i])):
                style = self.tablestyles.getstyle(t.cellstyles[i][j])
                if j > 0:
                    markdown += ' & '

                if t.colspan[i][j] < 1:  # This column is being overwritten in some way
                    continue
                if t.rowspan[i][j] < 1:  # This column is being overwritten in some way
                    continue

                mr = []
                # Multi-column
                if t.colspan[i][j] > 1:
                    mr.append("c={}".format(t.colspan[i][j]))

                # Multi-row
                if t.rowspan[i][j] > 1:
                    mr.append("r={}".format(t.rowspan[i][j]))

                mrspec = "" if len(mr) == 0 else "[{}]".format(",".join(mr))

                cellopts = []

                # cell alignment, first try cellalign, then style
                if t.cellalign[i][j] != '':
                    cellopts.append("halign={}".format(t.cellalign[i][j]))
                elif style and style['alignment'] != '':
                    cellopts.append("halign={}".format(style['alignment']))

                cellinit = ''
                if style:
                    if style['color']:
                        cellopts.append("fg=rrcolor{}".format(style['color']))
                    if style['bgcolor']:
                        cellopts.append(
                            "bg=rrcolor{}".format(style['bgcolor']))
                    if style['bold']:
                        cellinit += "\\bfseries "
                    if style['italic']:
                        cellinit += "\\itshape "

                    if style['size']:
                        s = style['size']
                        sizes = {
                            'tiny': '\\tiny',
                            'small': '\\small',
                            'normal': '',
                            'large': '\\large',
                            'Large': '\\Large',
                            'LARGE': '\\LARGE',
                            'huge': '\\huge',
                            'Huge': '\\Huge'
                        }
                        if s in sizes:
                            cellinit += sizes[s]
                elif t.cellstyles[i][j] != '':
                    if t.cellstyles[i][j] in headeralias:
                        t.cellstyles[i][j] = headeralias[t.cellstyles[i][j]]

                if len(mr) > 0 or len(cellopts) > 0:
                    markdown += "\\SetCell{}{{{}}}".format(
                        mrspec, ",".join(cellopts))

                cell = t.table[i][j]

                # If we've got a split box
                if(isinstance(cell, list)) and not isinstance(cell, str):
                    if len(cell) > 1:
                        markdown += "\\diagbox{{{} {} }}{{{} {} }}".format(cellinit, stripmdpara(lr(
                            str(cell[0]))), cellinit, stripmdpara(lr(str(cell[1]))))
                    else:
                        markdown += "{{{} {} }}".format(cellinit,
                                                        stripmdpara(lr(str(cell[0]))))
                else:
                    celltext = stripmdpara(lr(str(cell)))
                    markdown += "{{{} {} }}".format(cellinit, celltext)

            markdown += " \\\\ \n"

        if opts['longtable']:
            markdown += "\\end{longtblr}\n"
        else:
            markdown += "\\end{tblr}\n"
        return markdown

    def newsection(self):
        if "newsection-content" in self.templateheaders['latex']:
            output = process_template(
                [], self.templateheaders['latex']['newsection-content'], env=self.env, name="section", filename="")
            return output
        markdown = '\\newpage\n'
        if "section-background" in self.templateheaders['latex']:
            markdown += '\\begin{tikzpicture}[remember picture,overlay]\n'
            markdown += '\\node[inner sep=0] at (current page.center)\n'
            markdown += '{\\includegraphics[width=\\paperwidth,height=\\paperheight]{' + os.path.join(
                self.templateheaders['templatedir'], self.templateheaders['latex']["section-background"]) + '}};\n'
            markdown += '\\end{tikzpicture}\n'
            if "section-skip" in self.templateheaders['latex']:
                markdown += '\\vskip {}\n'.format(
                    self.templateheaders['latex']['section-skip'])
            else:
                markdown += '\\vskip 14em\n'
        return markdown

    def newpage(self):
        return "\\pagebreak"
    
    def _process_template_headers(self, header, headername, env):
        if type(header) == str:
            # Run a jinja template if it's a string
            try:
                j2template = jinja2.Template(header)
                return j2template.render(env)
            except jinja2.exceptions.TemplateSyntaxError as error:
                log.error(f"Error in processing template header {headername}: {error.message}")
                log.error(f"Header contents: {header}")
                log.error(f"Returning unprocessed header")
                return header
            except jinja2.exceptions.TemplateError as error:
                log.error(f"Error in processing template header {headername}: {error.message}")
                log.error(f"Returning unprocessed header")
                return header
        if type(header) == list:
            # If it's a list, rerun on each element of the list
            return [self._process_template_headers(headervalue, headername, env) for headername, headervalue in enumerate(header)]
        if type(header) == dict:
            # If it's a dict, rerun on each element of the dict
            return {headername: self._process_template_headers(headervalue, headername, env) for headername, headervalue in header.items()}
        # If it's anything else (number, date, etc), just return it blank.
        return header
                



    def headers(self):
        
        env = self.env.get_env()

        markdown = yaml.dump(self._process_template_headers(self.latexheaders, "headers", env))
        return markdown

    def end(self):
        if "endpage-content" in self.templateheaders['latex']:
            output = process_template(
                [], self.templateheaders['latex']['endpage-content'], env=self.env, name="endpage", filename="")
            return output
        else:
            markdown = '\\newpage\n'
            """ To be called at the end of the output - puts in the ending page/graphics """
            markdown = ''
            markdown += '\\pagebreak\n'
            markdown += '\\thispagestyle{empty}\n'
            markdown += '\\NoBgThispage\n'
            markdown += '\\begin{tikzpicture}[remember picture,overlay]\n'
            markdown += '\\node[inner sep=0] at (current page.center)\n'
            markdown += '{\\includegraphics[width=\\paperwidth,height=\\paperheight]{' + os.path.join(
                self.templateheaders['templatedir'], self.templateheaders['latex']['titlepage-background']) + '}};\n'
            markdown += '\\end{tikzpicture}\n'
            markdown += '\\vskip 14em\n'
            return markdown

    def output(self, markdown, outputfile=''):
        output = self._build_markdown(markdown)

        if self.docformat and self.docformat != 'pdf':
            log.info("Writing Markdown")
            with open(outputfile, 'w') as fh:
                fh.write(output)
            log.info("Finished writing")

            return output

        log.info("Writing PDF")
        log.info(f"Latex template file: {self.templatefile}")
        log.info(f"Output file: {outputfile}")
        # Use Pandoc to print to PDF
        pandoc_arguments = ['pandoc', '--from', 'markdown', '--to', 'latex',
                            '--template', self.templatefile, '--listings', '-o', outputfile]
        if self.options and 'latex_numbered-headers' in self.options and self.options['latex_numbered-headers']:
            pandoc_arguments.append('--number-sections')
        process = subprocess.run(pandoc_arguments,
                                 input=output,
                                 universal_newlines=True)

        return output
