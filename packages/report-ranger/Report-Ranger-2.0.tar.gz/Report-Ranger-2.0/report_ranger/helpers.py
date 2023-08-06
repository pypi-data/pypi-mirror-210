import cerberus
import logging

log = logging.getLogger(__name__)


def make_list(value):
    """ If it's a list, return value, otherwise return [value]
    """
    if type(value) is list:
        return value
    else:
        return [value]


def filter_rows(table, validation, return_fails=False):
    """Filter table rows based on the supplied validation
    """
    validator = cerberus.Validator()
    validator.allow_unknown = True
    validator.schema = validation
    new_table = []
    for row in table:
        if validator.validate(row):
            if not return_fails:
                new_table.append(row)
        else:
            if return_fails:
                new_table.append(row)
    return new_table


def sort_table(table, column, mapper=None, reverse=False):
    """Sort the table based off content in the chosen column.
    """
    if len(table) == 0:
        return table
    if mapper:
        return sorted(table, key=lambda d: mapper[d[column]] if d[column] in mapper else d[column], reverse=reverse)
    return sorted(table, key=lambda d: d[column], reverse=reverse)


def table_aggregate_value(table, column, aggtype, map_values=None):
    """Get aggregate value from the supplied table.

    aggtype can be 'min', 'max', 'mean', 'sum', or 'count'.
    map_values is a dict {value:mapping}. It will substitute value for mapping if found in the column.
    """
    val = None
    sum = 0
    count = 0
    for row in table:
        if type(row) is dict:
            if column in row:
                cv = row[column]
            else:
                continue
        else:
            if column >= 0 and column < len(row):
                cv = row[column]
            else:
                continue

        if map_values:
            if cv in map_values:
                cv = map_values[cv]

        if aggtype == 'min':
            if val == None or cv < val:
                val = cv
        elif aggtype == 'max':
            if val == None or cv > val:
                val = cv
        elif aggtype == 'count':
            count += 1
        elif aggtype == 'sum':
            sum += cv
        elif aggtype == 'mean':
            sum += cv
            count += 1
        else:
            log.warn(
                "Invalid aggtype encountered for table_aggregate_value: {}".format(aggtype))
            return None

    if aggtype == 'min' or aggtype == 'max':
        return val
    if aggtype == 'count':
        return count
    if aggtype == 'sum':
        return sum
    if aggtype == 'mean':
        return sum / count

    return None


def _get_aggregate(cgbv, prevrows, groupby, dict_list, agg, map_values):
    nr = cgbv

    # Do the aggregation
    for column, aggtype in agg.items():
        if dict_list:
            nr["{}_{}".format(column, aggtype)
               ] = table_aggregate_value(prevrows, column, aggtype, map_values)
        else:
            nr.append(table_aggregate_value(
                prevrows, column, aggtype, map_values))
    return nr


def table_aggregate(table, groupby, agg, map_values=None):
    """Get aggregate information from a table with groupings specified in groupby.

    groupby should be either a single column or a list of columns. If the table is a list of dicts the columns should be
    column heading names. If it is a list of lists it should be the index number of the table.
    """

    # Go backwards sorting with groupby so that we have everything sorted
    if type(groupby) is str or type(groupby) is int:
        # If it's a string make it a list of one
        groupby = [groupby]

    st = table
    for gb in reversed(groupby):
        st = sort_table(st, gb)

    if len(st) == 0:
        return []

    if type(st[0]) is dict:
        dict_list = True
    else:
        dict_list = False

    # We now have everything sorted by the groupby columns. Now we need to get the aggregates
    if dict_list:
        cgbv = {}
        for gb in groupby:
            cgbv[gb] = st[0][gb]
    else:
        cgbv = []
        for gb in groupby:
            cgbv.append(st[0][gb])
    prevrows = []

    new_table = []

    for row in st:
        for i in groupby:
            if row[i] != cgbv[i]:
                # We have a new row
                if len(prevrows) > 0:
                    # We're not at the start of the table so we've hit the next block to aggregate
                    # Initialise the new row with what's in groupby

                    new_table.append(_get_aggregate(
                        cgbv, prevrows, groupby, dict_list, agg, map_values))
                # Initialise the new values
                if dict_list:
                    cgbv = {}
                    for gb in groupby:
                        cgbv[gb] = row[gb]
                else:
                    cgbv = []
                    for gb in groupby:
                        cgbv.append(row[gb])
                prevrows = []

        # Add the row to prevrows
        prevrows.append(row)

    new_table.append(_get_aggregate(
        cgbv, prevrows, groupby, dict_list, agg, map_values))

    return new_table


def table_to_dict(table, keyindex=None, valindex=None, keys=None, default=None):
    """ Convert tabular data into a dict of key:value pairs taking the keys and values from the keyindex and valindex columns.

    This is used for feeding tabular data into charts.
    keys provides a filter for keys. If default is set, then keys that don't appear in the table will appear in the returned dict
    with the default value.
    """
    d = {}

    if keys != None and default != None:
        for k in keys:
            d[k] = default

    if len(table) == 0:
        # We have an empty table
        if keys != None and default != None:
            for key in keys:
                d[key] = default
            return d
        else:
            return {}

    if keyindex == None:
        if len(table[0]) < 1:
            log.warning(
                "keyindex for table_to_dict is not set and the first row has less than 1 value so it cannot be automatically set")
            return {}
        keyindex = list(table[0].keys())[0]

    if valindex == None:
        if len(table[0]) < 2:
            log.warning(
                "valindex for table_to_dict is not set and the first row has less than 2 values so it cannot be automatically set")
            return {}
        valindex = list(table[0].keys())[1]

    for row in table:
        if keyindex not in row or valindex not in row:
            continue
        if keys:
            if row[keyindex] not in keys:
                continue
        d[row[keyindex]] = row[valindex]

    return d


