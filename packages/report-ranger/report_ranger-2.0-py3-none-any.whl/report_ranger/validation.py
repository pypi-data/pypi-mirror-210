# This file contains validation functions and exceptions

import cerberus
import logging

log = logging.getLogger(__name__)

default_report_validation = {
    "title": {'type': 'string', 'required': True}
}

default_vulnerability_validation = {
    "name": {'type': 'string', 'required': True}
}

default_appendix_validation = {
    "name": {'type': 'string', 'required': True}
}


class ValidationError(Exception):
    pass


def validate_headers(validation, headers, defaults={}, name="template"):
    validator = cerberus.Validator()
    validator.allow_unknown = True

    schema = defaults.copy()
    schema.update(validation)

    validator.schema = schema

    if validator.validate(headers) == True:
        return True

    # We have an error!
    for error in validator.errors.keys():
        logging.error("Validation of {} failed due to header {}: {}".format(name,
                                                                            error, validator.errors[error]))

    raise ValidationError(
        "Validation of headers of {} failed: {}".format(name, validator.errors))
