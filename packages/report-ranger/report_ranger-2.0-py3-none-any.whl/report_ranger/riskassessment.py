from report_ranger.errors import InputError
import logging

log = logging.getLogger(__name__)


def combine_matrix(matrix, next_matrix):
    """ Combine two risk matrices where the final risk in one is fed into the next. It is called recursively """

    # Create a shallow copy of the matrix so we're not changing what is being passed to the function
    newmatrix = matrix.copy()

    for stage in newmatrix.keys():
        # See if we're at the end, otherwise recurse
        if isinstance(newmatrix[stage], dict):
            # We're in a dict so recurse
            newmatrix[stage] = combine_matrix(newmatrix[stage], next_matrix)
        else:
            # This is a reference to the next matrix so add it in
            if newmatrix[stage] not in next_matrix:
                log.error(
                    "Risk matrix validation error: In validating the risk assessment, we have not been able to find {} in the next matrix stage. Options are {}.".format(
                        newmatrix[stage], next_matrix.keys()))
                raise Exception("In validating the risk assessment, we have not been able to find {} in the next matrix stage. Options are {}.".format(
                    newmatrix[stage], next_matrix.keys()))
            else:
                # Add what's in the next matrix so this field is combined
                newmatrix[stage] = next_matrix[newmatrix[stage]]

    return newmatrix


def validate_matrix(matrix, stages, risks):
    """ Validates that each combination of stages is in the final matrix and the risks all make sense """
    if len(stages) == 0:
        log.error(
            "Risk matrix validation error: Excessively deep risk matrix found. We have the following part of the matrix, but we're out of risk stages. {}".format(
                matrix))
        # We've gotten to the end of stages, but we still have a matrix. This isn't good.
        raise Exception("Excessively deep risk matrix found. We have the following part of the matrix, but we're out of risk stages. {}".format(
            matrix))

    current_stage = stages[0]
    future_stages = stages[1:]

    for stage in current_stage['ratings']:
        if stage not in matrix:
            log.error(
                "Risk matrix validation error: Stage {} not found in the remaining matrix. All we have is {}".format(
                    stage, matrix.keys()))
            raise Exception("Stage {} not found in the remaining matrix. All we have is {}".format(
                stage, matrix.keys()))

        elif len(future_stages) == 0:
            if matrix[stage] not in risks:
                log.error(
                    "Risk matrix validation error: Could not find {} in the risks. The risks we have are {}".format(
                        matrix[stage], risks))
                raise Exception("Could not find {} in the risks. The risks we have are {}".format(
                    matrix[stage], risks))
            else:
                # Validate the next level of the matrix
                return validate_matrix(matrix[stage], future_stages, risks)


def get_risk(matrix, stages, headers):
    """
    A recursive assisting function that goes through the risk assessment tree to get the final risk
    """
    if len(stages) == 0:
        return matrix

    # Make sure that the next stage is actually in the headers
    if stages[0]['id'] not in headers:
        log.warn("{} not found in the headers of the vulnerability file as required by the template. Assigning risk as None.".format(
            stages[0]['id']))
        return "None"

    stageval = headers[stages[0]['id']]

    # If the header for this stage is a list of length one then take that value
    if type(stageval) is list:
        if len(stageval) != 1:
            stageval = stageval[0]
        else:
            log.warn("{} in this vulnerability was a list rather than a string. Assigning risk as None.".format(
                stages[0]['id']))
            return "None"

    # If the value of the header isn't in the matrix, cast an alert
    if stageval not in matrix:
        log.warn("'{}' is not a valid value for {}. The selection is: {}".format(
            stageval, stages[0]['id'], stages[0]['ratings']))
        return "None"

    return get_risk(matrix[headers[stages[0]['id']]], stages[1:], headers)


class RiskAssessment:
    """
    Holds the risk assessment, allows easy application of the risk assessment
    Can be customised
    """

    def __init__(self, riskassessment):
        self.name = riskassessment['name']
        self.id = riskassessment['id']
        self.stages = riskassessment['stages']
        self.risks = ["None", "Closed"] + riskassessment['risks']
        self.methodology = riskassessment['methodology']
        if 'mapping' in riskassessment:
            self.mapping = riskassessment['mapping']
        else:
            self.mapping = {}

        if 'style_text' in riskassessment:
            self.style_text = riskassessment['style_text']
        else:
            self.style_text = {}

        matrix = riskassessment['matrix']

        # First we see if there's a split matrix, and if so combine them into one
        if isinstance(matrix, list):
            # We have a split matrix. Combine them together
            combinedmatrix = matrix[0]
            for next_matrix in matrix[1:]:
                combinedmatrix = combine_matrix(combinedmatrix, next_matrix)

            self.matrix = combinedmatrix
        else:
            self.matrix = matrix

        # Validate the matrix
        validate_matrix(self.matrix, self.stages, self.risks)

        # Generate the table
        self.generate_riskmatrixtable()

    def get_risk(self, headers):
        """ Get the risk from the submitted risk assessment """

        if 'status' in headers and headers['status'] == 'Closed':
            return 'Closed'

        # Process the mappings
        for value, mapping in self.mapping.items():
            # We have to make sure we're not overwriting a value here
            if mapping not in headers and value in headers:
                headers[mapping] = headers[value]

        for stage in self.stages:
            # Make sure that the next stage is actually in the headers
            if stage['id'] not in headers:
                log.warn("{} not found in the headers of the vulnerability file as required by the template. Assigning risk as None.".format(
                    stage['id']))
                # Reset all stages to None if they're not there
                for s in self.stages:
                    if s['id'] not in headers:
                        headers[s['id']] = "None"
                return "None"

            if 'mapping' in stage:
                # Process the mappings
                for value, mapping in stage['mapping'].items():
                    if headers[stage['id']] == value:
                        headers[mapping] = headers[value]

        return get_risk(self.matrix, self.stages, headers)

    def generate_riskmatrixtable(self):
        """
        This displays a two stage risk matrix in a table. Note that it will only generate output if there are specifically 2 stages.
        """
        if len(self.stages) != 2:
            log.info(
                "Not auto generating a risk assessment table as there are not specifically 2 stages.")
            return ''

        sa = self.stages[0]
        sb = self.stages[1]
        theaders = [['thead'] * (len(sa['ratings']) + 1)]
        ratable = [[[sb['name'], sa['name']]] + sa['ratings']]
        sbratings = sb['ratings']
        sbratings.reverse()
        for sbrating in sbratings:
            rs = [sbrating]
            th = ['thead']
            for sarating in sa['ratings']:
                rs.extend(
                    [self.get_risk({sa['id']: sarating, sb['id']: sbrating})])
                th.extend(
                    ['t' + self.get_risk({sa['id']: sarating, sb['id']: sbrating}).lower().replace(' ', '')])
            ratable += [rs]
            theaders += [th]

        self.riskmatrixtable = ratable
