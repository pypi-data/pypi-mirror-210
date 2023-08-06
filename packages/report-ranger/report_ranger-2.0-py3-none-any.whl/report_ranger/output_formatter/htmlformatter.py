from report_ranger.output_formatter.outputformatter import OutputFormatter
import yaml
import html
from report_ranger.table import Table
import logging
import subprocess

log = logging.getLogger(__name__)

default_html_headers = {'template': ''}

html_header_aliases = {
}


class HTMLFormatter(OutputFormatter):
    def __init__(self, templateheaders=dict(), timer=None, watcher=None):
        OutputFormatter.__init__(self, templateheaders, timer, watcher=watcher)
        self.templatefile = self.templateheaders['html_template']
        self.figformat = "svg"

    def escape(self, text):
        ''' Escape the given text based on the format we're working with

        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
        '''
        return html.escape(text)

    def table(self, table, options={}, **tableargs):
        ''' This function formats the table in either latex or markdown, depending on the output. '''
        markdown = ""

        t = Table(table, env=self.env, **tableargs)

        markdown += "<table>"
        for i in range(len(t.table)):
            markdown += "\n<tr>"
            for j in range(len(t.table[i])):
                attrs = ""
                if t.colspan[i][j] < 1 or t.rowspan[i][j] < 1:
                    continue
                if t.colspan[i][j] > 1:
                    attrs += " colspan={}".format(t.colspan[i][j])
                if t.rowspan[i][j] > 1:
                    attrs += " rowspan={}".format(t.rowspan[i][j])
                if t.cellstyles[i][j] != '':
                    attrs += " class='{}'".format(t.cellstyles[i][j])

                # cell alignment, first try cellalign then colalign
                if t.cellalign[i][j] != '':
                    alignment = t.cellalign[i][j]
                elif t.colalign[j] != '':
                    alignment = t.colalign[j]
                else:
                    alignment = ''

                if alignment != '':
                    if alignment == 'l':
                        attrs += " style='text-align: left'"
                    elif alignment == 'c':
                        attrs += " style='text-align: center'"
                    elif alignment == 'r':
                        attrs += " style='text-align: right'"
                    elif alignment == 'j':
                        attrs += " style='text-align: justified'"

                markdown += "<td{}>{}</td>".format(attrs,
                                                   self.escape(str(t.table[i][j])))
            markdown += "</tr>"
        markdown += "</table>"
        return markdown

    def headers(self):
        markdown = ''
        headers = dict()
        headers['title'] = '{{title}}'
        headers['date'] = '{{date.strftime("%-d %B %Y")}}'

        # Put in the defaults for the latex template
        headers.update(default_html_headers)

        if "html" in self.template:
            for header in html_header_aliases.keys():
                if header in self.template['html']:
                    self.template['html'][html_header_aliases[header]
                                          ] = self.template['html'][header]
                    del self.template['html'][header]

            headers.update(self.template['html'])

        # Overwrite the headers with the report headers if they are set
        htmlheaders = self.env.get("html")
        if htmlheaders != None:
            for header in html_header_aliases.keys():
                if header in htmlheaders:
                    htmlheaders[html_header_aliases[header]
                                ] = htmlheaders[header]
                    del htmlheaders

            headers.update(htmlheaders)

        markdown += yaml.dump(headers)
        return markdown

    def output(self, markdown, outputfile=''):
        output = self._build_markdown(markdown)

        log.info("Writing HTML")

        # Use Pandoc to print to PDF
        pandoc_arguments = ['pandoc', '--from', 'markdown', '--to', 'html',
                            '--template', self.templatefile, '--listings', '-o', outputfile]
        log.info("Running pandoc with arguments {}".format(pandoc_arguments))
        process = subprocess.run(pandoc_arguments,
                                 input=output,
                                 universal_newlines=True)

        return output
