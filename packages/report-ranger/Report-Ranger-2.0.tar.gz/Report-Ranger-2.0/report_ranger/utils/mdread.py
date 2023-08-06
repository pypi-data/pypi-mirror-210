import copy
from report_ranger.errors import InputError
import os
from pathlib import Path
import re
from jinja2 import Template
import jinja2
from jinja2.runtime import Macro
import yaml
import json
from report_ranger.imports.imports import import_csv, import_xlsx
import logging
from report_ranger.imports import section
from report_ranger.helpers import make_list
from report_ranger.imports import vulnerability
import traceback
import datetime

from report_ranger.utils.jinja_helpers import log_jinja2_error

log = logging.getLogger(__name__)

yamlmatch = re.compile(r'^[\.\=\-]{3}$')
jsonmatch = re.compile(r'^\;\;\;$')


def process_included_header(headers, includedheaders):
    """ Process the included headers using an overlay routine:
    - Don't overwrite values
    - Add new values if they're not there
    - Append to lists
    """
    if isinstance(includedheaders, dict):
        if not isinstance(headers, dict):
            return headers
        for header in includedheaders:
            if header in headers:
                header = process_included_header(
                    headers[header], includedheaders[header])
            else:
                headers[header] = includedheaders[header]
        return headers
    elif isinstance(includedheaders, list):
        if not isinstance(headers, dict):
            return headers
        headers.extend(includedheaders)
        return headers
    else:
        return headers


def process_template(headers, markdown, env=None, name='', filename=''):
    try:
        template = Template(markdown)  # Start jinja2
        env.push(headers)  # Add our new headers in
        output = template.render(env.get_env())
        env.pop()  # Take away the headers

    except jinja2.exceptions.TemplateSyntaxError as error:
        log.error(f"Error in processing {name} at {filename}")
        log.error(f"Message: {error.message}. Line number: {error.lineno}.")
        log_jinja2_error(markdown, error)
        raise Exception(f"Error reading {name}: {error.message} at lineno {error.lineno}")

    return output

def _get_resultant_path(file:str, filemapper:dict={}, pathlist:list=[]):
    # Try CWD
    filepath = Path(file)
    if filepath.exists():
        return filepath
    
    # Try includemapper
    if file in filemapper:
        file = filemapper[file]
        return Path(file)
    
    # Try pathlist
    if len(pathlist) > 0:
        for path in pathlist:
            filepath = Path(path) / Path(file)
            if Path(path) not in filepath.parents:
                log.warn(f"Path {filepath} seems to be going up in directories, skipping")
                raise Exception("Could not get resultant path")
            if filepath.exists():
                return filepath
    raise Exception("Could not find file")

def _process_includes(headers, env=None, includemapper={}, pathlist=[], watcher=None):
    for included in make_list(headers['include']):
        log.info(f"Including headers from file {included}")
        try:
            included = _get_resultant_path(included, includemapper, pathlist)
            log.info(f"Just about to process include with env={env}")
            includedheaders, _ = markdown_from_file(included, pathlist=pathlist, env=env, watcher=watcher)
            headers = process_included_header(headers, includedheaders)
        except Exception as e:
            log.warn(f"Could not include headers from file {included}: {e.args}")
    return headers

def _process_include_markdown(markdown, includemapper, pathlist, watcher=None):
    try:
        included = _get_resultant_path(markdown, includemapper, pathlist)
        log.info(f"Processing included markdown")
        _, included_markdown = markdown_from_file(included, pathlist=pathlist, process_imports=False, process_includes=False, watcher=watcher)
        return included_markdown
    except Exception as e:
        log.warn(f"Could not include headers from file {included}: {e.args}")

def _check_import_directory(importdict):
    """ Run the standard checks for directory imports including vulnerabilities and sections
    """
    if 'variable' not in importdict or not isinstance(importdict['variable'], str):
        raise Exception("Import item does not have variable name")
    if not isinstance(importdict, dict):
        raise Exception(f"Import item '{importdict['variable']}' in front matter not a dict")
    if 'directory' not in importdict or not isinstance(importdict['directory'], str):
        raise Exception(f"Import item '{importdict['variable']}' does not have a directory")
    return True

