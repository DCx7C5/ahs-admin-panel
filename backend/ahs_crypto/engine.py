import logging

from . import settings as app_settings

logger = logging.getLogger(__name__)




def check_min_settings():
    """
    Checks if minimum settings are set.
    """
    if hasattr(app_settings, 'ROOT_PRIVKEY_PATH'):
        return True
    return False
