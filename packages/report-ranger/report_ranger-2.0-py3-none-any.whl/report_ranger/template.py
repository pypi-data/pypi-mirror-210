import os
from report_ranger.utils.mdread import markdown_from_file
import logging

log = logging.getLogger(__name__)

def retrieve_template(templatefile, templatemapper={}, parentdir=""):
    if templatefile in templatemapper:
        return Template(templatemapper[templatefile], templatemapper)
    if parentdir:
        templatefile = os.path.join(parentdir, templatefile)
    if os.path.isfile(templatefile):
        return Template(templatefile, templatemapper)
    raise Exception(f"Could not find template {templatefile}")

class Template:
    template_headers={}
    template_markdown=""

    def __init__(self, templatefile, templatemapper={}):
        self.templateheaders, self.templatemarkdown = markdown_from_file(
            templatefile,
            includemapper=templatemapper,
            pathlist=[os.path.dirname(templatefile)]
            )

        self.templatedir = os.path.dirname(os.path.abspath(os.path.join(os.path.curdir, templatefile)))
        self.templateheaders['templatedir'] = self.templatedir

        self.templateheaders['latex_template'] = os.path.join(
            self.templatedir, self.templateheaders['latex']['template'])

        if 'html' in self.templateheaders:
            self.templateheaders['html_template'] = os.path.join(
                self.templatedir, self.templateheaders['html']['template'])
        else:
            self.html_template = ''
