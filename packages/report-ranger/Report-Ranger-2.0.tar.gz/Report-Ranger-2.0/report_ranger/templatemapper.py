import yaml
import cerberus
import logging
import os

log = logging.getLogger(__name__)

# Cerberus validation for a strict dictionary
validate_strictdict = {
         'propertyschema': {'type': 'string'},
         'valuesschema':{
            'type':'string'
         }
     }

def process_templatemapperfile(filename):
    mapper = {}
    directory = os.path.dirname(filename)
    try:
        with open(filename, "r") as stream:
            try:
                filemapper = yaml.safe_load(stream)

                # Validate that the mapper is a simple dictionary
                v = cerberus.Validator(validate_strictdict)
                v.validate(filemapper)
                
                for name, location in filemapper.items():
                    mapper[name] = os.path.join(directory, location)
                
            except yaml.YAMLError as error:
                log.warn(f"Template mapper file '{filename}' not valid YAML code, gives error {error.args}")
                return {}
            except cerberus.schema.SchemaError as error:
                log.warn(f"Template mapper file '{filename}' does not contain a simple dict. Validation error {error.args}. Skipping.")
                return {}
    except FileNotFoundError as error:
        log.warn(f"Template mapper file '{filename}' not found. Skipping.")
    
    return mapper
    


def process_templatemapper(arg = None, config = {}, configfiles = []):
    """ Process the template mappers provided (if any).

    The order of precedence will be arg -> config -> configfiles.
    arg: a string containing the location of a template mapper or None
    config: A dictionary mapper from the config.py file
    configfiles: A list of files containing locations of template mappers
    """
    mapper = {}
    if configfiles:
        for tm in configfiles:
            mapper.update(process_templatemapperfile(tm))
    
    if config:
        mapper.update(config)

    if arg != None and arg != '':
        mapper.update(process_templatemapperfile(arg))

    return mapper