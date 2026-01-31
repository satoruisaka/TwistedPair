# utils.py
import enum
from dataclasses import asdict

def to_serializable(obj):
    """
    Recursively convert dataclasses, Enums, and other objects to JSON-serializable types.
    """
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_serializable(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, enum.Enum):
        return obj.value   # store the string value of the enum
    elif isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    else:
        return obj
    

