from copy import deepcopy
import logging

log = logging.getLogger(__name__)


class Environment:
    """ Store environment variables

    This class operates as a stack. You can push a bunch of variables onto the stack when you go down a layer
    (say when a file is included). You can then pop off the stack when we finish with that file.
    """

    def __init__(self, other=None):
        self._static = {}
        self._variable = [{}]
        self._private = [{}]

        if other != None:
            # We can duplicate another environment. This involved deep copying so we don't accidentally
            # modify the other environment
            self._static = deepcopy(other._static)
            self._variable = deepcopy(other._variable)

    def set_private(self, key, value):
        # Set the private variable in the most recent stack
        # _private allows a set of hidden variables that can be kept track of through files
        # These variables cannot be accessed within the report
        self._private[-1][key] = value
    
    def get_private(self, key):
        # Go backwards through self._private looking to see if the variable is there
        for ve in reversed(self._private):
            if key in ve:
                return ve[key]


    def set_static(self, key, value):
        '''Set a static variable in the environment

        Static variables cannot be overwritten, they always win in a clash. This means they survive pushes and pops.
        '''
        self._static[key] = value

    def set_variable(self, key, value):
        '''Set a variable in the environment

        This variable will be set in the current layer of the stack. For instance, if pop is called the variable is lost.
        '''
        # When we set a variable we only set it to the last piece of the stack
        self._variable[-1][key] = value

    def set_variables(self, env=dict()):
        '''Set multiple variables in the environment

        These variables should be passed as a dict.
        '''
        self._variable[-1].update(env)

    def get(self, key):
        '''Get the variable with the key "key".'''
        # Static wins in a variable clash, so see if it's there first
        if key in self._static:
            return self._static[key]

        # Go backwards through self._variable looking to see if the variable is there
        for ve in reversed(self._variable):
            if key in ve:
                return ve[key]

        # We haven't found this variable
        return None

    def get_env(self):
        '''Get the current variables from the stack

        This function returns a dict full of key value pairs representing the current state of the environment.'''
        # We get the environment by overlaying each layer of the stack and then returning
        # what is at the end.
        env = {}
        for varenv in self._variable:
            env.update(varenv)

        # Static always wins, so finally overlay that
        env.update(self._static)
        return env

    def push(self, newenv={}):
        '''Add a layer to the stack

        This allows an isolated environment, where the variables you set can be removed once it's done.

        For instance, if you include a file, the headers of the included file will not affect the outer file.
        '''
        self._variable.append(newenv)
        self._private.append({})

    def pop(self):
        '''Take a layer off the stack

        This will remove all variables that have been added since the last time push() was called. Overwritten variables
        will be replaced with what was there before.
        '''
        self._variable.pop()
        self._private.pop()
