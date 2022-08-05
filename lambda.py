def procLambda(string: str) -> str:
    """Transform strings with λ symbols to lambda notation. Only takes one
    letter arguments after the lambda just as lambda calculus would expect.

    Args:
        string (str): lambda string you want to process for eventual execution.
                      If you use multiple λ's, that's fine as the processing
                      is recursive and will transform each λ into a lambda.
                      NOTE: arguments after the λ will be expected as single
                      characters. Each character after a λ before the ':' will
                      be transformed into an argument. If you put special chars
                      in this section, your code might fail.

    Returns:
        str: Properly formed lambda expression replacing all λ's with lambda
             and reforming arguments to follow the single argument style of
             lambda calculus. If a lambda is already in the string then it's
             arguments are left alone.
    """
    if 'λ' in string:
        lambda_index = string.index('λ')
        end_args_index = string[lambda_index:].index(':') + lambda_index
        char_args = string[lambda_index+1:end_args_index].strip()
        lambda_string = ''.join([f'lambda {arg}: ' for arg in char_args])
        too_replace = string[lambda_index:end_args_index+1].strip()
        return string.replace(too_replace, lambda_string)
    if 'lambda' in string:
        return string


# , temp=None: dict
def exec_lambda(string: str, name: str = None):
    """Takes a lambda string (regular or with λ's - if with λ then we run
    processing), executes it, and returns the resulting lambda function. If
    the provided string is not a lambda then it will not be executed.

    WARNING: PROBABLY DANGEROUS

    Args:
        string (str): string representing a lambda you want to run

    Returns:
        lambda: function created by executing the provided string
    """
    lambda_string = procLambda(string)
    lambda_func_s = 'LAMBDA_FUNC'
    name = lambda_func_s if not name else name
    if lambda_string:
        exec(f'{name} = {lambda_string}', globals())
        if name is lambda_func_s:
            temp = globals()['LAMBDA_FUNC']
            del globals()['LAMBDA_FUNC']
            return temp


# _show_true_false = lambda s: 'true' if s == TRUE \
#                               else 'false' if s == FALSE \
#                               else 'invalid'
def _show_true_false(input_function, TRUE, FALSE) -> str:
    if input_function is TRUE:
        return 'true'
    elif input_function is FALSE:
        return 'false'
    else:
        return 'INVALID'


# _incr = lambda x: x + 1
def _incr(input_number):
    return input_number + 1


# _show_num = lambda s: s(_incr)(0)
# _show_num = lambda s: s(lambda x: x + 1)(0)
def _show_number(input_function):
    return input_function(_incr)(0)


# _show = lambda s: _show_true_false(s) if s is TRUE or s is FALSE else \
#                   _show_num(s)
def _show(input_function, TRUE, FALSE):
    if input_function is TRUE or input_function is FALSE:
        return _show_true_false(input_function, TRUE, FALSE)
    else:
        return _show_number(input_function)


# DEFAULT VALUES - the true and false functions operate as a base definition
# of the true and false behavior functions... Calling them behavior functions
# as they don't give true or false, the define how true and false should work
# in this framework - specifically, they counter each other. These could be
# renamed RIGHT and LEFT as they simply take the right or left argument.
# By treating them as binary functions for truth and false SIMULTANEOUSLY with
# treating them as the truth and false values we can use these functions in
# the later binary operations, math, and data representations...
# TRUE = lambda x: lambda y: x
TRUE = exec_lambda('λxy:x')
# FALSE = lambda x: lambda y: y
FALSE = exec_lambda('λxy:y')

show = lambda s: _show(s, TRUE, FALSE)

# NOT = lambda x: x(FALSE)(TRUE)
NOT = exec_lambda('λx:x(FALSE)(TRUE)')
# AND = lambda x: lambda y: x(y)(x)
AND = exec_lambda('λxy:x(y)(x)')
# OR = lambda x: lambda y: x(x)(y)
OR = exec_lambda('λxy:x(x)(y)')

# ZERO = lambda f: lambda x: x
ZERO = exec_lambda('λfx:x')
# ONE = lambda f: lambda x: f(x)
ONE = exec_lambda('λfx:f(x)')
# TWO = lambda f: lambda x: f(f(x))
TWO = exec_lambda('λfx:f(f(x))')
# THREE = lambda f: lambda x: f(f(f(x)))
THREE = exec_lambda('λfx:f(f(f(x)))')
# FOUR = lambda f: lambda x: f(f(f(f(x))))
FOUR = exec_lambda('λfx:f(f(f(f(x))))')
# FIVE = lambda f: lambda x: f(f(f(f(f(x)))))
FIVE = exec_lambda('λfx:f(f(f(f(f(x)))))')

# SUCC = lambda n: lambda f: lambda x: f(n(f)(x))
SUCC = exec_lambda('λnfx:f(n(f)(x))')

# ADD = lambda x: lambda y: y(SUCC)(x)
ADD = exec_lambda('λxy:y(SUCC)(x)')
# MUL = lambda x: lambda y: lambda f: y(x(f))
MUL = exec_lambda('λxyf:y(x(f))')

# PRED = λnfx.n (λgh.h (g f)) (λu.x) (λu.u)

# CONS = lambda a: lambda b: lambda s: s(a)(b)
CONS = exec_lambda('λabs:s(a)(b)')
# CAR = lambda p: p(TRUE)
# CAR  = lambda p: p(TRUE) if not isinstance(p, str) else p
CAR = exec_lambda('λp:p(TRUE)')
# CDR = lambda p: p(FALSE)
CDR = exec_lambda('λp:p(FALSE)')


def print_list(my_list):
    new_list = []
    # while CAR(my_list) is not FALSE:  <- infinite loop on 1 and 'true'
    #
    # during evaluation:
    #   CAR(FALSE) behaves like 'ONE' ...? it acts as a functional
    #                                      equivalent to ONE when calling
    #                                      show because of the incr function
    #   CAR(FALSE) = FALSE(TRUE) = not a TRUE or FALSE function in show =
    #   FALSE(TRUE)(_incr)(0) = 1... FALSE(TRUE) produces a function
    #   that takes in some input and returns it... same behavior as ONE?
    #
    # getting next element
    #   CDR(FALSE) {returns 1 also, weird}... when evaluated CAR(CDR(FALSE))
    #   CDR(FALSE) = FALSE(FALSE)
    #   CAR(CDR(FALSE)) = FALSE(FALSE)(TRUE)
    while my_list is not FALSE:
        new_list.append(show(CAR(my_list)))
        my_list = CDR(my_list)
    print(f'({", ".join(map(str,new_list))})')


cons_list = CONS(ONE)(CONS(TWO)(CONS(THREE)(CONS(FOUR)(FALSE))))
print_list(cons_list)
