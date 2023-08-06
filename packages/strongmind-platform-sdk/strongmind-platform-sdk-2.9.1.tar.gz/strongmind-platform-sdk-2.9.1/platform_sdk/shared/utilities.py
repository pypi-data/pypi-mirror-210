from platform_sdk.shared.constants import ONEROSTER_SINGLE_TYPE_NAME_CLASS


def get_plural_oneroster_type(oneroster_type: str) -> str:
    es_plurals = [ONEROSTER_SINGLE_TYPE_NAME_CLASS]
    suffix = 's' if oneroster_type not in es_plurals else 'es'
    return oneroster_type + suffix
