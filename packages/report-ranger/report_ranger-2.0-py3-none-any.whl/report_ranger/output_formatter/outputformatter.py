import os
import jinja2
from report_ranger.utils.jinja_helpers import log_jinja2_error
from report_ranger.utils.mdread import markdown_from_file, process_template
from report_ranger.table import Table
from report_ranger.contentassistant import ContentAssistant
from num2words import num2words
import pandas as pd
import plotly.express as px
from pathlib import Path
from report_ranger.environment import Environment
from tabulate import tabulate
from report_ranger.imports.imports import import_csv, import_xlsx
import traceback
import logging
from report_ranger.styles import TableStyles, ColorList, test_color
from report_ranger.imports.section import Section
import plotly.io as pio
import plotly.graph_objects as go
from report_ranger.helpers import table_aggregate, table_aggregate_value, filter_rows, table_to_dict, tables_outer_join, table_separate_column, table_add_row, table_separate_column_groups, sort_table, separate_sequences

# Mathjax fix for plotly
pio.kaleido.scope.mathjax = None

log = logging.getLogger(__name__)

headeralias = {
    'h': 'thead',
    'e': 'temph',
    'L': 'tlow',
    'M': 'tmedium',
    'H': 'thigh',
    'C': 'tcritical',
    'I': 'tinformational',
    'o': 'topen',
    'c': 'tclosed',
    'cb': 'tclosedbold',
    'O': 'topenbold',
    'ob': 'topenbold',
    'b': 'bold'
}


# For sorting IP addresses
def split_ip(ip):
    """Split a IP address given as string into a 4-tuple of integers."""
    return tuple(int(part) for part in ip.split('.'))

def sort_ips(item):
    ''' Helper function for sorting IPs, used as key in sorted function. '''
    return split_ip(item)

def oxfordcomma(listed):
    if len(listed) == 0:
        return ''
    if len(listed) == 1:
        return listed[0]
    if len(listed) == 2:
        return listed[0] + ' and ' + listed[1]
    return ', '.join(listed[:-1]) + ', and ' + listed[-1]


