import re

###############################################################################
# From https://en.wikipedia.org/wiki/Lambda_calculus#Formal_definition
# Lambda expressions are composed of:
#   - variables v1, v2, …;
#   NOTE: we assume all argument variables will be single characters, when
#   processing we loop over the chars in the string. Any multi-char argument
#   variables will be treated as many single character variables.
#   - the abstraction symbols λ (lambda) and . (dot);

λ = 'λ'
dot = '.'


#   - parentheses ().
def paren_matched(string: str) -> str:
    count = 0
    for char in string:
        count += 1 if char == '(' else -1 if char == ')' else 0
        if count < 0:
            return False
    return count == 0


# To keep the notation of lambda expressions uncluttered, the following
# conventions are usually applied:
#   - Outermost parentheses are dropped: M N instead of (M N).
#   NOTE: python applications look like this M(N) not (M N) or M N
#   - Applications are assumed to be left associative: M N P may be written
#     instead of ((M N) P).
#   NOTE: python applications look like this M(N)(P) not ((M N) P)
def process_application(string: str) -> str:
    arg_list = []
    substitution = ''
    continuous = False
    for char in string:
        if char.isspace():
            continue
        if char.isupper():
            substitution = char if not continuous else substitution + char
            continuous = True
        else:
            if continuous:
                arg_list.append(substitution)
                substitution = ''
                continuous = False
            else:
                arg_list.append(char)
    # first, rest = (lambda x, *y: (x, y))(*arg_list)
    first, *rest = arg_list
    return first + "".join([f'({arg})' for arg in rest])


#   - A sequence of abstractions is contracted: λx.λy.λz.N is abbreviated as
#     λxyz.N
def expand_lambdas(string: str) -> str:
    λ_index = string.find(λ)
    while λ_index != -1:
        # relative_dot_index...
        dot_index = string[λ_index:].index(dot) + λ_index
        arg_length = dot_index - (λ_index + 1)
        if arg_length > 1:
            lambda_string = ''.join([f'lambda {arg}. ' for arg in
                                    string[λ_index+1:dot_index]])
            string = string.replace(string[λ_index:dot_index+1],
                                    lambda_string, 1)
        else:
            # allow us to skip this λ in the while loop...
            string = string.replace(λ, 'lambda', 1)
        λ_index = string.find(λ)
    # End with replacing lambda with λ, allows us to treat an a-zA-Z in the
    # remaining string as variables... Side effect, you can interchangably use
    # the λ symbol and python lambda keyword...
    return string.replace('lambda', λ)


#   - The body of an abstraction extends as far right as possible: λx.M N means
#     λx.(M N) and not (λx.M) N.
#   NOTE: this is almost implicit based on the way that python does application
def find_applications(string: str) -> str:
    string = ''.join(string.split())  # remove ALL whitespace
    two_or_more_variables = re.compile('[a-zA-Z][a-zA-Z]+')  # continuous alpha
    # chars, meaning there is no λ, ., (, or ) breaking up the calls... This
    # essentially identifies applications in the uncluttered notation
    for application in re.findall(two_or_more_variables, string):
        string = string.replace(application, process_application(application))
    return string

# END OF PROCESSING LAMBDA HELPER CODE - based on wikipedia link, with relevant
# information attributed to processing functions by comments...
###############################################################################


def process_lambda(string: str) -> str:
    if paren_matched(string):
        # this allows interchangeable dot and colon notation
        string = string.replace(':', dot)
        string = expand_lambdas(string)
        string = find_applications(string)
        string = string.replace(λ, 'lambda ')
        string = string.replace(dot, ': ')
        return string


