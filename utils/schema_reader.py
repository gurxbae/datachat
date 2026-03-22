from core.db_manager import get_schema

def get_formatted_schema():
    """Returns a clean formatted schema string."""
    return get_schema()