class OutputFormatter:
    def __init__(self, templateheaders=dict(), timer=None, watcher=None):
        self.templateheaders = templateheaders
        self.figformat = "png"
        self.watcher=watcher
        log.info(f"watcher is {watcher}")

        self.timer = timer

        self.timer = timer

        # Initial filling in the environment
        log.info(f"{self.time()}: Initialising new environment for output formatter")
        env = Environment()
        env.set_static('file_exists', self.file_exists)
        env.set_static('include_file', self.include_file)
        env.set_static('escape', self.escape)
        env.set_static('stringescape', self.escape)
        env.set_static('pathjoin', os.path.join)
        env.set_static('range', range)
        env.set_static('str', str)
        env.set_static('int', int)
        env.set_static('len', len)
        env.set_static('num2words', num2words)
        env.set_static('oxfordcomma', oxfordcomma)
        env.set_static('px', px)
        env.set_static('pd', pd)

        env.set_static('nfig', 0)
        ca = ContentAssistant()
        env.set_static('ca', ca)
        env.set_static('ft', ca.format_table)
        env.set_static('format_table', ca.format_table)
        env.set_static('counter', ca.counter)
        env.set_static('get_counter', ca.get_counter)
        env.set_static('reset_counter', ca.reset_counter)
        env.set_static('icounter', ca.icounter)
        env.set_static('get_icounter', ca.get_icounter)
        env.set_static('reset_icounter', ca.reset_icounter)
        env.set_static('table_row', ca.table_row)
        env.set_static('table_rows', ca.table_rows)
        env.set_static('display_table', ca.display_table)

        env.set_static('newpage', self.newpage)
        env.set_static('new_page', self.newpage)
        env.set_static('import_csv', import_csv)
        env.set_static('csv', import_csv)
        env.set_static('import_xlsx', import_xlsx)
        env.set_static('xlsx', import_xlsx)
        env.set_static('import_section', self.import_section)
        env.set_static('process_tags', self.process_tags)
        env.set_static('build_from_data', self.build_from_data)
        env.set_static('new_section', self.newsection)
        env.set_static('end_report', self.end)
        env.set_static('iplist', self.iplist)
        env.set_static('table', self.table)
        env.set_static('figure', self.fig)
        env.set_static('fig', self.fig)
        env.set_static('bar_chart', self.bar_chart)
        env.set_static('polar_bar_chart', self.polar_bar_chart)
        env.set_static('funnel_chart', self.funnel_chart)
        env.set_static('chart', self.chart)
        env.set_static('include', self.include_file)
        env.set_static('table_aggregate', table_aggregate)
        env.set_static('table_aggregate_value', table_aggregate_value)
        env.set_static('filter_rows', filter_rows)
        env.set_static('sort_table', sort_table)
        env.set_static('table_to_dict', table_to_dict)
        env.set_static('tables_outer_join', tables_outer_join)
        env.set_static('table_separate_column', table_separate_column)
        env.set_static('table_add_row', table_add_row)
        env.set_static('table_separate_column_groups',
                       table_separate_column_groups)
        env.set_static('separate_sequences',
                       separate_sequences)

        # Legacy variables - these function names have changed, but can be referred to with the old function name
        env.set_static('include_file', self.include_file)  # Legacy

        # For legacy reasons, let's set a new "of" variable which contains pointers to functions in the output formatter
        of = type('of', (object,), {})()
        of.newpage = self.newpage
        of.newsection = self.newsection
        of.end = self.end
        of.table = self.table
        of.iplist = self.iplist
        of.fig = self.fig
        of.include_file = self.include_file
        of.escape = self.escape
        env.set_static('of', of)
        
        log.info(f"{self.time()}: Finished basic setting up env")

        # Start with the defaults
        if 'defaults' in templateheaders:
            env.set_variables(templateheaders['defaults'])

        # Get color list
        self.colors = ColorList()
        if 'colors' in self.templateheaders:
            self.colors.addcolors(self.templateheaders['colors'])
        if 'colors' in self.templateheaders['riskassessment']:
            self.colors.addcolors(self.templateheaders['riskassessment']['colors'])


        log.info(f"{self.time()}: Setting up table styles")

        # Get table styles
        self.tablestyles = TableStyles()

        temp_ts = dict()

        if 'table_styles' in self.templateheaders:
            temp_ts = self.templateheaders['table_styles']

        if 'table_styles' in self.templateheaders['riskassessment']:
            temp_ts.update(self.templateheaders['riskassessment']['table_styles'])

        for name, style in temp_ts.items():
            # We need to make sure the colors are in the colorlist otherwise
            # latex won't be able to refer to the color
            if 'color' in style and not self.colors.getcolor(style['color']):
                style['color'] = self.colors.addcolor(None, style['color'])
                log.info("added new color {}".format(style['color']))
            if 'bgcolor' in style and not self.colors.getcolor(style['bgcolor']):
                style['bgcolor'] = self.colors.addcolor(
                    None, style['bgcolor'])
                log.info("added new color {}".format(style['bgcolor']))

            self.tablestyles.addstyle(name, style)

        self.env = env
        
        log.info(f"{self.time()}: Setting up plotly template")

        self.setup_plotly_template(self.templateheaders, self.colors)

        log.info(f"{self.time()}: Finished output formatter initialisation")

    def time(self):
        if self.timer:
            return self.timer.time()
        return ""

    def stringescape(self, text):
        return text.replace("\\", "\\\\")

    def escape(self, text):
        return text

    def import_section(self, directory, ordinal='1'):
        newsection = Section(directory, ordinal, watcher=self.watcher)
        return newsection.get_chapters(self.env)

    def iplist(self, listofips, heading="IP list", columns=4):
        '''Build a table from a list of IPs. Automatically format based on number of columns and sort IPs into order.'''

        log.debug("iplist(): Building IP list")

        try:
            sortedips = sorted(listofips, key=sort_ips)
        except Exception as e:
            log.warn(
                "IP list failed sorting, just leaving it unsorted: {}".format(e.args))
            sortedips = listofips

        if(len(sortedips) < columns):
            columns = len(sortedips)

        iptable = [[heading]]
        for i in range(len(sortedips)):
            row = int(i / columns) + 1
            if i % columns == 0:
                iptable += [[]]
            iptable[row] += [sortedips[i]]

        return self.table(iptable, headings='top', colspan=[[columns]], cellalign=[['c']])

    def table(self, table, options={}, **tableargs):
        ''' This function formats the table in either latex or markdown, depending on the output.'''

        t = Table(table, env=self.env, **tableargs)

        # We're going to do a markdown table with tabulate
        if t.colalign != None:
            # We need to convert the 'l' and 'r' in colalign if it exists
            ca = []
            for col in t.colalign:
                if col == 'r':
                    ca.append('right')
                elif col == 'c':
                    ca.append('center')
                else:
                    ca.append('left')
        else:
            ca = None

        return tabulate(t.table[1:], t.table[0], stralign=ca, tablefmt="github")

    def newsection(self):
        return ""

    def newpage(self):
        return ""

    def headers(self):
        return ""

    def end(self):
        """ To be called at the end of the output - puts in the ending page/graphics """
        return ""

    def ra_methodology(self, ra):
        """ The output for the risk assessment methodology for the appendices """
        markdown = ra.markdown
        return markdown

    def file_exists(self, file_loc):
        fn, ext = os.path.splitext(file_loc)
        if ext != ".md" and ext != ".rr":
            return False
        return os.path.isfile(file_loc)

    def process_tags(self, text, add_to_env={}):
        if type(text) is not str:
            log.warn("Text passed to process_tags is not a string")
            return ""
        if text == "":
            log.warn("Empty string passed to process_tags")
            return ""
        return process_template(
            add_to_env, text, env=self.env, name="Call to process")

    def build_from_data(self, data, headings={}, heading_text={}, text={}, pre_text={}):
        """
        Build a hierarchy of report headings and text based on the entries in data.

        This function is commonly used to "reportise" a spreadsheet and so the expected data structures match
        the csv and xslx functions. Data should be in the format of dicts/lists of dicts/lists, like what the
        csv and xslx functions return.

        The headings parameter should provide a dict mapping between the depth of heading (1-4) to either the
        index or key of the column which should map to the heading. The text of the heading is pasted in, which
        means multiple lines will cause normal markdown to be displayed. Similarly, text is a dict mapping the
        heading depth with what text to show under that heading.
        """

        # If the structure is a dict, assume it's a row indexed dict. In that case we only want the values
        # as a list
        if type(data) is dict:
            data = data.values()

        # Make sure we now have a list
        if type(data) is not list:
            log.warn(
                "Data passed to build_from_data isn't a list or a dict, skipping.")
            return ''

        # Detect if we've got a list of dicts (colindexed) or a list of lists (not colindexed)
        if len(data) == 0:
            log.warn("Empty set of data passed to build_from_data, skipping.")
            return ''
        elif type(data[0]) is dict:
            colindexed = True
        elif type(data[0]) is list:
            colindexed = False
        else:
            log.warn(
                "Data passed to build_from_data is a list of something other than dicts or lists, skipping.")
            return ''

        try:
            # If we don't have accurate heading keys, the loop below will fail miserably. We've got to fix that.
            depths = list(headings.keys())
            for depth in depths:
                if depth not in range(1, 5):
                    log.warn(
                        "Heading keys in call build_from_data included {} which is not in the range 1-4, skipping".format(depth))
                    del headings[depth]

            # Lets try this again
            depths = list(headings.keys())

            if len(headings) == 0:
                log.warn("Call to build_from_data has no headings, skipping.")
                return ''

            current_headings = []
            markdown = ''
            for cr in range(len(data)):
                row = data[cr]

                for cd in range(len(depths)):
                    # Get the value of the heading. Note that this is the same whether it's a dict or list
                    heading = headings[depths[cd]]

                    if cd >= len(current_headings):  # We have to add the new heading
                        current_headings.append(row[heading])
                    elif row[heading] != current_headings[cd] and row[heading] != '' and row[heading] != None:
                        # We have a new heading. Let's snip off the headings of lower depths
                        # and add the new current heading
                        current_headings = current_headings[:cd] + [
                            row[heading]]
                    else:
                        # This heading isn't new, we can skip this depth
                        continue

                    # Need to pull pull together this and what is below
                    rd = dict(row)
                    th = {}
                    for key in rd:
                        new_key = str(key)
                        th[new_key.replace(
                            ' ', '_')] = rd[new_key]

                    # If there's pre_text print it out
                    # TODO: Add the potential to call other cells etc
                    if depths[cd] in pre_text:
                        markdown += "{}\n\n".format(
                            process_template(
                                th, pre_text[depths[cd]], env=self.env, name="build_from_data cell")
                        )

                    if depths[cd] in heading_text:
                        markdown += "{}\n\n".format(
                            process_template(
                                th, heading_text[depths[cd]], env=self.env, name="build_from_data cell")
                        )
                    else:
                        # Print it out
                        markdown += "{} {}\n\n".format("#" *
                                                       depths[cd], row[heading])

                    # If there's text print this out as well
                    if depths[cd] in text:
                        try:
                            # We need to get the rows under this heading to add to the jinja environment. That allows us
                            # to refer to the rows for summary lists for instance
                            # TODO This isn't necessary when you're referring directly to a column. Fix.
                            upcoming_rows = []
                            for ucr in range(cr, len(data)):
                                upcoming_row = data[ucr]
                                new_heading = False
                                for ucd in range(0, cd+1):
                                    heading = headings[depths[ucd]]
                                    if upcoming_row[heading] != current_headings[ucd] and upcoming_row[heading] != '' and upcoming_row[heading] != None:
                                        # log.info(
                                        #    "upcoming rows break: current heading {} is {}, upcoming_row[heading] is {}".format(ucd, current_headings[ucd], upcoming_row[heading]))
                                        new_heading = True
                                        break

                                if new_heading:
                                    break
                                else:
                                    upcoming_rows.append(upcoming_row)

                            if colindexed:
                                row_dict = dict(row)
                                # Fix up headings with spaces
                                text_headers = {}
                                for key in row_dict:
                                    new_key = str(key)
                                    text_headers[new_key.replace(
                                        ' ', '_')] = row_dict[new_key]
                                text_headers['upcoming_rows'] = upcoming_rows

                                # The user has the choice of putting in the title of a row or directly putting in templated markdown into text.
                                if text[depths[cd]] in row and row[text[depths[cd]]] != '':
                                    # Skip if there's nothing to display. This stops, for instance, displaying "None".
                                    if row[text[depths[cd]]] != '' and row[text[depths[cd]]] != None:
                                        markdown += "{}\n\n".format(process_template(
                                            text_headers, row[text[depths[cd]]], env=self.env, name="build_from_data cell"))
                                else:
                                    markdown += "{}\n\n".format(process_template(
                                        text_headers, text[depths[cd]], env=self.env, name="build_from_data cell"))

                                # log.info('upcoming_rows: {}'.format(upcoming_rows))

                            else:
                                text_headers = {'row': row,
                                                'upcoming_rows': upcoming_rows}

                                # Here the user can instead put in a number referring to the column number
                                if text[depths[cd]] in range(len(row)):
                                    # Skip if there's nothing to display. This stops, for instance, displaying "None".
                                    if row[text[depths[cd]]] != '' and row[text[depths[cd]]] != None:
                                        markdown += "{}\n\n".format(process_template(
                                            text_headers, row[text[depths[cd]]], env=self.env, name="build_from_data cell"))
                                else:
                                    markdown += "{}\n\n".format(process_template(
                                        text_headers, text[depths[cd]], env=self.env, name="build_from_data cell"))
                        except Exception as e:
                            log.warn(
                                "Exception occurred in building text in column {} of data in build_from_data, args: {}".format(heading, e.args))
                            log.warn(traceback.format_exc())

            return markdown

        except Exception as e:
            log.warn("Call to build_from_data failed: {}".format(e.args))
            log.warn(traceback.format_exc())
            return ''

    def include_file(self, file_loc, include_headers=True, custom_headers=None):
        """ Process the file, template it, and return just the markdown """
        fn, ext = os.path.splitext(file_loc)
        if ext != ".md" and ext != ".rr":
            return ""
        headers, markdown = markdown_from_file(file_loc, env=self.env, watcher=self.watcher)
        headers['cwd'] = os.path.dirname(
            os.path.join(os.path.curdir, file_loc))

        if not include_headers:
            headers = {}

        if custom_headers != None:
            headers.update(custom_headers)

        try:
            output = process_template(
                headers, markdown, env=self.env, name="included file", filename=file_loc)
            return output
        except jinja2.exceptions.TemplateSyntaxError as error:
            log.error("Jinja2 error processing included file {}: {} at lineno {} for file {}".format(
                file_loc, error.message, error.lineno, filename=error.filename))
            log.error("Removing markdown for included file {}".format(file_loc))
            log_jinja2_error(markdown, error)
            log.error(traceback.format_exc())
            return ""
        except Exception as e:
            log.error(
                "Received exception when processing markdown for included file {}: {}".format(file_loc, e.args))
            log.error(
                "Removing markdown for included file {}".format(file_loc))
            log.error(traceback.format_exc())
            return ""

    def setup_plotly_template(self, template, colors):
        """ Setup the plotly template based on the table_styles template header
        """
        if 'charts' in template:
            log.info(f"{self.time()}: Customising chart template")
            charts = template['charts']
            # Translate colours for the template
            for l in ['colorway']:
                if l in charts:
                    for i in range(len(charts[l])):
                        if colors.getcolor(charts[l][i]):
                            charts[l][i] = '#' + colors.getcolor(charts[l][i])
                        elif test_color(charts[l][i]):
                            charts[l][i] = '#' + charts[l][i]


            plotly_template = dict(
                layout=go.Layout(template['charts'])
            )
            pio.templates["reportranger"] = plotly_template

            log.info(f"{self.time()}: Before set static plotly template")
            pio.templates.default = 'plotly_white+reportranger'
        else:
            plotly_template = 'plotly_white'
            pio.templates.default = 'plotly_white'

        self.env.set_static("plotly_template", plotly_template)

    def _dataframe_from_data(self, data, labels=['number', 'stage', 'category']):
        frames = []
        # Concatenate the data frames
        for i in data:
            df = pd.DataFrame(
                {
                    labels[0]: data[i].values(),
                    labels[1]: data[i].keys()
                }
            )
            df[labels[2]] = i
            frames.append(df)

        dataframe = pd.concat(frames, axis=0)
        return dataframe

    def bar_chart(self, description, data, update_layout=None, update_traces=None, *args, **kwargs):
        """ Simple vertical bar chart that is {column: value}
        """
        multi = False
        # See if we have multiple categories
        for i in data:
            if type(data[i]) is dict:
                multi = True
                break

        if multi:
            dataframe = self._dataframe_from_data(
                data, ['value', 'index', 'category'])
            figure = px.bar(dataframe, x="index", y="value",
                            color="category", *args, **kwargs)
        else:
            dataframe = pd.Series(data=data)

            figure = px.bar(dataframe, *args, **kwargs)
            figure.update_layout(showlegend=False)
        return self.fig(description, figure, update_layout, update_traces)

    def funnel_chart(self, description, data, *args, **kwargs):

        multi = False
        # See if we have multiple categories
        for i in data:
            if type(data[i]) is dict:
                multi = True
                break

        if multi:
            dataframe = self._dataframe_from_data(data)
            figure = px.funnel(dataframe, x="number", y="stage",
                               color="category", *args, **kwargs)
        else:
            dataframe = pd.DataFrame(
                {
                    'number': data.values(),
                    'stage': data.keys()
                }
            )

            figure = px.funnel(dataframe, x="number",
                               y="stage", *args, **kwargs)

        return self.fig(description, figure)

    def polar_bar_chart(self, description, data, colors=None, range=None, *args, **kwargs):
        """ Polar chart. data is a dict {category: value}, colors is a map {value:color}

        This function exists cause I really like the stacked colours for compliance work.
        """
        direction = []
        value = []
        maturity = []

        for category, level in data.items():
            level = float(level)
            if level <= 0:
                direction.append(category)
                value.append(0)
                maturity.append('1')
            else:
                if level > 100:
                    log.warn(
                        "Level {} passed to polar_bar_chart > 100".format(level))
                else:
                    cl = 1
                    while level > 0:
                        direction.append(category)
                        if level >= 1:
                            value.append(1)
                        else:
                            value.append(level)
                        maturity.append(str(cl))
                        cl += 1
                        level -= 1

        dataframe = pd.DataFrame(data={
            'direction': direction, 'value': value, 'maturity': maturity
        })

        if 'colors':
            kwargs['color_discrete_map'] = colors
            kwargs['color'] = 'maturity'

        figure = px.bar_polar(dataframe, r='value',
                              theta='direction', *args, **kwargs)

        update_layout = {'showlegend': False, 'polar_radialaxis_dtick': 1,
                         'polar_radialaxis_showticklabels': False,
                         'polar_radialaxis_showline': False
                         }

        if range:
            update_layout['polar_radialaxis_range'] = range

        figure.update_layout(**update_layout)

        return self.fig(description, figure)

    def chart(self, chart, description, data, update_layout=None, update_traces=None, *args, **kwargs):
        """ Generalist chart function
        """
        multi = False
        # See if we have multiple categories
        for i in data:
            if type(data[i]) is dict:
                multi = True
                break

        if multi:
            dataframe = self._dataframe_from_data(
                data, ['value', 'index', 'category'])
            figure = chart(dataframe, *args, **kwargs)
        else:
            df = pd.DataFrame(
                {
                    'index': data.keys(),
                    'value': data.values()
                }
            )
            figure = chart(df, *args, **kwargs)
        return self.fig(description, figure, update_layout, update_traces)

    def fig(self, description, figure, update_layout=None, update_traces=None):
        nfig = self.env.get('nfig')
        self.env.set_static('nfig', nfig + 1)
        filename = 'screenshots/fig{}.{}'.format(int(nfig), self.figformat)
        log.info("Generating figure {}: {} to file {}".format(
            int(nfig), description, filename))
        filepath = Path(filename)
        cwdpath = Path(os.path.curdir)
        if cwdpath not in filepath.parents:
            log.warn(
                "Screenshot figure path {} doesn't seem to be in cwd".format(filepath))
            return ''

        if update_layout:
            figure.update_layout(**update_layout)
        if update_traces:
            figure.update_traces(**update_traces)

        figure.write_image(filename)
        return '![{}]({})'.format(description, filename)

    def _build_markdown_headers(self, headers):
        # Headers. This is a separate function because it might be modified or taken away by specific formatters.
        markdown = '''---\n'''
        markdown += headers
        markdown += "\n...\n\n"
        return markdown

    def _warn_in_text(self, templateheaders, env, text):
        ''' Throw a log warning if the warn list in templateheaders or env is in the text
        '''
        warn = []

        # Generate the warning list. This combines the lists in the template as well as the report (if it's there)

        # Get the list from the template
        if 'warn' in templateheaders:
            log.info("Warning on {}".format(templateheaders['warn']))

            if isinstance(templateheaders['warn'], list):
                warn = templateheaders['warn']
            else:
                log.warn(
                    "Warn header in the template front matter is not a list. Warning function won't work.")

        # Get the list from the report headers
        if 'warn' in env:
            if isinstance(env['warn'], list):
                warn = [*warn, *env['warn']]
            else:
                log.warn(
                    "Warn header in the report front matter is not a list. Warning function won't work.")

        # Go through the final output and warn on the line if the warning text is found
        for warntext in warn:
            if text.find(warntext):
                matched_lines = [line for line in text.split(
                    '\n') if warntext.lower() in line.lower()]
                for line in matched_lines:
                    log.warn(
                        "Found '{}' in the following line: {}".format(warntext, line))


    def _build_markdown(self, templatemarkdown):
        # A giant string to put all the output markdown into
        markdown = ""

        log.info(f"{self.time()}: Outputting markdown")
        markdown += self._build_markdown_headers(self.headers())

        env = self.env.get_env()


        try:
            j2template = jinja2.Template(templatemarkdown)
            processedtemplate = j2template.render(env)
            markdown += processedtemplate

            # Content assistant parsing
            output = self.env.get('ca').parse_register(self, markdown)

            self._warn_in_text(self.templateheaders, env, output)


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

        return output

    def output(self, markdown, outputfile=''):
        output = self._build_markdown(markdown)

        log.info("Writing Markdown")

        with open(outputfile, 'w') as fh:
            fh.write(output)
        log.info("Finished writing")

        return output
