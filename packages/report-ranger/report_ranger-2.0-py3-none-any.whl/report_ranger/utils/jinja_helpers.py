import logging

log = logging.getLogger(__name__)

def log_jinja2_error(markdown, error):
    log.error("Affected lines:")
    mdlines = markdown.splitlines()
    for i in range(5):
        el = error.lineno - 5 + i
        if el < 0:
            continue
        log.error("{}: {}".format(el, mdlines[el]))
    log.error("+ {}: {}".format(error.lineno, mdlines[error.lineno]))
    for i in range(5):
        el = error.lineno + 1 + i
        if el >= len(mdlines):
            continue
        log.error("{}: {}".format(el, mdlines[el]))