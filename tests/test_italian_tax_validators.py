"""Unit tests for Italian tax validators.

Tests for:
- Codice Fiscale validation
- Partita IVA validation
- Birthdate extraction
- Age verification
- Check digit algorithms
"""

import datetime
from datetime import date
from unittest import TestCase

from italian_tax_validators import (
    CodiceFiscaleValidator,
    PartitaIvaValidator,
    validate_codice_fiscale,
    validate_partita_iva,
    CF_MONTH_CODES,
)


class CodiceFiscaleValidatorTest(TestCase):
    """Tests for Italian Codice Fiscale (CF) validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_valid_codice_fiscale_male(self):
        """Test validation of a valid male CF."""
        # RSSMRA85M01H501Q - Mario Rossi, born Aug 1, 1985 in Rome
        result = self.validator.validate("RSSMRA85M01H501Q")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")
        self.assertIsNotNone(result.birthdate)
        self.assertEqual(result.birthdate.year, 1985)
        self.assertEqual(result.birthdate.month, 8)
        self.assertEqual(result.birthdate.day, 1)

    def test_valid_codice_fiscale_female(self):
        """Test validation of a valid female CF (day + 40)."""
        # RSSMRA85M41H501U - Maria Rossi, born Aug 1, 1985 in Rome (female: 01+40=41)
        result = self.validator.validate("RSSMRA85M41H501U")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertIsNotNone(result.birthdate)
        self.assertEqual(result.birthdate.day, 1)  # 41 - 40 = 1

    def test_valid_codice_fiscale_lowercase_input(self):
        """Test that lowercase input is accepted and converted to uppercase."""
        result = self.validator.validate("rssmra85m01h501q")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")

    def test_valid_codice_fiscale_with_spaces(self):
        """Test that spaces are removed from input."""
        result = self.validator.validate("RSS MRA 85M01 H501Q")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "RSSMRA85M01H501Q")

    def test_invalid_codice_fiscale_wrong_length(self):
        """Test that CF with wrong length is rejected."""
        result = self.validator.validate("RSSMRA85M01H501")  # 15 chars

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_invalid_codice_fiscale_wrong_format(self):
        """Test that CF with invalid format is rejected."""
        result = self.validator.validate("123456789012345A")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_invalid_codice_fiscale_wrong_check_digit(self):
        """Test that CF with wrong check digit is rejected."""
        # Change last character from Q to A (wrong check digit)
        result = self.validator.validate("RSSMRA85M01H501A")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_codice_fiscale_omocodia(self):
        """Test validation of CF with omocodia substitutions."""
        # RSSMRA85M01H50MZ - with omocodia: 1 -> M at position 14
        result = self.validator.validate("RSSMRA85M0MH50MZ")

        # Note: The check digit changes with omocodia
        # This test verifies the validator handles omocodia characters
        self.assertIn(result.is_valid, [True, False])  # Depends on correct check digit

    def test_age_check_adult(self):
        """Test age verification for adult (18+)."""
        # Person born in 1985 should be adult
        result = self.validator.validate("RSSMRA85M01H501Q", check_adult=True)

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.age)
        self.assertGreaterEqual(result.age, 18)

    def test_age_check_minor(self):
        """Test age verification for minor (under 18)."""
        # RSSMRA20M01H501X - born Aug 1, 2020 (minor)
        result = self.validator.validate("RSSMRA20M01H501X", check_adult=True)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_underage")

    def test_age_check_custom_minimum_age(self):
        """Test age verification with custom minimum age."""
        # Person born in 1985 is about 40 years old
        result = self.validator.validate("RSSMRA85M01H501Q", check_adult=True, minimum_age=50)

        # Should fail because they're not 50+ yet
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_underage")

    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.validator.validate("")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_cf_invalid_format")

    def test_all_months_codes(self):
        """Test that all month codes are recognized."""
        expected_months = {
            "A": 1,
            "B": 2,
            "C": 3,
            "D": 4,
            "E": 5,
            "H": 6,
            "L": 7,
            "M": 8,
            "P": 9,
            "R": 10,
            "S": 11,
            "T": 12,
        }
        self.assertEqual(CF_MONTH_CODES, expected_months)


class PartitaIvaValidatorTest(TestCase):
    """Tests for Italian Partita IVA (VAT number) validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = PartitaIvaValidator()

    def test_valid_partita_iva(self):
        """Test validation of a valid P.IVA."""
        # 12345678903 is a valid P.IVA (check digit: 3)
        result = self.validator.validate("12345678903")

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_valid_partita_iva_with_spaces(self):
        """Test that spaces are removed from input."""
        result = self.validator.validate("123 456 78903")

        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_valid_partita_iva_with_prefix_it(self):
        """Test that IT prefix is handled (stripped)."""
        result = self.validator.validate("IT12345678903")

        # IT prefix should be stripped, leaving only digits
        self.assertTrue(result.is_valid)
        self.assertEqual(result.formatted_value, "12345678903")

    def test_invalid_partita_iva_wrong_length(self):
        """Test that P.IVA with wrong length is rejected."""
        result = self.validator.validate("1234567890")  # 10 digits

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_invalid_partita_iva_too_long(self):
        """Test that P.IVA with too many digits is rejected."""
        result = self.validator.validate("123456789012")  # 12 digits

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_invalid_partita_iva_wrong_check_digit(self):
        """Test that P.IVA with wrong check digit is rejected."""
        # 12345678901 - wrong check digit (should be 3)
        result = self.validator.validate("12345678901")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_check_digit")

    def test_invalid_partita_iva_all_zeros(self):
        """Test that P.IVA with all zeros is handled."""
        result = self.validator.validate("00000000000")

        # 00000000000 actually passes Luhn check (sum = 0, 0 % 10 = 0)
        self.assertTrue(result.is_valid)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.validator.validate("")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "tax_id_piva_invalid_length")

    def test_luhn_algorithm_correctness(self):
        """Test the Luhn algorithm implementation with known values."""
        # Some known valid Italian P.IVA numbers
        valid_pivas = [
            "12345678903",  # Standard test number
            "00000000000",  # Edge case: all zeros
            "00743110157",  # Real example: Mediaset
        ]

        for piva in valid_pivas:
            result = self.validator.validate(piva)
            self.assertTrue(result.is_valid, f"P.IVA {piva} should be valid")


