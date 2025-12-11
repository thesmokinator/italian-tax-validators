# API Reference

Complete API documentation for the Italian Tax Validators library.

## Table of Contents

- [Validation Functions](#validation-functions)
  - [validate_codice_fiscale()](#validate_codice_fiscale)
  - [validate_partita_iva()](#validate_partita_iva)
- [Generation Functions](#generation-functions)
  - [generate_codice_fiscale()](#generate_codice_fiscale)
- [Municipality Functions](#municipality-functions)
  - [get_municipality_info()](#get_municipality_info)
  - [get_cadastral_code()](#get_cadastral_code)
  - [search_municipality()](#search_municipality)
  - [is_foreign_country()](#is_foreign_country)
- [Result Classes](#result-classes)
  - [CodiceFiscaleValidationResult](#codicefiscalevalidationresult)
  - [PartitaIvaValidationResult](#partitaivavalidationresult)
  - [CodiceFiscaleGenerationResult](#codicefiscalegenerationresult)
- [Validator Classes](#validator-classes)
  - [CodiceFiscaleValidator](#codicefiscalevalidator)
  - [PartitaIvaValidator](#partitaivavalidator)
  - [CodiceFiscaleGenerator](#codicefiscalegenerator)
- [Constants](#constants)
- [Type Aliases](#type-aliases)
- [Error Codes](#error-codes)

---

## Validation Functions

### validate_codice_fiscale()

Validate an Italian Codice Fiscale (personal tax identification code).

```python
def validate_codice_fiscale(
    value: str,
    check_adult: bool = False,
    minimum_age: int = 18,
) -> CodiceFiscaleValidationResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `str` | required | The CF string to validate |
| `check_adult` | `bool` | `False` | Whether to verify minimum age requirement |
| `minimum_age` | `int` | `18` | Minimum age required in years |

**Returns:** [`CodiceFiscaleValidationResult`](#codicefiscalevalidationresult)

**Example:**

```python
from italian_tax_validators import validate_codice_fiscale

# Basic validation
result = validate_codice_fiscale("RSSMRA85M01H501Q")
print(result.is_valid)           # True
print(result.formatted_value)    # "RSSMRA85M01H501Q"
print(result.birthdate)          # datetime.date(1985, 8, 1)
print(result.age)                # 40
print(result.gender)             # "M"
print(result.birth_place_code)   # "H501"
print(result.birth_place_name)   # "ROMA"
print(result.birth_place_province)  # "RM"
print(result.is_foreign_born)    # False

# With age verification
result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True)
if not result.is_valid:
    print(f"Error: {result.error_code}")  # "tax_id_cf_underage" if under 18

# With custom minimum age
result = validate_codice_fiscale("RSSMRA85M01H501Q", check_adult=True, minimum_age=21)
```

---

### validate_partita_iva()

Validate an Italian Partita IVA (VAT identification number).

```python
def validate_partita_iva(value: str) -> PartitaIvaValidationResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `value` | `str` | required | The P.IVA string to validate |

**Returns:** [`PartitaIvaValidationResult`](#partitaivavalidationresult)

**Example:**

```python
from italian_tax_validators import validate_partita_iva

# Basic validation
result = validate_partita_iva("12345678903")
print(result.is_valid)        # True
print(result.formatted_value) # "12345678903"
print(result.province_code)   # "890"
print(result.is_temporary)    # False

# Flexible input (spaces and IT prefix are handled)
result = validate_partita_iva("IT 123 456 78903")
print(result.is_valid)        # True
print(result.formatted_value) # "12345678903"

# Temporary VAT number detection
result = validate_partita_iva("99000000002")
print(result.is_temporary)    # True
```

---

## Generation Functions

### generate_codice_fiscale()

Generate an Italian Codice Fiscale from personal data.

```python
def generate_codice_fiscale(
    surname: str,
    name: str,
    birthdate: date,
    gender: Gender,
    birth_place_code: str,
) -> CodiceFiscaleGenerationResult
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `surname` | `str` | required | Person's surname |
| `name` | `str` | required | Person's first name |
| `birthdate` | `date` | required | Date of birth |
| `gender` | `Gender` | required | `"M"` for male, `"F"` for female |
| `birth_place_code` | `str` | required | 4-character cadastral code |

**Returns:** [`CodiceFiscaleGenerationResult`](#codicefiscalegenerationresult)

**Example:**

```python
from datetime import date
from italian_tax_validators import generate_codice_fiscale

# Generate CF
result = generate_codice_fiscale(
    surname="Rossi",
    name="Mario",
    birthdate=date(1985, 8, 1),
    gender="M",
    birth_place_code="H501"  # Rome
)

if result.is_valid:
    print(result.codice_fiscale)  # "RSSMRA85M01H501Q"
else:
    print(f"Error: {result.error_code}")

# Female example
result = generate_codice_fiscale(
    surname="Rossi",
    name="Maria",
    birthdate=date(1985, 8, 1),
    gender="F",
    birth_place_code="H501"
)
print(result.codice_fiscale)  # "RSSMRA85M41H501U" (note: day 41 = 1 + 40)
```

---

## Municipality Functions

### get_municipality_info()

Get municipality name and province from cadastral code.

```python
def get_municipality_info(cadastral_code: str) -> tuple[str, str] | None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cadastral_code` | `str` | 4-character cadastral code |

**Returns:** `tuple[str, str]` (municipality_name, province_code) or `None` if not found

**Example:**

```python
from italian_tax_validators import get_municipality_info

info = get_municipality_info("H501")
print(info)  # ("ROMA", "RM")

info = get_municipality_info("F205")
print(info)  # ("MILANO", "MI")

info = get_municipality_info("Z109")
print(info)  # ("FRANCIA", "EE")  # Foreign countries have "EE" as province

info = get_municipality_info("X999")
print(info)  # None (not found)
```

---

### get_cadastral_code()

Get cadastral code from municipality name (exact match).

```python
def get_cadastral_code(municipality_name: str) -> str | None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `municipality_name` | `str` | Municipality name (case-insensitive) |

**Returns:** `str` (cadastral code) or `None` if not found

**Example:**

```python
from italian_tax_validators import get_cadastral_code

code = get_cadastral_code("ROMA")
print(code)  # "H501"

code = get_cadastral_code("milano")  # Case-insensitive
print(code)  # "F205"

code = get_cadastral_code("Unknown City")
print(code)  # None
```

---

### search_municipality()

Search municipalities by partial name.

```python
def search_municipality(partial_name: str) -> list[tuple[str, str, str]]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `partial_name` | `str` | Partial municipality name to search |

**Returns:** `list[tuple[str, str, str]]` - List of (cadastral_code, municipality_name, province_code)

**Example:**

```python
from italian_tax_validators import search_municipality

results = search_municipality("MILAN")
for code, name, province in results:
    print(f"{code}: {name} ({province})")
# F205: MILANO (MI)

results = search_municipality("ROMA")
# [("H501", "ROMA", "RM"), ("Z124", "ROMANIA", "EE")]
```

---

### is_foreign_country()

Check if a cadastral code represents a foreign country.

```python
def is_foreign_country(cadastral_code: str) -> bool
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cadastral_code` | `str` | 4-character cadastral code |

**Returns:** `bool` - `True` if code starts with "Z" (foreign country)

**Example:**

```python
from italian_tax_validators import is_foreign_country

print(is_foreign_country("Z109"))  # True (France)
print(is_foreign_country("H501"))  # False (Rome)
```

---

## Result Classes

### CodiceFiscaleValidationResult

Result of Codice Fiscale validation.

```python
@dataclass
class CodiceFiscaleValidationResult:
    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None
    birthdate: date | None = None
    age: int | None = None
    gender: Gender | None = None
    birth_place_code: str | None = None
    birth_place_name: str | None = None
    birth_place_province: str | None = None
    is_foreign_born: bool | None = None
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_valid` | `bool` | Whether the CF is valid |
| `error_code` | `str \| None` | Error code if invalid |
| `formatted_value` | `str \| None` | Cleaned/formatted CF value |
| `birthdate` | `date \| None` | Extracted birthdate |
| `age` | `int \| None` | Calculated age in years |
| `gender` | `Gender \| None` | `"M"` or `"F"` |
| `birth_place_code` | `str \| None` | 4-character cadastral code |
| `birth_place_name` | `str \| None` | Municipality/country name |
| `birth_place_province` | `str \| None` | Province code or "EE" for foreign |
| `is_foreign_born` | `bool \| None` | True if born outside Italy |

---

### PartitaIvaValidationResult

Result of Partita IVA validation.

```python
@dataclass
class PartitaIvaValidationResult:
    is_valid: bool
    error_code: str | None = None
    formatted_value: str | None = None
    is_temporary: bool | None = None
    province_code: str | None = None
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_valid` | `bool` | Whether the P.IVA is valid |
| `error_code` | `str \| None` | Error code if invalid |
| `formatted_value` | `str \| None` | Cleaned/formatted P.IVA value |
| `is_temporary` | `bool \| None` | True if VAT starts with "99" |
| `province_code` | `str \| None` | Provincial office code (digits 8-10) |

---

### CodiceFiscaleGenerationResult

Result of Codice Fiscale generation.

```python
@dataclass
class CodiceFiscaleGenerationResult:
    is_valid: bool
    error_code: str | None = None
    codice_fiscale: str | None = None
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `is_valid` | `bool` | Whether generation was successful |
| `error_code` | `str \| None` | Error code if generation failed |
| `codice_fiscale` | `str \| None` | The generated CF |

---

## Validator Classes

### CodiceFiscaleValidator

Validator class for Codice Fiscale with instance methods.

```python
class CodiceFiscaleValidator:
    def validate(
        self,
        value: str,
        check_adult: bool = False,
        minimum_age: int = 18,
    ) -> CodiceFiscaleValidationResult: ...
```

**Example:**

```python
from italian_tax_validators import CodiceFiscaleValidator

validator = CodiceFiscaleValidator()
result = validator.validate("RSSMRA85M01H501Q")
```

---

### PartitaIvaValidator

Validator class for Partita IVA with instance methods.

```python
class PartitaIvaValidator:
    def validate(self, value: str) -> PartitaIvaValidationResult: ...
```

**Example:**

```python
from italian_tax_validators import PartitaIvaValidator

validator = PartitaIvaValidator()
result = validator.validate("12345678903")
```

---

### CodiceFiscaleGenerator

Generator class for Codice Fiscale with instance methods.

```python
class CodiceFiscaleGenerator:
    def generate(
        self,
        surname: str,
        name: str,
        birthdate: date,
        gender: Gender,
        birth_place_code: str,
    ) -> CodiceFiscaleGenerationResult: ...
```

**Example:**

```python
from datetime import date
from italian_tax_validators import CodiceFiscaleGenerator

generator = CodiceFiscaleGenerator()
result = generator.generate(
    surname="Rossi",
    name="Mario",
    birthdate=date(1985, 8, 1),
    gender="M",
    birth_place_code="H501"
)
```

---

## Constants

### CF_MONTH_CODES

Mapping of month letters to month numbers.

```python
CF_MONTH_CODES = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "H": 6,
    "L": 7, "M": 8, "P": 9, "R": 10, "S": 11, "T": 12,
}
```

### CF_MONTH_CODES_REVERSE

Mapping of month numbers to month letters.

```python
CF_MONTH_CODES_REVERSE = {
    1: "A", 2: "B", 3: "C", 4: "D", 5: "E", 6: "H",
    7: "L", 8: "M", 9: "P", 10: "R", 11: "S", 12: "T",
}
```

### CF_OMOCODIA_CHARS

Mapping of omocodia letters to digits.

```python
CF_OMOCODIA_CHARS = {
    "L": "0", "M": "1", "N": "2", "P": "3", "Q": "4",
    "R": "5", "S": "6", "T": "7", "U": "8", "V": "9",
}
```

### CF_OMOCODIA_DIGITS

Mapping of digits to omocodia letters.

```python
CF_OMOCODIA_DIGITS = {
    "0": "L", "1": "M", "2": "N", "3": "P", "4": "Q",
    "5": "R", "6": "S", "7": "T", "8": "U", "9": "V",
}
```

### MINIMUM_AGE_YEARS

Default minimum age for adult verification.

```python
MINIMUM_AGE_YEARS = 18
```

### CODICI_CATASTALI

Dictionary of Italian municipality cadastral codes.

```python
CODICI_CATASTALI: dict[str, tuple[str, str]]
# Key: cadastral code (e.g., "H501")
# Value: (municipality_name, province_code) (e.g., ("ROMA", "RM"))
```

---

## Type Aliases

### Gender

```python
Gender = Literal["M", "F"]
```

Used for specifying gender in CF generation and extraction.

---

## Error Codes

### Codice Fiscale Validation Errors

| Error Code | Description |
|------------|-------------|
| `tax_id_cf_invalid_format` | Invalid format or check digit |
| `tax_id_cf_cannot_decode_birthdate` | Cannot extract birthdate from CF |
| `tax_id_cf_underage` | Person is younger than minimum age |

### Partita IVA Validation Errors

| Error Code | Description |
|------------|-------------|
| `tax_id_piva_invalid_length` | Not exactly 11 digits |
| `tax_id_piva_invalid_check_digit` | Check digit verification failed |

### Codice Fiscale Generation Errors

| Error Code | Description |
|------------|-------------|
| `cf_gen_invalid_surname` | Empty or invalid surname |
| `cf_gen_invalid_name` | Empty or invalid name |
| `cf_gen_invalid_gender` | Gender must be "M" or "F" |
| `cf_gen_invalid_birth_place_code` | Birth place code must be 4 characters |

---

## CLI Reference

The package includes a command-line interface.

### Commands

```bash
# Show help
italian-tax-validators --help

# Validate Codice Fiscale
italian-tax-validators validate-cf <value> [--check-adult] [--minimum-age N]

# Validate Partita IVA
italian-tax-validators validate-piva <value>

# Generate Codice Fiscale
italian-tax-validators generate-cf \
    --surname <surname> \
    --name <name> \
    --birthdate <YYYY-MM-DD> \
    --gender <M|F> \
    [--birth-place-code <code>] \
    [--birth-place <name>]

# Search municipalities
italian-tax-validators search-municipality <query> [--limit N]
```

### Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success (valid input) |
| `1` | Failure (invalid input or error) |
