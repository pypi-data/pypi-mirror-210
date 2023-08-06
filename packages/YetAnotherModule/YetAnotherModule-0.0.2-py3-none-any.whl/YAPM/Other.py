from collections.abc import Sequence

#
# Random Stuff
#


def RaisesError(code: str, Ignore: Sequence[Exception] = [], GlobalVars: dict[str, any] = {}):
    """
    Evaluates the code provited.

    :param str code: str - The code to eval
    :param Sequence[Exception] Ignore: Exceptions to ignore
    :param dict[str, any] GlobalVars: Globals to pass into the eval function

    :returns:
        - Tuple[True, any] - Code ran without any errors. returns code result.
        - Tuple[True, Exception] - Code threw a error that is in the Ignored exceptions list
        - Tuple[False, Exception] - Code threw a error that is not Ignored.'

    :raises:
        - ValueError - Ignore isn't a iterable
        - ValueError - GlobalVars isn't a dict
        - ValueError - Code isn't a string
    """
    try:
        iter(Ignore)
    except ValueError:
        raise ValueError("Ignore Should be an iterable")
    try:
        dict(GlobalVars)
    except ValueError:
        raise ValueError("GlobalVars Should be an dict")
    if not isinstance(code, str):
        raise ValueError("Code needs to be a string or isinstance(code, str) should return true")

    try:
        Value = eval(compile(code, '<string>', 'eval'), GlobalVars)
    except Exception as e:
        if e in Ignore:
            return (True, e)
        else:
            return (False, e)

    return (True, Value)
