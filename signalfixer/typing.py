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
    # Retrieve the type hints of the function
    hints = get_type_hints(func)

    # Get the function's parameter names
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

    # Combine positional arguments into a dictionary with argument names
    all_args = dict(zip(arg_names, inputs))

    # Check each argument against its type hint
    for arg_name, arg_value in all_args.items():
        if arg_name in hints:
            expected_type = hints[arg_name]
            # Handle Union types
            if get_origin(expected_type) is Union:
                possible_types = get_args(expected_type)
                if not any(isinstance(arg_value, t) for t in possible_types):
                    raise TypeError(f"Argument '{arg_name}' must be one of {
                                    possible_types}. Got {type(arg_value)} instead.")
            else:
                # Handle single types
                if not isinstance(arg_value, expected_type):
                    raise TypeError(f"Argument '{arg_name}' must be of type {
                                    expected_type}. Got {type(arg_value)} instead.")
