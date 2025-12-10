# Italian Tax Validators

A comprehensive Python library for validating Italian fiscal identification documents:

- **Codice Fiscale (CF)**: Italian personal tax identification code
- **Partita IVA (P.IVA)**: Italian VAT registration number

## Features

✅ **Codice Fiscale Validation**
- Format validation
- Omocodia handling (substitution of digits with letters)
- Check digit verification
- Birthdate extraction from CF
- Age calculation
- Minimum age verification (18+ by default)

✅ **Partita IVA Validation**
- Format validation
- Check digit verification using Italian Luhn algorithm variant
- Flexible input handling (spaces, prefixes)

✅ **Easy to Use**
- Simple, intuitive API
- Detailed validation results with error codes
- Type hints for better IDE support
- Zero external dependencies

## Installation

```bash
pip install italian-tax-validators
```

## Quick Start

### Validating Codice Fiscale

```python
from italian_tax_validators import validate_codice_fiscale

# Basic validation
result = validate_codice_fiscale("RSSMRA85M01H501Q")
print(result.is_valid)  # True
print(result.birthdate)  # 1985-08-01
print(result.age)  # 39 (or current age)

# With age verification
result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True)
print(result.is_valid)  # True (person is 18+)

# With custom minimum age
result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True, minimum_age=21)
print(result.is_valid)  # True (person is 21+)
```

### Validating Partita IVA

```python
from italian_tax_validators import validate_partita_iva

# Basic validation
result = validate_partita_iva("12345678903")
print(result.is_valid)  # True
print(result.formatted_value)  # "12345678903"

# Flexible input handling
result = validate_partita_iva("123 456 78903")  # Works with spaces
result = validate_partita_iva("IT12345678903")  # Works with IT prefix
```

## API Reference

### Codice Fiscale

#### Function: `validate_codice_fiscale()`

```python
def validate_codice_fiscale(
    value: str,
    check_adult: bool = False,
    minimum_age: int = 18,
) -> CodiceFiscaleValidationResult
```

**Parameters:**
- `value` (str): The CF string to validate
- `check_adult` (bool): Whether to verify minimum age requirement (default: False)
- `minimum_age` (int): Minimum age required in years (default: 18)

**Returns:** `CodiceFiscaleValidationResult` with:
- `is_valid` (bool): Whether the CF is valid
- `error_code` (str | None): Error code if invalid
- `formatted_value` (str): Cleaned/formatted CF value
- `birthdate` (date | None): Extracted birthdate
- `age` (int | None): Calculated age in years

**Error Codes:**
- `tax_id_cf_invalid_format`: Invalid format or check digit
- `tax_id_cf_cannot_decode_birthdate`: Cannot extract birthdate
- `tax_id_cf_underage`: Person is younger than minimum age requirement

#### Class: `CodiceFiscaleValidator`

For advanced usage, create a validator instance:

```python
from italian_tax_validators import CodiceFiscaleValidator

validator = CodiceFiscaleValidator()
result = validator.validate("RSSMRA85M01H501Q")
```

### Partita IVA

#### Function: `validate_partita_iva()`

```python
def validate_partita_iva(value: str) -> PartitaIvaValidationResult
```

**Parameters:**
- `value` (str): The P.IVA string to validate

**Returns:** `PartitaIvaValidationResult` with:
- `is_valid` (bool): Whether the P.IVA is valid
- `error_code` (str | None): Error code if invalid
- `formatted_value` (str): Cleaned/formatted P.IVA value

**Error Codes:**
- `tax_id_piva_invalid_length`: Not exactly 11 digits
- `tax_id_piva_invalid_check_digit`: Check digit verification failed

#### Class: `PartitaIvaValidator`

For advanced usage:

```python
from italian_tax_validators import PartitaIvaValidator

validator = PartitaIvaValidator()
result = validator.validate("12345678903")
```

## Codice Fiscale Structure

The Italian Codice Fiscale is a 16-character alphanumeric code:

```
RSSMRA85M01H501Q
├─ RSS    → Surname (first 3 consonants)
├─ MRA    → Name (first 3 consonants)
├─ 85     → Birth year (1985)
├─ M      → Birth month (M = August)
├─ 01     → Birth day (01), or +40 for females
├─ H501   → Birth place code
└─ Q      → Check digit
```

### Month Codes
- A=January, B=February, C=March, D=April, E=May, H=June
- L=July, M=August, P=September, R=October, S=November, T=December

### Omocodia
When multiple people share the same CF, digits can be replaced with letters:
- L=0, M=1, N=2, P=3, Q=4, R=5, S=6, T=7, U=8, V=9

The validator automatically handles these substitutions.

## Partita IVA Structure

The Italian Partita IVA is an 11-digit number:

```
12345678903
├─ 1234567  → Company registration number
├─ 890      → Provincial office code
└─ 3        → Check digit (Luhn algorithm variant)
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Or with unittest:

```bash
python -m unittest discover tests/
```

## Examples

### Example 1: Processing a list of tax IDs

```python
from italian_tax_validators import validate_codice_fiscale, validate_partita_iva

# Validate multiple CFs
cfs = [
    "RSSMRA85M01H501Q",
    "BNCRSU90A01H501A",
    "invalid_cf_code"
]

for cf in cfs:
    result = validate_codice_fiscale(cf)
    if result.is_valid:
        print(f"✓ {cf} - Born: {result.birthdate}, Age: {result.age}")
    else:
        print(f"✗ {cf} - Error: {result.error_code}")

# Validate P.IVA numbers
pivas = ["12345678903", "IT12345678903", "invalid"]

for piva in pivas:
    result = validate_partita_iva(piva)
    print(f"{'✓' if result.is_valid else '✗'} {piva}")
```

### Example 2: Django integration

```python
from django.db import models
from italian_tax_validators import validate_codice_fiscale

class Person(models.Model):
    codice_fiscale = models.CharField(
        max_length=16,
        validators=[
            lambda x: validate_codice_fiscale(x, check_adult=True) or None
        ]
    )
```

### Example 3: Form validation with Pydantic

```python
from pydantic import BaseModel, field_validator
from italian_tax_validators import validate_codice_fiscale

class PersonForm(BaseModel):
    codice_fiscale: str
    
    @field_validator('codice_fiscale')
    @classmethod
    def validate_cf(cls, v):
        result = validate_codice_fiscale(v, check_adult=True)
        if not result.is_valid:
            raise ValueError(f"Invalid Codice Fiscale: {result.error_code}")
        return v
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on GitHub.

## Disclaimer

This library provides validation utilities for Italian tax identification documents. Always verify the results with official sources and compliance requirements.

## Resources

- [Agenzia delle Entrate](https://www.agenziaentrate.gov.it/) - Official Italian Tax Agency
- [Codice Fiscale Format](https://en.wikipedia.org/wiki/Fiscal_code) - Wikipedia
- [Partita IVA Format](https://en.wikipedia.org/wiki/VAT_identification_number) - Wikipedia
