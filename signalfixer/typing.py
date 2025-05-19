from typing import get_type_hints, get_args, get_origin, Union, List, Dict


def check_inputs(func, *inputs):
    """
    Checks if all input arguments match the type hints defined in the function signature.

    Args:
        func: The function whose type hints to check.
        *inputs: Positional arguments to check.

    Raises:
        TypeError: If any input argument doesn't match its corresponding type hint.
    """
    hints = get_type_hints(func)
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    all_args = dict(zip(arg_names, inputs))

    for arg_name, arg_value in all_args.items():
        if arg_name not in hints:
            continue

        expected_type = hints[arg_name]
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if origin is Union:
            if not any(_check_type(arg_value, t) for t in args):
                raise TypeError(f"Argument '{arg_name}' must be one of {args}. Got {type(arg_value)} instead.")
        else:
            if not _check_type(arg_value, expected_type):
                raise TypeError(f"Argument '{arg_name}' must be of type {expected_type}. Got {type(arg_value)} instead.")

def _check_type(value, expected_type):
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is list:
        return isinstance(value, list) and all(_check_type(v, args[0]) for v in value)
    elif origin is dict:
        return isinstance(value, dict) and all(
            _check_type(k, args[0]) and _check_type(v, args[1]) for k, v in value.items()
        )
    elif origin is Union:
        return any(_check_type(value, t) for t in args)
    elif origin is None:
        return isinstance(value, expected_type)
    else:
        return isinstance(value, origin)