import re
import logging
from report_ranger.utils.mdread import process_template
from report_ranger.helpers import filter_rows as fr


log = logging.getLogger(__name__)


def style_text_match(style_text, text, regexlist=None):
    ''' See if the text is in the style_text dict and match it to stylelist '''
    if type(text) is not str:
        return None
    if not regexlist:
        regexlist = [(re.compile(ts), cf)
                     for (ts, cf) in style_text.items()]

    # We have to go through each regex to see if it matches
    for ts in regexlist:
        # Regexes are in a tuple (regex, cf)
        if ts[0].match(text):
            return ts[1]


class Table:
    """ This class holds a table to be used in output formatters. It will hold things like table contents, headings, alignment, widths

    The table has the following state:
    table: A list of lists containing the content of each cell, always guaranteed to be square. Table will pad if necessary.
    cellstyles: A list of lists containing a string with the style of each square, always guaranteed be the same size of table.
    colalign: A list of strings, either 'l', 'c', 'r', 'j' or an empty string. Guaranteed to be the width of the table.
    cellalign: A list of lists of strings,  either 'l', 'c', 'r', 'j' or an empty string, always guaranteed be the same size of table.
    colspan: A list of lists containing numbers where each number >= 1 or -1 if the cell is overwritten, always guaranteed be the same size of table. This is for when you would like a cell to overwrite the next column.
    rowspan: A list of lists containing numbers where each number >= 1 or -1 if the cell is overwritten, always guaranteed be the same size of table. This is for when you would like a cell to overwrite the next row.
    colwidths: A single list of numbers. Guaranteed to be the width of the table. This corresponds to the width of each cell.
    """

    def _pad_matrix(self, m, width=0, height=0, pad_value=''):
        """ Pad the matrix m (a list of lists) to the set width and height with the pad_value.

        If the width and height is not set, make sure that the matrix m is rectangular, with each row being the same length by padding them with pad_value.
        """
        if m == None:
            m = []
            for i in range(height):
                m += [[pad_value]*width]
            return m

        if height == 0:
            height = len(m)

        if width == 0:
            for i in m:
                mw = len(i)
                if mw > width:
                    width = mw

        for row in m:
            if len(row) < width:
                row += [pad_value]*(width-len(row))
            if len(row) > width:
                row = row[:width]

        if len(m) < height:
            for i in range(height-len(m)):
                m += [[pad_value]*width]
        elif len(m) > height:
            m = m[:height]

        return m

    def _pad_list(self, l, width, pad_value=''):
        """ Pad the list l to the required width with pad_value """
        if l == None:
            l = []

        if len(l) < width:
            l += [pad_value]*(width-len(l))

        return l
    
    def _clear_table(self):
        self.table = [[]]
        self.width = 0
        self.height = 0
        self.cellstyles = []
        self.colalign = []
        self.cellalign = []
        self.colspan = []
        self.rowspan = []
        self.colwidths = []
    
    def _markdown_to_matrix(self, markdown):
        """ Convert the markdown string into a table.
        
        Returns """
        re_tablecells = re.compile(r'(\||^)([^\|]*)(?=(\||$))')
        re_isheaderline = re.compile(r'^\|?(\s*:?-+:?\s*\|?)*\s*$')
        re_hastablecells = re.compile(r'\|')
        lines = markdown.splitlines()
        matrixtable = []
        colalign = []
        has_heading = False
        for line in lines:
            if not re_hastablecells.match(line):
                continue
            cells = re_tablecells.findall(line)
            # Is it the heading line?
            if re_isheaderline.match(line):
                has_heading = True
                for cell in cells:
                    ic = cell[1].strip()
                    if len(ic) == 0:
                        continue
                    if ic[0] == ':':
                        if ic[-1] == ':':
                            colalign.append('c')
                        else:
                            colalign.append('l')
                    elif ic[-1] == ':':
                        colalign.append('r')
                    else:
                        colalign.append('l')
            else:
                row = []
                # Check to see if the first line has a |, if so skip the last one
                if cells[0][0] == '|':
                    endpipe = True
                for cell in cells:
                    row.append(cell[1].strip())
                if endpipe:  # Kill last empty cell
                    if row[-1] == '':
                        row = row[:-1]
                matrixtable.append(row)

        return matrixtable, colalign, has_heading

    def _process_list_of_dicts(self, table, append_column, env):
        """Convert a list of dicts to a matrix with a header line
        
        append_column will be appended to the end of each row.
        """
        
        tableheadings = None

        for r in range(len(table)):
            if not isinstance(table[r], dict):
                log.warn(
                    f"Table defined as dicts has something which is not a dict, replacing with empty row: {table[r]}")
                table[r] = dict()

            # Process append_column
            if isinstance(append_column, dict):
                append_column_done = True
                newcols = {}
                for key in append_column:
                    newcols[key] = process_template(
                        table[r], append_column[key], env=env, name="append_column")
                table[r].update(newcols)

        tableheadings = []

        # Get the headings from the dicts
        for row in table:
            for h in row.keys():
                if h not in tableheadings:
                    tableheadings.append(h)

        newtable = []

        # Headings will always be the first row of the new table
        newtable.append(tableheadings)
        for row in table:
            newrow = []
            for h in tableheadings:
                if h in row.keys():
                    newrow.append(row[h])
                else:
                    # This heading isn't in this row, add a blank
                    newrow.append("")
            newtable.append(newrow)
        return newtable, tableheadings
        

    def __init__(self, table, env=None, filter_rows=None, header=[], headings=None, cellstyles=None, colstyles=None, colalign=None, cellalign=None, colspan=None, rowspan=None, colwidths=None, append_column=None, colpicker=None, rowpicker=None, style_text={}):
        # Is it just a markdown table?
        if isinstance(table, str):
            table, newcolalign, has_heading = self._markdown_to_matrix(table)

            # Append colalign if it's not complete
            if colalign == None:
                colalign = []
            colalign += newcolalign[len(colalign):]
            
            # Set a heading row if it has one
            if has_heading == True and headings == None:
                headings = 'top'

        # The table now has to be a list. If it is not a list, warn and skip
        if not isinstance(table, list):
            log.warn(f"Table not a list. Trying to make a table out of {table}.")
            self._clear_table()
            return
        
        # If there's no rows there's nothing to display
        if len(table) == 0:
            log.warn("Table has no rows, skipping table.")
            self._clear_table()
            return

        # We perform validation now, after converting a blank markdown table and before converting list of dicts to list of lists
        if filter_rows:
            table = fr(table, filter_rows)
            if len(table) == 0:
                log.warning("Table has no rows after filtering")
                self._clear_table()
                return
            
        append_column_done = False

        # We are representing the table in a dict form and we need to translate that into a table. For instance:
        # affected_hosts:
        # - hostname: host.com
        #   port: 80
        # - hostname: host2.com
        #   port: 80
        tableheadings = None
        if isinstance(table[0], dict):
            table, tableheadings = self._process_list_of_dicts(table, append_column, env)
            append_column_done = True

        # We should now have a list of lists. Let's just make sure!
        newtable = []
        for row in table:
            if not isinstance(row, list):
                log.warn(f"Table row not a list. Skipping table row: {row}")
            else:
                newtable.append(row)
        table = newtable

        # If we have a list of lists, then append_column won't be done yet. Let's do that.
        if append_column and not append_column_done:
            if isinstance(append_column, list):
                for row in range(len(table)):
                    rowdict = {}
                    # We need to index for each column
                    for col in range(len(row)):
                        rowdict['col' + str(col)] = table[row][col]
                    for key in range(len(append_column)):
                        table[row].append(process_template(
                            rowdict, append_column[key], env=env, name="append_column"))
            elif isinstance(append_column, dict):
                log.warning(f"append_column a dict for a table of lists, skipping: {append_column}")
            else:
                log.warning(f"append_column not a list, skipping: {append_column}")

        # Pad everything
        self.table = self._pad_matrix(table, pad_value='')
        width, height = len(table[0]), len(table)
        
        self.width, self.height = width, height

        # Handle rowpicker and colpicker
        # Rowpicker first, since filtering rows is easier and quicker than filtering columns
        if rowpicker != None and rowpicker != []:
            if not isinstance(rowpicker, list):
                log.warn("Rowpicker variable not a list, ignoring.")
            else:
                newtable = []
                for row in rowpicker:
                    if not isinstance(row, int):
                        log.warn(
                            "Entry in rowpicker was not int. Found: {}".format(row))
                    elif row < 0 or row >= len(self.table):
                        log.warn("Entry in rowpicker outside the range of the table length {}. Found: {}".format(
                            len(self.table), row))
                    else:
                        newtable.append(self.table[row])
                self.table = newtable
                self.height = len(self.table)

        if colpicker != None and colpicker != []:
            if not isinstance(colpicker, list):
                log.warn("Colpicker variable not a list, ignoring.")
            else:
                newtable = []
                for i in range(len(self.table)):
                    newtable.append([])
                for col in colpicker:
                    if isinstance(col, str):
                        # Check to see if we're referring to a column heading
                        if col in self.table[0]:
                            col = self.table[0].index(col)
                        else:
                            log.warn(
                                "Entry in colpicker is a string but not a column heading. Found: {}".format(col))
                            continue
                    elif not isinstance(col, int):
                        log.warn(
                            "Entry in colpicker was not int. Found: {}".format(col))
                        continue

                    if col < 0 or col >= len(self.table[0]):
                        log.warn("Entry in colpicker outside the range of the table length {}. Found: {}".format(
                            len(self.table[0]), col))
                        continue

                    for trow in range(len(self.table)):
                        newtable[trow].append(self.table[trow][col])
                self.table = newtable

                if len(self.table) > 0:  # Do we actually still have a table?
                    self.width = len(self.table[0])
                else:
                    self.width = 0

        # If there's no table anymore due to rowpicker or colpicker then get rid of the rest, just cancel it out
        if self.width == 0:
            log.warn("rowpicker and colpicker resulted in an empty table.")
            self._clear_table()
            return

        # Put in the header if it's been supplied
        if header != []:
            if isinstance(header, list):
                # If there's tableheadings from a dict already, remove them
                if tableheadings:
                    self.table = [header] + self.table[1:]

                else:
                    self.table = [header] + self.table

                # Do we need to repad?
                if width != len(header):
                    self.table = self._pad_matrix(self.table, pad_value='')
                    self.width = len(self.table[0])

                self.height = len(self.table)
            else:
                log.warn(
                    "Header of the table is not a list. Trying to add {}.".format(header))

        # colalign must be one of 'l' 'c' 'r' or 'j' or an empty string
        colalign = self._pad_list(colalign, self.width, '')
        for i in range(self.width):
            if colalign[i] not in 'lcrj':
                colalign[i] = ''

        cellalign = self._pad_matrix(cellalign, self.width, self.height, '')
        for i in range(self.height):
            for j in range(self.width):
                if cellalign[i][j] not in 'lcrj':
                    cellalign[i][j] = ''
        self.colalign = colalign
        self.cellalign = cellalign

        # Handle colspan and rowspan
        colspan = self._pad_matrix(
            colspan, self.width, self.height, 1)  # Pad to size of table
        rowspan = self._pad_matrix(
            rowspan, self.width, self.height, 1)  # Pad to size of table

        # Handle colspan
        for i in range(self.height):
            for j in range(self.width):
                if not int(colspan[i][j]):  # Validate it's an int
                    colspan[i][j] = 1
                if colspan[i][j] >= 1:  # We have a colspan!
                    # Does it go over the side of the table?
                    if j + colspan[i][j] > self.width:
                        colspan[i][j] = self.width - j  # Snip it off
                    # We blank out the rest of the span
                    for span in range(1, colspan[i][j]):
                        colspan[i][j+span] = -1

        # Handle rowspan. This is equivalent of the above, just swapping row and column
        for i in range(self.height):
            for j in range(self.width):
                if not int(rowspan[i][j]):
                    rowspan[i][j] = 1
                if rowspan[i][j] >= 1:
                    if i + rowspan[i][j] > self.height:
                        rowspan[i][j] = self.height - i
                    for span in range(1, rowspan[i][j]):
                        rowspan[i+span][j] = -1
        self.colspan = colspan
        self.rowspan = rowspan

        self.colwidths = self._pad_list(colwidths, self.width, 0)

        cellstyles = self._pad_matrix(cellstyles, self.width, self.height, '')

        # Allow the 'left', 'top', and 'left-top' headings settings
        if not isinstance(headings, list) and not headings == None:
            headingslist = headings.split('-')
            if 'left' in headingslist:
                for row in cellstyles:
                    if row[0] == '':
                        row[0] = 'h'
            if 'right' in headingslist:
                for row in cellstyles:
                    if row[-1] == '':
                        row[-1] = 'h'
            if 'top' in headingslist:
                for i in range(len(cellstyles[0])):
                    if cellstyles[0][i] == '':
                        cellstyles[0][i] = 'h'
            if 'bottom' in headingslist:
                for i in range(len(cellstyles[-1])):
                    if cellstyles[-1][i] == '':
                        cellstyles[-1][i] = 'h'
        else:
            cellstyles = self._pad_matrix(
                cellstyles, self.width, self.height, '')

        # Do the col styles if set. Go through and set each entire column in cellstyles as per what is set by the user in colstyles.
        # Note that this won't overwrite headers
        if colstyles:
            for row in range(len(cellstyles)):
                for col in range(len(cellstyles[row])):
                    # Don't overwrite existing cellstyles, only fill in if it's blank
                    if (cellstyles[row][col] == '' or cellstyles[row][col] == None) and col < len(colstyles) and colstyles[col] and colstyles[col] != '':
                        cellstyles[row][col] = colstyles[col]

        # If there's headings text sync then add them
        if style_text:
            # Get all the regexes
            stregexlist = [(re.compile(ts), cf)
                           for (ts, cf) in style_text.items()]

        for r in range(self.height):
            for c in range(self.width):
                # First check to see if there's a style in cellstyles
                if type(cellstyles[r][c]) is dict:
                    # If it's a dict, treat it as a style text dict
                    st_return = style_text_match(
                        cellstyles[r][c], self.table[r][c])
                    if st_return:
                        cellstyles[r][c] = st_return
                    else:
                        cellstyles[r][c] = ''
                elif type(cellstyles[r][c]) is str and cellstyles[r][c] != '':
                    # Leave it as is if there's something filled in
                    continue
                elif style_text:
                    # Now check master style_text
                    cellstyle = style_text_match(
                        style_text, self.table[r][c], stregexlist)
                    if cellstyle:
                        cellstyles[r][c] = cellstyle
                else:
                    cellstyles[r][c] = ''

        self.cellstyles = cellstyles