###############################################################################
# From https://en.wikipedia.org/wiki/Lambda_calculus#Formal_definition
# The set of lambda expressions, Λ, can be defined inductively:
#   - If x is a variable, then x ∈ Λ.
#   - If x is a variable and M ∈ Λ, then (λx.M) ∈ Λ.
#   - If M, N ∈ Λ, then (M N) ∈ Λ.
# The abstraction operator, λ, is said to bind its variable wherever it occurs
# in the body of the abstraction. Variables that fall within the scope of an
# abstraction are said to be bound. In an expression λx.M, the part λx is often
# called binder, as a hint that the variable x is getting bound by appending λx
# to M. All other variables are called free. For example, in the expression
#   λy.x x y,
# y is a bound variable and x is a free variable. Also a variable is bound by
# its nearest abstraction. In the following example the single occurrence of x
# in the expression is bound by the second lambda:
#   λx.y (λx.z x).
# The set of free variables of a lambda expression, M, is denoted as FV(M) and
# is defined by recursion on the structure of the terms, as follows:
#   - FV(x) = {x}, where x is a variable.
#   - FV(λx.M) = FV(M) \ {x}.
#   - FV(M N) = FV(M) ∪ FV(N).
# NOTE: this is basically letting us know how scoping works and gives the
# ability to name and reference functions later. Most of this is handled by
# the natural scoping of python. The only trick is being able to reference
# previous named lambda's which we accomplish with globals()...
# NOTE: we aren't doing proper reductions - more utilizing python to do
# function application (instead of β-reduction)... and ignoring the a- and η-
# reduction (real substitution) and instead doing some psuedo-substitution with
# variable names and the global scope
def exec_lambda(string: str, name: str = None):
    """Takes a lambda string (regular or with λ's - if with λ then we run
    processing), executes it, and returns the resulting lambda function. If
    the provided string is not a lambda then it will not be executed.

    WARNING: PROBABLY DANGEROUS

    Args:
        string (str): string representing a lambda you want to run
        name (str, optional): the variable which will hold the created lambda.
            If None is provided, a default name is used to create the function
            in your global context and return it.

    Returns:
        lambda: function created by executing the provided string, otherwise
            it modifies the context you passed in.
    """
    λ_string = process_lambda(string)
    Λ_string = f'Λ_{hash(λ_string)}'  # id for set of lambdas
    name = Λ_string if not name else name
    if λ_string:
        exec(f'{name} = {λ_string}', globals())
        if name is Λ_string:
            temp = globals()[Λ_string]
            del globals()[Λ_string]
            return temp
# END OF EXECUTE LAMBDA CODE
###############################################################################


def execute_lambda_file(filename):
    hasTRUE = False
    hasFALSE = False
    with open(filename) as f:
        contents = f.readlines()
    for line in contents:
        line = line.strip()
        if line:
            name, λ = line.split(':=')
            name = name.strip()
            if name == 'TRUE':
                hasTRUE = True
            if name == 'FALSE':
                hasFALSE = True
            exec_lambda(λ.strip(), name)
    # give access to a show helper function which can show if something is true
    # or false (given the true or false functions), otherwise it will pass an
    # increment function as the first arg and the number 0 as the second - such
    # that for two input (curried) functions the result will be the number of
    # times the first function is called on the second.
    # NOTE: ALL OTHER BEHAVIOR OF show(...) IS UNKNOWN
    show = 'show = lambda s: _show(s'
    show += ', TRUE, FALSE)' if hasTRUE and hasFALSE else ')'
    exec(show, globals())


# _show = lambda s: _show_true_false(s) if s is TRUE or s is FALSE else \
#                   _show_num(s)
def _show(input_function, TRUE=None, FALSE=None):
    if input_function is TRUE or input_function is FALSE:
        return _show_true_false(input_function, TRUE, FALSE)
    return _show_number(input_function)


# _show_true_false = lambda s: 'true' if s == TRUE \
#                               else 'false' if s == FALSE \
#                               else 'invalid'
def _show_true_false(input_function, TRUE, FALSE) -> str:
    if input_function is TRUE:
        return 'true'
    if input_function is FALSE:
        return 'false'
    return 'INVALID'


# _show_num = lambda s: s(_incr)(0)
# _show_num = lambda s: s(lambda x: x + 1)(0)
def _show_number(input_function):
    return input_function(_incr)(0)


# _incr = lambda x: x + 1
def _incr(input_number):
    return input_number + 1

# execute_lambda_file('/Users/samuelhill/Sync/General/programming/Python/lambda/church.lambda')
