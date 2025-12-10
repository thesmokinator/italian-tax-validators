"""Italian tax validators for Codice Fiscale and Partita IVA.

This package provides validation utilities for Italian tax identification numbers:
- Codice Fiscale (CF): Personal tax identification code
- Partita IVA (P.IVA): VAT identification number

Example:
    >>> from italian_tax_validators import validate_codice_fiscale, validate_partita_iva
    >>> cf_result = validate_codice_fiscale("RSSMRA85M01H501Q")
    >>> piva_result = validate_partita_iva("12345678903")

"""

from italian_tax_validators.validators import (
    CF_EVEN_VALUES,
    CF_MONTH_CODES,
    CF_ODD_VALUES,
    CF_OMOCODIA_CHARS,
    MINIMUM_AGE_YEARS,
    CodiceFiscaleValidator,
    CodiceFiscaleValidationResult,
    PartitaIvaValidator,
    PartitaIvaValidationResult,
    validate_codice_fiscale,
    validate_partita_iva,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "CodiceFiscaleValidator",
    "PartitaIvaValidator",
    "CodiceFiscaleValidationResult",
    "PartitaIvaValidationResult",
    "validate_codice_fiscale",
    "validate_partita_iva",
    "CF_ODD_VALUES",
    "CF_EVEN_VALUES",
    "CF_MONTH_CODES",
    "CF_OMOCODIA_CHARS",
    "MINIMUM_AGE_YEARS",
]