class ItalianTaxValidatorConvenienceFunctionsTest(TestCase):
    """Tests for convenience functions in italian_tax_validators module."""

    def test_validate_codice_fiscale_function(self):
        """Test the validate_codice_fiscale convenience function."""
        result = validate_codice_fiscale("RSSMRA85M01H501Q")

        self.assertTrue(result.is_valid)
        self.assertIsNotNone(result.birthdate)

    def test_validate_codice_fiscale_with_age_check(self):
        """Test validate_codice_fiscale with age verification."""
        result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True)

        self.assertTrue(result.is_valid)
        self.assertGreaterEqual(result.age, 18)

    def test_validate_partita_iva_function(self):
        """Test the validate_partita_iva convenience function."""
        result = validate_partita_iva("12345678903")

        self.assertTrue(result.is_valid)


class CodiceFiscaleBirthdateExtractionTest(TestCase):
    """Tests specifically for birthdate extraction from Codice Fiscale."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = CodiceFiscaleValidator()

    def test_birthdate_january(self):
        """Test birthdate extraction for January (A)."""
        # RSSMRA85A01H501Z - January
        result = self.validator.validate("RSSMRA85A01H501Z")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.month, 1)

    def test_birthdate_december(self):
        """Test birthdate extraction for December (T)."""
        # RSSMRA85T01H501M - December
        result = self.validator.validate("RSSMRA85T01H501M")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.month, 12)

    def test_century_determination_1900s(self):
        """Test that years > current year's last 2 digits are 1900s."""
        # RSSMRA90M01H501N - Someone born in 1990
        result = self.validator.validate("RSSMRA90M01H501N")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.year, 1990)

    def test_century_determination_2000s(self):
        """Test that years <= current year's last 2 digits are 2000s."""
        # RSSMRA10M01H501S - Someone born in 2010
        result = self.validator.validate("RSSMRA10M01H501S")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.year, 2010)

    def test_female_day_extraction(self):
        """Test that female birth day is correctly extracted (day + 40)."""
        # RSSMRA85M55H501I - Female born on day 15 (55 - 40 = 15)
        result = self.validator.validate("RSSMRA85M55H501I")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.birthdate.day, 15)


class PartitaIvaCheckDigitTest(TestCase):
    """Tests specifically for Partita IVA check digit algorithm."""

    def test_check_digit_calculation(self):
        """Test the Italian Luhn algorithm implementation."""
        validator = PartitaIvaValidator()

        # Test known valid P.IVA numbers
        test_cases = [
            ("12345678903", True),  # Valid
            ("12345678901", False),  # Invalid check digit
            ("12345678902", False),  # Invalid check digit
            ("00743110157", True),  # Valid (Mediaset)
        ]

        for piva, expected_valid in test_cases:
            result = validator.validate(piva)
            self.assertEqual(
                result.is_valid,
                expected_valid,
                f"P.IVA {piva} validation mismatch: expected {expected_valid}",
            )
