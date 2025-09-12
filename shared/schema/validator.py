"""Certificate schema validation."""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import jsonschema

sys.path.append(str(Path(__file__).parent.parent))
try:
    from utils.exceptions import CertificateValidationError
except ImportError:
    # Define locally if not available
    class CertificateValidationError(Exception):
        """Certificate validation error."""
        pass


def validate_certificate(certificate: Dict[str, Any]) -> bool:
    """Validate certificate against schema.

    Args:
        certificate: Certificate data to validate

    Returns:
        True if valid

    Raises:
        jsonschema.ValidationError: If certificate is invalid
    """
    schema_path = Path(__file__).parent / "certificate_v1.json"
    with open(schema_path) as f:
        schema = json.load(f)

    try:
        jsonschema.validate(certificate, schema)
        return True
    except jsonschema.ValidationError as e:
        raise CertificateValidationError(
            f"Certificate validation failed: {e.message}"
        ) from e
    except Exception as e:
        raise CertificateValidationError(
            f"Unexpected validation error: {str(e)}"
        ) from e
