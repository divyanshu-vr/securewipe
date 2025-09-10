"""Schema version migration utilities."""

from typing import Any, Dict


def migrate_certificate(
    certificate: Dict[str, Any], target_version: str = "1.0.0"
) -> Dict[str, Any]:
    """Migrate certificate to target schema version.

    Args:
        certificate: Certificate to migrate
        target_version: Target schema version

    Returns:
        Migrated certificate
    """
    current_version = certificate.get("schemaVersion", "1.0.0")

    if current_version == target_version:
        return certificate

    # Future migration logic will be added here
    # For now, only v1.0.0 is supported
    return certificate


def is_compatible_version(version: str) -> bool:
    """Check if schema version is compatible.

    Args:
        version: Schema version to check

    Returns:
        True if compatible
    """
    return version.startswith("1.0.")
