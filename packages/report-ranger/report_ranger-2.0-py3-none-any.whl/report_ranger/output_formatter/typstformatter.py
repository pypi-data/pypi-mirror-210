import os
import shutil
from report_ranger.output_formatter.outputformatter import OutputFormatter, headeralias
import re
import jinja2
import mistune
from report_ranger.markdown_renderer.typstrenderer import TypstRenderer
from report_ranger.table import Table
import logging
from report_ranger.utils.jinja_helpers import log_jinja2_error
from report_ranger.utils.mdread import process_template


log = logging.getLogger(__name__)

class TypstFormatter(OutputFormatter):
    def __init__(self, templateheaders=dict(), timer=None, watcher=None):
        OutputFormatter.__init__(self, templateheaders, timer, watcher=watcher)
        self.figformat = "svg"
        self.env.set_static('table', self._register_table)

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
            '[': r'\[',
            ']': r'\]',
            '@': r'\@',
            '\\': r'\\'
        }
        regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(
            conv.keys(), key=lambda item: - len(item))))
        return regex.sub(lambda match: conv[match.group()], text)
    
    def _register_table(self, *args, **kwargs):
        ca = self.env.get('ca')
        return ca._register_string(self.table(*args, **kwargs))

    def table(self, table, options={}, **tableargs):
        ''' This function formats the table in either latex or markdown, depending on the output. '''
        typst = ""

        t = Table(table, env=self.env, **tableargs)

        columndef = ",".join(["auto" if cw == 0 else f"{cw}fr" for cw in t.colwidths])

        tablespan = ',\n'.join(
            f'[{"],[".join([self.escape(str(cell)) for cell in row])}]\n' for row in t.table
        )
        
        typst = f'#table(columns: ({columndef}), {tablespan})'

        return typst

    def newsection(self):
        return ''

    def newpage(self):
        ca = self.env.get('ca')
        return ca._register_string("#pagebreak()")
    
    def _build_markdown_headers(self, headers):
        return ''

    def headers(self):
        return ''

    def end(self):
        return ''

    def _build_markdown(self, templatemarkdown):
        # A giant string to put all the output markdown into
        markdown = ""

        log.info("Outputting markdown")
        env = self.env.get_env()

        try:
            j2template = jinja2.Template(templatemarkdown)
            processedtemplate = j2template.render(env)
            markdown += processedtemplate

            self._warn_in_text(self.templateheaders, env, markdown)


        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error(
                "Error in processing the final template: {}".format(error.message))
            log_jinja2_error(markdown, error)
            raise Exception("Error reading the final template: {} at lineno {} for file {}".format(
                error.message, error.lineno, error.filename))
        except jinja2.exceptions.TemplateError as error:
            log.error(
                "Error in processing the final template: {}".format(error.message))
            raise Exception("Error reading the final template: {}".format(
                error.message))

        return markdown

    def output(self, markdown, outputfile=''):
        output = self._build_markdown(markdown)

        lr = mistune.create_markdown(renderer=TypstRenderer())

        # Process the typst text
        output = lr(output)

        # Get the template and data directory
        if 'typst' in self.templateheaders:
            if 'template' in self.templateheaders['typst']:
                templatefile = os.path.join(
                    self.templateheaders['templatedir'], self.templateheaders['typst']['template'])
                with open(templatefile) as tf:
                    output = tf.read() + output
            if 'data_dir' in self.templateheaders['typst']:
                data_dir = os.path.join(
                    self.templateheaders['templatedir'], self.templateheaders['typst']['data_dir'])
                dest = os.path.join(os.getcwd(), "typst_template")
                if not os.path.exists(dest):
                    log.info(f"Copying '{data_dir}' to '{dest}'")
                    shutil.copytree(data_dir, dest)
            if 'template_variables' in self.templateheaders['typst']:
                # Add in env
                docenv = self.env.get_env()
                for var in self.templateheaders['typst']['template_variables']:
                    if var in docenv.keys():
                        output = f'#let {var} = "{str(docenv[var])}"\n' + output
                
        

        # Content assistant parsing
        output = self.env.get('ca').parse_register(self, output)

        if self.docformat and self.docformat != 'pdf':
            log.info("Writing Typst")
            with open(outputfile, 'w') as fh:
                fh.write(output)
                log.info("Finished writing")

            return output

        log.info("Writing PDF")
        log.error("We don't support writing PDF just yet!")

        return output
