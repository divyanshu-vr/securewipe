"""Custom exception classes for SecureWipe."""


class SecureWipeError(Exception):
    """Base exception for SecureWipe operations."""

    pass


class CertificateValidationError(SecureWipeError):
    """Certificate validation failed."""

    pass


class CryptographyError(SecureWipeError):
    """Cryptographic operation failed."""

    pass


class SchemaVersionError(SecureWipeError):
    """Unsupported schema version."""

    pass
