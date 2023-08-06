import os

# This is to fill in the defaults so there's not too many variables
config = {
    "defaulttemplate": os.getenv('RR_TEMPLATE', '/mnt/c/Users/strid/OneDrive - Volkis/dev/volkis-rr-template/volkis-template.md'),
    "input_file": os.getenv('RR_INPUT_FILE', "reportbody.md"),
    "default_output_file": 'report-preview.md',
    "nessusmapper": os.getenv('RR_NESSUSMAPPER', '/mnt/c/Users/strid/OneDrive - Volkis/dev/pentest-docs/Vulnerability Templates/nessus-mapper.yaml'),
    "format": os.getenv('RR_FORMAT', ""),
    "verbose": os.getenv('RR_VERBOSE', False),
    # The template mapper. This gives the locations of template files for each template.
    "templatemapper": {
        "sample": "/mnt/c/Users/strid/OneDrive - Volkis/dev/rr-2/report-ranger/sample/sample-template/rr-sample-template.md"
    },
    # Additional template mapper files to link.
    "templatemappers": [
        "/mnt/c/Users/strid/OneDrive - Volkis/dev/volkis-rr-template/templatemapper.yaml"
    ],
    # Files with additional
    "includes": {

    }
}
