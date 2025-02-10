from backend.ahs_crypto import settings, get_ecc_backend

ECC_BACKEND_CLASS_STR: str = settings.ECC_BACKEND


def validate_settings():
    try:
        ECC = get_ecc_backend()
        ECC.check_settings()
        return True
    except Exception as e:
        raise Exception(f"Error validating settings: {e}")
