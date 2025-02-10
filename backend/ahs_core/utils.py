import inspect
import os
import shutil

from config.settings import BASE_DIR


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

def clean_migrations_dirs(base_path, purge: bool = False):
    """
    Find all `migrations` directories under the given base path and delete all files
    in them except for `__init__.py`.

    :param base_path: Root directory to start searching from.
    :param purge: If True, deletes the migration directories; otherwise, cleans them.
    """
    for root, dirs, files in os.walk(base_path):
        # Filter for `migrations` directories
        if 'migrations' in dirs:
            migrations_dir = os.path.join(root, 'migrations')

            if purge:
                # Delete the entire migrations directory
                shutil.rmtree(migrations_dir)
                print(f"Purged directory: {migrations_dir}")
            else:
                # Only delete files in the migrations folder except `__init__.py`
                for file_name in os.listdir(migrations_dir):
                    file_path = os.path.join(migrations_dir, file_name)

                    # Keep `__init__.py`, delete everything else
                    if file_name != '__init__.py' and os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")


def get_all_apps():
    """
    Recursively find all directories containing a file named 'apps.py' starting from a specified path.
    :return: A list of directory paths containing 'apps.py'.
    """
    directories_with_apps_py = ["ahs_accounts"]
    for root, dirs, files in os.walk(BASE_DIR / 'backend' ):
        if "apps.py" in files:  # Check if 'apps.py' exists in the current folder
            directories_with_apps_py.append(root.split('backend/')[-1].replace('/', '.'))
    if 'makemigrations' in directories_with_apps_py:
        directories_with_apps_py.remove('makemigrations')
    if 'modules' in directories_with_apps_py:
        directories_with_apps_py.remove('modules')
    if 'manage.py' in directories_with_apps_py:
        directories_with_apps_py.remove('manage.py')

    return directories_with_apps_py


def get_all_core_apps():
    return [x for x in get_all_apps() if x.startswith('ahs')]

def get_all_plugin_apps():
    plugins = []
    for x in get_all_apps():
        if not x.startswith('ahs'):
            if x.startswith('apps.'):
                x.replace('apps.','')
            plugins.append(x)
    return plugins