def _process_imports(headers, env=None, watcher=None, includemapper:dict={}, pathlist:dict={}):
    new_headers = {}
    if not 'import' in headers:
        log.info("No import in headers")
        return {}
    if not isinstance(headers['import'], dict):
        log.warn("import front matter variable not a dict, skipping")
    else:
        if 'vulnerabilities' in headers['import']:
            vulnerabilities = make_list(headers['import']['vulnerabilities'])
            for vulnerabilitiesimport in vulnerabilities:
                if vulnerabilitiesimport['variable'] in headers:
                    log.warn(
                        f"Vulnerabilities import variable name {vulnerabilitiesimport['variable']} already in front matter, skipping")
                    continue
                
                try:
                    _check_import_directory(vulnerabilitiesimport)
                except Exception as e:
                    log.warn(f"Error importing vulnerabilities: {e.args}")

                vulndir = vulnerabilitiesimport['directory']
                log.info("Vulnerability directory included: {}".format(vulndir))

                vulnerabilitylist = vulnerability.VulnerabilityList()

                try:
                    # Get the vulnerability validation (if it exists) from the env
                    vulnerability_validation = {}
                    if 'validation' in vulnerabilitiesimport:
                        validation = vulnerabilitiesimport['validation']
                        if validation is dict and 'vulnerability' in validation:
                            vulnerability_validation = validation['vulnerability']

                    if env == None:
                        log.warn("Exception raising because env is None in _process_imports vulnerability import")
                        raise Exception("env is None")

                    vulnerabilitylist.add_from_dir(
                        vulndir, env, env.get("ra"), vulnerability_validation=vulnerability_validation, watcher=watcher)

                    if 'updated_date' in vulnerabilitiesimport:
                        updated_date = vulnerabilitiesimport['updated_date']
                        if updated_date == 'today':
                            updated_date = datetime.date.today()
                        log.info(f"Updating vulnerabilities to {updated_date}")
                        log.info(f"Vulnerabilities: {vulnerabilitylist}")
                        vulnerabilitylist = vulnerabilitylist.updated(updated_date)
                        log.info(f"Updated vulnerabilities: {vulnerabilitylist}")
                    
                    log.info(f"Setting vulnerabilities as {vulnerabilitylist}")
                    new_headers[vulnerabilitiesimport['variable']] = vulnerabilitylist

                    # Generate vulnerability markdown
                    vulnerabilitylist.generate_markdown(env)
                except FileNotFoundError as e:
                    log.warn(e.args[0])
                except Exception as e:
                    log.warn(f"Error loading vulnerabilities import {vulnerabilitiesimport['variable']}: {e.args}")
                    log.warn(traceback.format_exc())
            
        if 'sections' in headers['import']:
            sectionlist = make_list(headers['import']['sections'])
            for sectionimport in sectionlist:
                if not isinstance(sectionimport, dict):
                    log.warn(
                        "Section import item in front matter not a dict, skipping")
                    continue
                if 'directory' not in sectionimport or not isinstance(sectionimport['directory'], str):
                    log.warn(
                        "Section import item does not have a directory, skipping")
                    continue
                if 'variable' not in sectionimport or not isinstance(sectionimport['variable'], str):
                    log.warn(
                        "Section import item does not have variable name, skipping")
                    continue
                if sectionimport['variable'] in headers:
                    log.warn(
                        "Section import variable name already in front matter, skipping")
                    continue
                if 'ordinal' in sectionimport:
                    ordinal = sectionimport['ordinal']
                else:
                    ordinal = '1'

                # Build the section
                newsection = section.Section(
                    sectionimport['directory'], ordinal, watcher=watcher)

                new_headers[sectionimport['variable']] = newsection.get_chapters(env)

        # Begin CSV imports
        if 'csv' in headers['import']:
            csvlist = make_list(headers['import']['csv'])
            for csvimport in csvlist:
                if not isinstance(csvimport, dict):
                    log.warn(
                        "csv import item in front matter not a dict, skipping")
                    continue
                if 'file' not in csvimport or not isinstance(csvimport['file'], str):
                    log.warn(
                        "csv import item does not have file location, skipping")
                    continue
                if 'variable' not in csvimport or not isinstance(csvimport['variable'], str):
                    log.warn(
                        "csv import item does not have variable name, skipping")
                    continue
                if csvimport['variable'] in headers:
                    log.warn(
                        "csv import variable name already in front matter, skipping")
                    continue
                if 'as_dict_list' in csvimport and not isinstance(csvimport['as_dict_list'], bool):
                    log.warning(
                        'csv import defines "as_dict_list", but it is not a boolean')
                    continue
                if 'index_col' in csvimport and not isinstance(csvimport['index_col'], int):
                    log.warning(
                        'csv import defines "index_col", but it is not an integer')
                    continue

                new_headers[csvimport['variable']] = import_csv(csvimport['file'], as_dict_list=csvimport.get(
                    'as_dict_list'), index_col=csvimport.get('index_col'))
        # Begin xlsx imports
        if 'xlsx' in headers['import']:
            xlsxlist = make_list(headers['import']['xlsx'])
            for xlsximport in xlsxlist:
                if not isinstance(xlsximport, dict):
                    log.warn(
                        "xlsx import item in front matter not a dict, skipping")
                    continue
                if 'file' not in xlsximport or not isinstance(xlsximport['file'], str):
                    log.warn(
                        "xlsx import item does not have file location, skipping")
                    continue
                if 'variable' not in xlsximport or not isinstance(xlsximport['variable'], str):
                    log.warn(
                        "xlsx import item does not have variable name, skipping")
                    continue
                if xlsximport['variable'] in headers:
                    log.warn(
                        "xlsx import variable name already in front matter, skipping")
                    continue
                if 'as_dict_list' in xlsximport and not isinstance(xlsximport['as_dict_list'], bool):
                    log.warning(
                        'xlsx import defines "as_dict_list", but it is not a boolean')
                    continue
                if 'index_col' in xlsximport and not isinstance(xlsximport['index_col'], int):
                    log.warning(
                        'xlsx import defines "index_col", but it is not an integer')
                    continue

                new_headers[xlsximport['variable']] = import_xlsx(
                    xlsximport['file'],
                    xlsximport.get('worksheet'),
                    xlsximport.get('min_row'),
                    xlsximport.get('max_row'),
                    xlsximport.get('min_col'),
                    xlsximport.get('max_col'),
                    as_dict_list=xlsximport.get('as_dict_list'),
                    index_col=xlsximport.get('index_col')
                )

        if 'macros' in headers['import']:
            macrolist = make_list(headers['import']['macros'])
            for macrofile in macrolist:
                fn, ext = os.path.splitext(macrofile)
                if ext not in ['.md', '.j2', '.jinja', '.rr']:
                    log.warn(f"Macro file {macrofile} not of the right extension. The extension is {ext} but should be one of md, j2, jinja, or rr")
                    continue
                try:
                    macrofile = _get_resultant_path(macrofile, includemapper, pathlist)
                except:
                    log.warn(f"Could not find {macrofile}")
                    continue

                mdheaders, markdown = markdown_from_file(macrofile, env=env, watcher=watcher)
                mdheaders['cwd'] = os.path.dirname(
                    os.path.join(os.path.curdir, macrofile))

                try:
                    jenv = jinja2.Environment()
                    # Add in the env to the globals. We want the existing globals to take precedence
                    globals = env.get_env()
                    globals.update(jenv.globals)
                    jenv.globals = globals
                    # Get the macro template from the markdown
                    macro_template = jenv.from_string(markdown)
                    # Copy over the macros and set variables into the new headers
                    for f in [method for method in dir(macro_template.module) if method.startswith('_') is False]:
                        k = getattr(macro_template.module, f)
                        if isinstance(k, Macro):
                            log.info(f"Setting macro {k.name}")
                            new_headers[k.name] = k
                        elif isinstance(k, str) or isinstance(k, int):
                            log.info(f"Setting variable {f} as {k}")
                            new_headers[f] = k
                except jinja2.exceptions.TemplateSyntaxError as error:
                    log.error("Jinja2 error processing macro file {}: {} at lineno {} for file {}".format(
                        macrofile, error.message, error.lineno, filename=error.filename))
                    log.error("Skipping import of macro file {}".format(macrofile))
                    log_jinja2_error(markdown, error)
                    log.error(traceback.format_exc())
                    return ""
                except Exception as e:
                    log.error(
                        "Received exception when processing markdown for macro file {}: {}".format(macrofile, e.args))
                    log.error(
                        "Skipping import of macro file {}".format(macrofile))
                    log.error(traceback.format_exc())
                    return ""

    return new_headers


