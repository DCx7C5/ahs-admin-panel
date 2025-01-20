import inspect

def parse_func_signature(func, exclude: list = None):
    """
    Parses the function signature to extract:
    - Positional arguments
    - Keyword arguments (with and without defaults)
    - Annotations
    """
    # Extract function signature
    sig = inspect.signature(func)
    args = []  # Positional arguments or ones with defaults
    kwargs = {}  # Keyword arguments (key: name, value: default)
    annotations = {}  # Parameter annotations
    exclude = exclude or []
    for name, param in sig.parameters.items():
        if name in exclude:
            continue
        # Capture annotations, if available
        if param.annotation != inspect.Parameter.empty:
            annotations[name] = param.annotation
        # Distinguish between positional arguments and kwargs with defaults
        if param.default == inspect.Parameter.empty:
            # No default means it's a positional argument
            args.append(name)
        else:
            # Has a default value
            kwargs[name] = param.default
    return args, kwargs, annotations
