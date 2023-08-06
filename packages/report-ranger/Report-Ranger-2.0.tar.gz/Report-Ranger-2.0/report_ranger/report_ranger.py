import time
from report_ranger.imports import vulnerability
from report_ranger import config  # Configuration settings within report ranger
from report_ranger.errors import InputError
from report_ranger.report import Report
from report_ranger.template import Template
from report_ranger.templatemapper import process_templatemapper
import os
import jinja2
import logging
from watchdog.observers import Observer
from report_ranger.watcher import Watcher

from report_ranger.utils.jinja_helpers import log_jinja2_error

log = logging.getLogger(__name__)


def main(args):
    # Turn on verbose mode
    if args.verbose:
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging.WARNING)

    parentdir = os.path.dirname(os.path.join(os.path.curdir, args.input))

    # We need to change the current working directory to the directory of the template otherwise relative
    # paths inside the template won't work. For instance you won't be able to include executivesummary.md
    rr_parent_folder = os.path.abspath(os.path.curdir)

    ctm = config.config['templatemapper'] if 'templatemapper' in config.config else {}        
    ctms = config.config['templatemappers'] if 'templatemappers' in config.config else []

    templatemapper = process_templatemapper(args.templatemapper, ctm, ctms)

    if args.template:
        if args.template in templatemapper:
            templatefile = templatemapper[args.template]
        else:
            templatefile = os.path.abspath(args.template)
    else:
        templatefile = ''

    os.chdir(parentdir)
    parentdir = '.'
    mdfile = os.path.basename(args.input)

    # Get the template
    report = Report(
        mdfile,
        templatefile=templatefile,
        templatemapper=templatemapper,
        default_template=config.config['defaulttemplate'])

    # Get the extension of the output file
    if args.output:
        fn, ext = os.path.splitext(args.output)
    else:
        ext = 'md'

    # Figure out what target we have
    if args.format == "pdf":
        target = "latex"
        docformat = "pdf"
    if args.format == "pdf-latex":
        target = "latex"
        docformat = "pdf"
    elif args.format == "markdown-latex":
        target = "latex"
        docformat = "markdown"
    elif args.format == "typst":
        target = "typst"
        docformat = "typst"
    elif args.format == "markdown":
        target = "markdown"
        docformat = "markdown"
    elif args.format == "docx":
        target = "docx"
        docformat = "docx"
    elif args.format == "html":
        target = "html"
        docformat = "html"
    elif args.format == "csv":
        target = "csv"
        docformat = "csv"
    else:
        if ext == ".docx":
            target = "docx"
            docformat = "docx"
            log.info("Setting target and format to docx")
        elif ext == ".md" or ext == ".rr":
            target = "markdown"
            docformat = "md"
            log.info("Setting target to markdown and format to md")
        elif ext == ".typ":
            target = "typst"
            docformat = "typst"
            log.info("Setting target to markdown and format to md")
        elif ext == ".html":
            target = "html"
            docformat = "html"
            log.info("Setting target and format to html")
        elif ext == ".csv":
            target = "csv"
            docformat = "csv"
            log.info("Setting target and format to csv")
        else:  # Default to PDF
            target = "latex"
            docformat = "pdf"
            log.info("Setting target to latex and format to pdf")

    # Pandoc does not support PDF output to stdout, so we need to hack it by
    # making a symlink to /dev/stdout and outputting to that file
    stdout_link = None
    if docformat.lower() == 'pdf' and args.output == '-':
        stdout_link = '/tmp/stdout.pdf'
        os.symlink('/dev/stdout', stdout_link)
        args.output = stdout_link

    # Convert output file path into full path if relative path is given
    if args.output and args.output[0] != '/':
        args.output = os.path.join(rr_parent_folder, args.output)


    if args.watch:
        log.info("Starting watch")
        try:
            watcher = Watcher(log.info, "Callback")
            watcher.set_callback(report.process_file, mdfile, target, docformat, args.output, default_output_file=config.config.get('default_output_file'), watcher=watcher)
            watcher.set_watch_mode(args.watch_mode)
            output = report.process_file(mdfile, target, docformat, args.output, default_output_file=config.config.get('default_output_file'), watcher=watcher)
            if args.watch_mode != "modified":
                log.info("Setting watch mode to os")
                observer = Observer()
                observer.schedule(watcher, parentdir, recursive=True)
                observer.start()
                try:
                    while True:
                        time.sleep(5)
                        watcher.run()
                finally:
                    observer.stop()
                    observer.join()
            else:
                log.info("Setting watch mode to modification time")
                while True:
                    try:
                        time.sleep(5)
                        watcher.run()
                    except InputError as ie:
                        log.error("Input Error: {}".format(ie.message))
                        exit()
                    except jinja2.exceptions.TemplateSyntaxError as error:
                        log.error("Final report processing Jinja2 error: {} at lineno {} for file {}".format(
                            error.message, error.lineno, error.filename))
                        log_jinja2_error(mdfile, error)
                        exit()

        except InputError as ie:
            log.error("Input Error: {}".format(ie.message))
        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error("Final report processing Jinja2 error: {} at lineno {} for file {}".format(
                error.message, error.lineno, error.filename))
            log_jinja2_error(mdfile, error)
    else:
        try:
            output = report.process_file(mdfile, target, docformat, args.output, default_output_file=config.config.get('default_output_file'))
        except InputError as ie:
            log.error("Input Error: {}".format(ie.message))
            exit()
        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error("Final report processing Jinja2 error: {} at lineno {} for file {}".format(
                error.message, error.lineno, error.filename))
            log_jinja2_error(mdfile, error)
            exit()

        # If we're outputting to stdout, remove the link
        if stdout_link and os.path.exists(stdout_link):
            os.remove(stdout_link)
