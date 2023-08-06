from report_ranger import validation
from report_ranger.output_formatter.typstformatter import TypstFormatter
from report_ranger.utils.jinja_helpers import log_jinja2_error
from report_ranger.utils.mdread import markdown_from_file, process_included_header, process_template, _process_imports
from report_ranger.output_formatter.outputformatter import OutputFormatter
from report_ranger.riskassessment import RiskAssessment
from report_ranger.template import Template, retrieve_template
import os
import jinja2
import datetime
import logging
import traceback
import copy
import time
from report_ranger.output_formatter.latexformatter import LatexFormatter
from report_ranger.output_formatter.htmlformatter import HTMLFormatter
from report_ranger.output_formatter.csvformatter import CSVFormatter
from report_ranger.output_formatter.docxformatter import DOCXFormatter
import time

log = logging.getLogger(__name__)

def retrieve_output_formatter(target, templateheaders, timer, watcher=None):
    # Set up the appropriate output formatter
    if target == 'latex':
        return LatexFormatter(templateheaders, timer, watcher=watcher)
    elif target == 'html':
        return HTMLFormatter(templateheaders, timer, watcher=watcher)
    elif target == 'csv':
        of = CSVFormatter(templateheaders, timer, watcher=watcher)
    elif target == 'docx':
        of = DOCXFormatter(templateheaders, timer, watcher=watcher)
    elif target == 'typst':
        of = TypstFormatter(templateheaders, timer, watcher=watcher)
    else:  # Markdown formatter as default
        of = OutputFormatter(templateheaders, timer, watcher=watcher)
    return of

class Timer:
    def __init__(self):
        self._start_time=time.perf_counter()
    
    def time(self):
        return time.perf_counter() - self._start_time

