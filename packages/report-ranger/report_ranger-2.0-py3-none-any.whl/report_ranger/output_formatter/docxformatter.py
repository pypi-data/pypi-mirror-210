from report_ranger.output_formatter.outputformatter import OutputFormatter
import subprocess
import logging

log = logging.getLogger(__name__)


class DOCXFormatter(OutputFormatter):
    def __init__(self, templateheaders=dict(), timer=None, watcher=None):
        OutputFormatter.__init__(self, templateheaders, timer, watcher=watcher)
        self.figformat = "png"

    def _build_markdown_headers(self, headers):
        return ""

    def output(self, markdown, outputfile=''):
        output = self._build_markdown(markdown)

        if(self.docformat and self.docformat != 'docx'):
            log.info("Writing Markdown")
            with open(outputfile, 'w') as fh:
                fh.write(output)
            log.info("Finished writing")

            return output

        log.info("Writing DOCX")
        # Use Pandoc to print to PDF
        pandoc_arguments = ['pandoc', '--from', 'markdown', '--to', 'docx',
                            '--listings', '-o', outputfile]
        if self.templatefile:
            pandoc_arguments.append('--template')
            pandoc_arguments.append(self.templatefile)
        process = subprocess.run(pandoc_arguments,
                                 input=output,
                                 universal_newlines=True)

        return output
