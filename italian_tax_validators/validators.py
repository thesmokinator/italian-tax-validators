"""Validators for Italian tax identification documents.

This module provides validation utilities for Italian tax IDs:
- Codice Fiscale (CF): Personal tax identification code
- Partita IVA (P.IVA): VAT identification number

Both validators include format validation, check digit verification,
and additional business logic (e.g., age verification for CF).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

# Minimum age required for certain operations (e.g., Pro registration)
MINIMUM_AGE_YEARS = 18

# ============================================================================
# Codice Fiscale (CF) Validation Tables
# ============================================================================

# Odd position character values (1st, 3rd, 5th, etc. - 1-indexed)
CF_ODD_VALUES = {
    "0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13, "6": 15, "7": 17, "8": 19, "9": 21,
    "A": 1, "B": 0, "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17, "I": 19, "J": 21,
    "K": 2, "L": 4, "M": 18, "N": 20, "O": 11, "P": 3, "Q": 6, "R": 8, "S": 12, "T": 14,
    "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23,
}

# Even position character values (2nd, 4th, 6th, etc. - 1-indexed)
CF_EVEN_VALUES = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8, "J": 9,
    "K": 10, "L": 11, "M": 12, "N": 13, "O": 14, "P": 15, "Q": 16, "R": 17, "S": 18, "T": 19,
    "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25,
}

# Month codes for Codice Fiscale (A=January, B=February, etc.)
CF_MONTH_CODES = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "H": 6,
    "L": 7, "M": 8, "P": 9, "R": 10, "S": 11, "T": 12,
}

# Omocodia substitution characters (digits can be replaced with these letters)
# Used when two people have the same CF
CF_OMOCODIA_CHARS = {
    "L": "0", "M": "1", "N": "2", "P": "3", "Q": "4",
    "R": "5", "S": "6", "T": "7", "U": "8", "V": "9",
}


@dataclass
class CodiceFiscaleValidationResult:
    """Result of Codice Fiscale validation.

    Attributes:
        is_valid: Whether the CF is valid
        error_code: Error code if invalid (None if valid)
        formatted_value: The cleaned/formatted CF value
        birthdate: Extracted birthdate (None if extraction failed)
        age: Calculated age in years (None if birthdate extraction failed)

    """

    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None
    birthdate: date | None = None
    age: int | None = None


@dataclass
class PartitaIvaValidationResult:
    """Result of Partita IVA validation.

    Attributes:
        is_valid: Whether the P.IVA is valid
        error_code: Error code if invalid (None if valid)
        formatted_value: The cleaned/formatted P.IVA value

    """

    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None


class CodiceFiscaleValidator:
    """Validator for Italian Codice Fiscale (CF).

    The Codice Fiscale is a 16-character alphanumeric code that encodes:
    - Surname (3 characters)
    - Name (3 characters)
    - Birth year (2 digits)
    - Birth month (1 letter)
    - Birth day and gender (2 digits, +40 for females)
    - Birth place code (4 characters)
    - Check character (1 letter)

    This validator handles:
    - Format validation
    - Omocodia (substitution of digits with letters)
    - Check digit verification
    - Birthdate extraction
    - Age calculation

    Example:
        >>> validator = CodiceFiscaleValidator()
        >>> result = validator.validate("RSSMRA85M01H501Z")
        >>> print(result.is_valid)
        True

    """

    # Positions where omocodia substitution can occur (0-indexed)
    OMOCODIA_POSITIONS = [6, 7, 9, 10, 12, 13, 14]

    # Regex pattern for CF format (allowing omocodia)
    CF_PATTERN = re.compile(r"^[A-Z]{6}[A-Z0-9]{2}[A-Z][A-Z0-9]{2}[A-Z][A-Z0-9]{3}[A-Z]$")

    def validate(
        self,
        value: str,
        check_adult: bool = False,
        minimum_age: int = MINIMUM_AGE_YEARS,
    ) -> CodiceFiscaleValidationResult:
        """Validate an Italian Codice Fiscale.

        Args:
            value: The CF string to validate
            check_adult: Whether to verify the person is at least minimum_age years old
            minimum_age: Minimum age required (default: 18)

        Returns:
            CodiceFiscaleValidationResult with validation details

        """
        # Clean and uppercase the value
        clean_value = value.strip().upper().replace(" ", "")

        # Step 1: Validate format
        if not self._validate_format(clean_value):
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_invalid_format",
                formatted_value=clean_value,
            )

        # Step 2: Validate check digit
        if not self._validate_check_digit(clean_value):
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_invalid_format",
                formatted_value=clean_value,
            )

        # Step 3: Extract birthdate
        birthdate = self._extract_birthdate(clean_value)
        age = None

        if birthdate is None:
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_cannot_decode_birthdate",
                formatted_value=clean_value,
            )

        # Calculate age
        today = date.today()
        age = today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )

        # Step 4: Check age if required
        if check_adult and age < minimum_age:
            return CodiceFiscaleValidationResult(
                is_valid=False,
                error_code="tax_id_cf_underage",
                formatted_value=clean_value,
                birthdate=birthdate,
                age=age,
            )

        # All validations passed
        return CodiceFiscaleValidationResult(
            is_valid=True,
            formatted_value=clean_value,
            birthdate=birthdate,
            age=age,
        )

    def _validate_format(self, cf: str) -> bool:
        """Validate CF format using regex pattern.

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            True if format matches the expected pattern

        """
        return len(cf) == 16 and bool(self.CF_PATTERN.match(cf))

    def _decode_omocodia(self, cf: str) -> str:
        """Decode omocodia characters back to digits.

        Omocodia occurs when two people have the same CF. In such cases,
        digits at positions 6, 7, 9, 10, 12, 13, 14 can be replaced with letters.

        Args:
            cf: 16-character CF string

        Returns:
            CF with omocodia characters replaced with digits

        """
        cf_list = list(cf)
        for pos in self.OMOCODIA_POSITIONS:
            char = cf_list[pos]
            if char in CF_OMOCODIA_CHARS:
                cf_list[pos] = CF_OMOCODIA_CHARS[char]
        return "".join(cf_list)

    def _validate_check_digit(self, cf: str) -> bool:
        """Validate CF check digit.

        The check digit is calculated by:
        1. Summing values for characters at odd positions (1-indexed)
        2. Summing values for characters at even positions (1-indexed)
        3. Taking the remainder of total sum divided by 26
        4. Converting to letter (A=0, B=1, etc.)

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            True if check digit is valid

        """
        # Decode omocodia for check digit calculation
        decoded_cf = self._decode_omocodia(cf)

        total = 0
        for i, char in enumerate(decoded_cf[:15]):
            if i % 2 == 0:  # Odd positions (1-indexed) = even index (0-indexed)
                total += CF_ODD_VALUES.get(char, 0)
            else:  # Even positions (1-indexed) = odd index (0-indexed)
                total += CF_EVEN_VALUES.get(char, 0)

        expected_check = chr(ord("A") + (total % 26))
        return cf[15] == expected_check

    def _extract_birthdate(self, cf: str) -> date | None:
        """Extract birthdate from Codice Fiscale.

        The birthdate is encoded in positions 6-11:
        - Positions 6-7: Last two digits of birth year
        - Position 8: Month letter code
        - Positions 9-10: Birth day (females add 40)

        Args:
            cf: 16-character CF string (uppercase)

        Returns:
            date object if extraction successful, None otherwise

        """
        try:
            # Decode omocodia first
            decoded_cf = self._decode_omocodia(cf)

            # Year: positions 6-7 (0-indexed)
            year_digits = decoded_cf[6:8]
            year = int(year_digits)

            # Determine century
            current_year = date.today().year
            current_century = current_year // 100 * 100
            current_year_two_digits = current_year % 100

            year = 1900 + year if year > current_year_two_digits else current_century + year

            # Month: position 8 (0-indexed)
            month_char = cf[8]
            month = CF_MONTH_CODES.get(month_char)
            if month is None:
                return None

            # Day: positions 9-10 (0-indexed)
            day_digits = decoded_cf[9:11]
            day = int(day_digits)

            # For females, 40 is added to the day
            if day > 40:
                day -= 40

            return date(year, month, day)

        except (ValueError, IndexError):
            return None


class PartitaIvaValidator:
    """Validator for Italian Partita IVA (VAT number).

    The Partita IVA is an 11-digit number composed of:
    - First 7 digits: Company registration number (matricola)
    - Next 3 digits: Provincial office code
    - Last digit: Check digit (Luhn algorithm variant)

    Example:
        >>> validator = PartitaIvaValidator()
        >>> result = validator.validate("12345678903")
        >>> print(result.is_valid)
        True

    """

    def validate(self, value: str) -> PartitaIvaValidationResult:
        """Validate an Italian Partita IVA.

        Args:
            value: The P.IVA string to validate

        Returns:
            PartitaIvaValidationResult with validation details

        """
        # Clean the value: remove whitespace and keep only digits
        clean_value = "".join(filter(str.isdigit, value.strip()))

        # Step 1: Must be exactly 11 digits
        if len(clean_value) != 11:
            return PartitaIvaValidationResult(
                is_valid=False,
                error_code="tax_id_piva_invalid_length",
                formatted_value=clean_value,
            )

        # Step 2: Validate check digit using Luhn algorithm variant
        if not self._validate_check_digit(clean_value):
            return PartitaIvaValidationResult(
                is_valid=False,
                error_code="tax_id_piva_invalid_check_digit",
                formatted_value=clean_value,
            )

        # All validations passed
        return PartitaIvaValidationResult(
            is_valid=True,
            formatted_value=clean_value,
        )

    def _validate_check_digit(self, vat_number: str) -> bool:
        """Validate P.IVA check digit using Italian Luhn algorithm variant.

        The algorithm:
        1. Sum digits at odd positions (1st, 3rd, 5th, etc. - 1-indexed)
        2. For digits at even positions: double the digit, subtract 9 if >= 10
        3. Sum of all processed digits should be divisible by 10

        Args:
            vat_number: 11-digit VAT number string

        Returns:
            True if check digit is valid, False otherwise

        """
        if len(vat_number) != 11 or not vat_number.isdigit():
            return False

        total = 0
        for i, digit in enumerate(vat_number):
            d = int(digit)
            if i % 2 == 0:
                # Odd positions (1-indexed) = even index (0-indexed): add directly
                total += d
            else:
                # Even positions (1-indexed) = odd index (0-indexed): double
                doubled = d * 2
                if doubled >= 10:
                    doubled -= 9
                total += doubled

        return total % 10 == 0


# Validator instances (lazy initialization via class method)
class _ValidatorInstances:
    """Container for validator singleton instances."""

    _cf_validator: CodiceFiscaleValidator | None = None
    _piva_validator: PartitaIvaValidator | None = None

    @classmethod
    def get_cf_validator(cls) -> CodiceFiscaleValidator:
        """Get singleton instance of CodiceFiscaleValidator."""
        if cls._cf_validator is None:
            cls._cf_validator = CodiceFiscaleValidator()
        return cls._cf_validator

    @classmethod
    def get_piva_validator(cls) -> PartitaIvaValidator:
        """Get singleton instance of PartitaIvaValidator."""
        if cls._piva_validator is None:
            cls._piva_validator = PartitaIvaValidator()
        return cls._piva_validator


def validate_codice_fiscale(
    value: str,
    check_adult: bool = False,
    minimum_age: int = MINIMUM_AGE_YEARS,
) -> CodiceFiscaleValidationResult:
    """Convenience function to validate a Codice Fiscale.

    Args:
        value: The CF string to validate
        check_adult: Whether to verify minimum age requirement
        minimum_age: Minimum age required (default: 18)

    Returns:
        CodiceFiscaleValidationResult with validation details

    """
    return _ValidatorInstances.get_cf_validator().validate(value, check_adult, minimum_age)


def validate_partita_iva(value: str) -> PartitaIvaValidationResult:
    """Convenience function to validate a Partita IVA.

    Args:
        value: The P.IVA string to validate

    Returns:
        PartitaIvaValidationResult with validation details

    """
    return _ValidatorInstances.get_piva_validator().validate(value)