class Report:
    """ Build a report from a collection of markdown. """

    def __init__(self, report_file, template:Template=None, templatefile:str="", default_template:str="", templatemapper:dict={}):
        self.timer = Timer()
        log.info(f"{self.timer.time()}: Retrieving file markdown")
        self.headers, self.markdown = markdown_from_file(report_file, process_imports=False)
        self.parentdir = os.path.dirname(os.path.join(os.path.curdir, report_file))
        self.templatefile = templatefile

        # Figure out where to get the template. In order of preference we take:
        # - Template provided in `template`
        # - Template provided in `templatefile`
        # - Template provided in the report, using templatemapper if necessary

        retrieved_template = False

        if template:
            # Template provided in `template`
            log.info("Using user provided template")
            self.template = self.template
            retrieved_template = True
        
        if not retrieved_template and templatefile != '':
            # Use the supplied template file
            try:
                self.template = retrieve_template(templatefile, templatemapper)
                log.info("Adding supplied template file")
                retrieved_template = True
            except Exception as e:
                log.warning(f"Template file provided cannot be loaded ({e.args}): {templatefile}")
        
        if not retrieved_template and 'template' in self.headers:
            # The template is specified in the report headers
            try:
                self.template = retrieve_template(self.headers['template'], templatemapper, self.parentdir)
                log.info("Adding template in report headers template file")
                retrieved_template = True
            except Exception as e:
                log.warning(f"Template in report headers cannot be loaded ({e.args}): {templatefile}")

        if not retrieved_template and default_template != "":
            # We're trying to fall back to the default template
            try:
                self.template = retrieve_template(default_template, templatemapper)
                log.info("Adding default template")
                retrieved_template = True
            except Exception as e:
                log.warning(f"Default template cannot be loaded ({e.args}): {default_template}")

        log.info(f"{self.timer.time()}: Finished report init")

    # If the "change_template" header is there the report can set its own template variables
    def _change_template_headers(self, templateheaders, reportheaders):
        if 'change_template' in reportheaders:
            log.info("change_template header detected")
            if not isinstance(reportheaders['change_template'], dict):
                log.warning(
                    "change_template front matter variable not a dictionary")
                return templateheaders

            # Notice this is back to front, the template itself is included into the report change_template variable
            templateheaders = process_included_header(
                reportheaders['change_template'], templateheaders)

        return templateheaders

    def attach_template(self, template:Template):
        self.template = template

    def process_file(self, mdfile, target, docformat, output=None, default_output_file=None, watcher=None):
        """ Process a file with the template. Returns the processed markdown for the file.

        The target should be one of (latex, docx, pdf)
        """
        
        log.info(f"{self.timer.time()}: Begin processing file")
        if watcher:
            watcher.clear_paths()
            watcher.set_running()

        # Make a new copy of the attached template
        templateheaders = copy.deepcopy(self.template.templateheaders)
        templatemarkdown = copy.deepcopy(self.template.templatemarkdown)

        templateheaders = self._change_template_headers(templateheaders, self.headers)

        # Initialise the risk assessment
        riskassessment = RiskAssessment(templateheaders['riskassessment'])
        if 'style_text' in templateheaders['riskassessment']:
            templateheaders['defaults']['ra_style_text'] = templateheaders['riskassessment']['style_text']

    
        log.info(f"{self.timer.time()}: Creating output formatter")

        of = retrieve_output_formatter(target, templateheaders, self.timer, watcher=watcher)

        # Set up environment variables
        of.env.set_static('ra', riskassessment)
        of.env.set_static('templatedir', templateheaders['templatedir'])

        # The title defaults to the filename without the extension
        if 'title' not in self.headers:
            log.warn("There's no title set in the front matter, the default title is the filename of {}".format(
                os.path.basename(mdfile)))
            of.env.set_variable('title', os.path.basename(mdfile))

        # Convert date to the date object
        if 'date' not in self.headers:
            # The date defaults to the last change, otherwise today
            if 'changes' in self.headers and len(self.headers['changes']) != 0:
                of.env.set_variable('date', self.headers['changes'][-1][1])
                log.info(f"As there's no date in front matter, date of the latest change is used: {of.env.get('date')}")
            else:
                of.env.set_variable('date', datetime.date.today())
                log.info(f"As there's no date in front matter or changes, date has been set to today: {of.env.get('date')}")

        if 'client' not in self.headers:
            log.warning(
                "Client name is not in the report front matter. Default of [client] will be used.")
            of.env.set_variable('client', '[client]')

        if 'version' not in self.headers:
            if 'changes' in self.headers:
                of.env.set_variable('version', self.headers['changes'][-1][0])
            else:
                of.env.set_variable('version', '1.0')
                log.warning(
                    "Version is not in the report front matter. Default of 1.0 will be used.")
        
        # We now need to process imports. This will import sections, vulnerabilities, XLSX and CSV files
        # We can't process imports before because the output formatter wasn't set up yet
        of.env.set_variables(self.headers)
        
        log.info("Setting reportbody imports")
        if 'defaults' in templateheaders:
            template_import_headers = _process_imports(
                templateheaders['defaults'],
                of.env,
                watcher=watcher,
                pathlist=[self.template.templatedir]
                )
            of.env.set_variables(template_import_headers)
        import_headers = _process_imports(
            self.headers,
            of.env,
            watcher=watcher
            )
        of.env.set_variables(import_headers)
        
        # Make sure that the risk assessment methodology is processed as RR markdown
        riskassessment.methodology_markdown = process_template(
            {}, riskassessment.methodology, env=of.env, name="Risk assessment methodology")

        if 'validation' in templateheaders:
            if 'report' in templateheaders['validation']:
                validation.validate_headers(
                    templateheaders['validation']['report'], self.headers, validation.default_report_validation)

        if output == None:
            if of.env.get('output_file'):
                rawfilename = of.env.get('output_file')
                try:
                    output = process_template({}, rawfilename, of.env, 'output_file')
                except Exception as error:
                    log.warn("Error processing filename header: {}".format(error.args))
                    output = f"{os.path.basename(mdfile)}.{docformat}"
                    log.warn(f"Setting to {output}")
            elif default_output_file:
                log.info(f"Setting to default output file {default_output_file}")
                output = default_output_file
            else:
                output = f"{os.path.basename(mdfile)}.{docformat}"
                log.warn(f"Filename not found, setting to {output}")

        log.info(f"{self.timer.time()}: Begin processing report body")

        # Render reportbody
        try:
            j2template = jinja2.Template(self.markdown)
            rbrendered = j2template.render(of.env.get_env())
            of.env.set_static('reportbody', rbrendered)
        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error("Report body render Jinja2 error: {} at lineno {} in reportbody for file {}".format(
                error.message, error.lineno, error.filename))
            log_jinja2_error(self.markdown, error)
            of.env.set_static('reportbody', "")
        except Exception as error:
            log.error("Exception found in reportbody: {}".format(error.args))
            traceback.print_exc()
            log.error("Removing reportbody text")
            of.env.set_static('reportbody', "")

        of.docformat = docformat
        of.options = {}
        
        log.info(f"{self.timer.time()}: Begin outputting")
        
        if watcher:
            watcher.stop_running()

        return of.output(templatemarkdown, output)