def markdown_from_file(file_loc, env=None, includemapper={}, process_includes=True, process_imports=True, pathlist=[], watcher=None):
    """ Read the markdown from a file.

    Arguments:
    - file_loc: The location of the file to read
    - env: The environment in its current context. The stack for this environment will be extended.
    - process_includes: Whether or not to process the include header, allowing the including of headers and markdown from other files.
    - process_imports: Whether or not to process the import header, allowing importing of sections, vulns, csv and xlsx files.
    - watcher: if a watcher is configured then add_path will automatically be called
    
    Returns (headers, markdown) where headers is a dict and markdown is a long string """

    log.debug(f"Reading markdown from file {file_loc}")

    if not os.path.exists(file_loc):
        log.warn(f"Trying to read file {file_loc} but it doesn't exist")
        return dict(), ""

    if watcher:
        watcher.add_path(file_loc)

    with open(file_loc, 'r') as vf:
        # If the first line starts with "---" that's our headers We have to make sure that it starts with "---"
        firstline = vf.readline()
        headers = dict()
        if yamlmatch.match(firstline):
            line = vf.readline()
            headerstring = ''
            # Read the headers.
            # Go until we get to the terminator to end the headers
            while not yamlmatch.match(line):
                headerstring += line
                line = vf.readline()
                if not line:
                    raise InputError(
                        f"Markdown file {file_loc} YAML headers don't end in a YAML terminator (...,---,===)")
            headers = yaml.safe_load(headerstring)  # Retrieve the YAML headers
            if headers == None:
                headers = {}
            markdown = vf.read()  # Read the rest of the file
        elif jsonmatch.match(firstline):
            line = vf.readline()
            headerstring = ''
            # Read the headers.
            # Go until we get to the terminator to end the headers
            while not jsonmatch.match(line):
                headerstring += line
                line = vf.readline()
                if not line:
                    raise InputError(
                        f"Markdown file {file_loc} JSON headers don't end in a JSON terminator (;;;)")
            headers = json.loads(headerstring)  # Retrieve the JSON headers
            markdown = vf.read()  # Read the rest of the file
        else:
            # There's no headers in this file. Put the first line back and just add it all into the markdown
            markdown = firstline + '\n' + vf.read()

        # Begin post processing. Process includes and imports.

        # Process includes in headers
        if process_includes and 'include' in headers:
            headers = _process_includes(headers, includemapper=includemapper, pathlist=pathlist, env=env)
        
        # Process include_markdown
        if process_includes and 'include_markdown' in headers:
            markdown = _process_include_markdown(headers['include_markdown'], includemapper, pathlist)

        # Process imports in headers
        if process_imports and 'import' in headers:
            if env == None:
                log.warn("Importing stopped because passed environment is None")
            else:
                log.info(f"Processing imports in file {file_loc}")
                headers.update(_process_imports(headers, env, pathlist=pathlist, includemapper=includemapper))

        return headers, markdown


def markdown_from_directory(dir_loc, env=None, watcher=None):
    log.debug("Reading markdown from directory '{}'".format(dir_loc))

    if not os.path.isdir(dir_loc):
        raise FileNotFoundError("Directory '{0}' doesn't exist. Skipping import of files from the directory.".format(
            dir_loc))

    files = []

    for f in os.listdir(dir_loc):
        mdfile = os.path.join(dir_loc, f)
        if os.path.isfile(mdfile):
            dir, filename = os.path.split(mdfile)
            fn, ext = os.path.splitext(filename)
            if ext == ".md" or ext == ".rr":
                mdfromfile=markdown_from_file(mdfile, env, watcher=watcher)
                mdfromfile[0]["filename"] = filename
                mdfromfile[0]["filename_noext"] = fn
                mdfromfile[0]["filename_full"] = mdfile
                files.extend([mdfromfile])
                

    return files