def tables_outer_join(table1, table2, column1, column2=None):
    """ Match the data in column1 for table1 to data in column2 for table2 to perform an outerjoin on two tables
    Tables can be either lists of lists or lists of dicts. If it is a list of lists then the column should be an int, otherwise
    it should refer to the dictionary key of the column.
    If column2 is not specified, column1 will be used for table2 as well.
    """
    new_table = []
    if len(table1) == 0:
        return []
    if type(table1[0]) is dict:
        dict_list = True
    else:
        dict_list = False

    for r1 in table1:
        for r2 in table2:
            if column2 != None:
                if r1[column1] == r2[column2]:
                    if dict_list:
                        new_table.append(r1 | r2)
                    else:
                        new_table.append(r1 + r2)
            else:
                if r1[column1] == r2[column1]:
                    if dict_list:
                        new_table.append(r1 | r2)
                    else:
                        new_table.append(r1 + r2)

    return new_table


def table_separate_column(table, column, separator, columnmapper=None, separatormapper=None, separator_list=None, dict_list=False):
    """ Separate out the content of one column into separate columns for each unique value of the content in separator.
    This is useful for displaying compliance stuff. For instance, you have a list of Essential 8 controls in a spreadsheet
    and you want a list of controls for each maturity level. You can use this to show them in three columns.

    If the content of separator is integers the output will be in order of the integer.

    columnmapper is used to change the content of the column in the output. For instance changing "Passed"/"Failed" to "P"/"F".
    separatormapper can be used in the same way for the separator. This can be used to map two pieces of content to the same
    thing or to map content to integers to have them ordered in the right way.
    separator_list can manually force the columns by using this list.
    """
    if separator_list is not None:
        separators = separator_list
    else:
        separators = []
        # First we need to go through and get all the separators
        for row in table:
            if separatormapper is not None and row[separator] in separatormapper:
                if separatormapper[row[separator]] not in separators:
                    separators.append(separatormapper[row[separator]])
            elif row[separator] not in separators:
                separators.append(row[separator])

        # We need to get the integers out and put them at the start in order
        orderedsep = []
        otherseps = []
        for sep in separators:
            if type(sep) is int:
                orderedsep.append(sep)
            else:
                otherseps.append(sep)

        orderedsep = sorted(orderedsep)
        separators = orderedsep + otherseps

    # We now have a list of separators with ints ordered at the front
    # To get the columns we have a dict of lists.
    columns = {}
    for sep in separators:
        columns[sep] = []

    # Let's put the column contents into the above data structure
    for row in table:
        if separatormapper is not None and row[separator] in separatormapper:
            sep = separatormapper[row[separator]]
        else:
            sep = row[separator]

        if sep not in separators:
            continue

        if columnmapper is not None and row[column] in columnmapper:
            col = columnmapper[row[column]]
        else:
            col = row[column]

        columns[sep].append(col)

    # We now have the columns in order. Create a new table.
    new_table = []
    finished = False
    while not finished:
        finished = True
        if dict_list:
            new_row = {}
        else:
            new_row = []

        for sep in columns:
            if len(columns[sep]) == 0:
                nc = ""
            else:
                nc = columns[sep].pop(0)
                finished = False

            if dict_list:
                new_row[sep] = nc
            else:
                new_row.append(nc)

        if not finished:
            new_table.append(new_row)

    return new_table


def table_separate_column_groups(table, groupby, column, separator, columnmapper=None, separatormapper=None, separator_list=None, dict_list=False):
    """table_separate_column but it 

    groupby is used to separate out into groups. This way each group will start at the same level.
    """
    # Get a list of groups
    groups = {}
    for row in table:
        if groupby not in row:
            gb = None
        else:
            gb = row[groupby]
        if gb == "None":
            gb = 'default_table_separate_column_groups'
        if gb not in groups:
            groups[gb] = []
        groups[gb].append(row)

    new_table = []
    for gb, group in groups.items():
        new_table += table_separate_column(
            group, column, separator, columnmapper, separatormapper, separator_list, dict_list)
    return new_table


def table_add_row(table, row=None, index=None):
    """Add a row to the table. If row is None it adds an empty row. If index is None it adds it to the end.
    """
    if row == None:
        if len(table) == 0:
            return [[]]
        if type(table[0]) is dict:
            row = {}
        else:
            row = []

    if index > len(table):
        table.append(row)
    else:
        table.insert(index, row)
    return table


def separate_sequences(sequence):
    """Separates out a dict into repeated keys. Useful for coloured charts.

    For example:
      {'a':'1', 'b':'2'}
    becomes
      {'a':{'a':'1'}, {'b':{'b':'2'}}
    """

    newdict = {}
    for k, i in sequence.items():
        newdict[k] = {k: i}
    return newdict
