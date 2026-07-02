## Minimal Spec: `miniattrs` v2

### Overview
Define data classes with a decorator `@define`. Fields are declared
via **type annotations** and optional **field descriptors** that
provide validation (and later coercion). The decorator auto‑generates
`__init__`, `__eq__`, and `__repr__` while preserving the power of
data descriptors for runtime attribute access.

### User API

```python
from miniattrs import define, , Integer, String

@define
class Pet:
    name: str                              # plain str field, no extra validation beyond type
    age: int = Integer(default=0)     # integer field with default
    species: str = String(default="cat", min_length=1, max_length=100)

# Usage
pet = Pet(name="Fido")                     # age defaults to 0, species to "cat"
pet.name = "Rex"                           # validation runs on assignment
print(pet)                                 # Pet(name='Rex', age=0, species='cat')
print(pet == Pet("Rex"))                   # True (compares all fields)
```

### Core Components

#### 1. `@define` decorator
- A class decorator (or a decorator that can be used with/without
  arguments) that transforms an ordinary class into a validated data
  class.
- **Parameters** (optional, may be added later):
  - `frozen: bool = False` – if `True`, instances become immutable
    after `__init__`.
  - `eq: bool = True` – generate `__eq__`.
  - `repr: bool = True` – generate `__repr__`.
  - `init: bool = True` – generate `__init__`.
  - `strict: bool = True` – if `False`, enable coercion (future).
- **Type checker support**: The decorator is marked with
  `@dataclass_transform()` so that mypy/pyright understand the
  generated `__init__` and attribute types.

#### 2. Field descriptors
- All field descriptors inherit from `miniattrs.Field` (a data
  descriptor).
- `Field` provides:
  - `validate(self, value) -> value` – validates and returns the
    (possibly coerced) value. The default implementation checks
    `isinstance(value, self.field_type)`.
  - `__get__(self, instance, owner)` – returns the stored value or a
    deep copy of the default.
  - `__set__(self, instance, value)` – runs `validate` and stores in
    `instance.__dict__`.
- **Built‑in subclasses**:
  - `Integer` – `field_type = int`
  - `Float` – `field_type = float`
  - `String` – `field_type = str`, with optional `min_length` and
    `max_length` checks.
- **Auto‑creation**: If an annotation has no explicit field instance
  in the class body (e.g., `name: str`), the decorator creates a plain
  `Field(field_type=str)` and attaches it to the class
  automatically. The descriptor’s `__set_name__` is called manually if
  needed.

#### 3. Automatic `__init__`
- Parameters match the field names (all keyword‑only in minimal
  version).
- Fields without a `default` are **required**; fields with a `default`
  are optional and use that value.
- Assignment inside `__init__` is done via `setattr(self, field_name,
  value)`, so the descriptor’s `__set__` (and thus validation) is
  executed.

#### 4. Automatic `__eq__`
- Two instances are equal if all field values compare equal.
- Implemented by the decorator, comparing `getattr(self, field_name)`
  for each field.

#### 5. Automatic `__repr__`
- Returns a string like `ClassName(field1=value1, field2=value2,
  ...)`.
- Iterates over all fields and uses `getattr`.

#### 6. Inheritance
- The decorator walks the MRO and collects fields from parent classes
  as well. Fields from child classes override those from parents (or
  are merged; typically parent fields are inherited, child fields
  added). The generated methods include all fields from the whole
  hierarchy.

### Error Handling (minimal)
- Validation failures raise `TypeError` or `ValueError` (same as
  current code). A future enhancement may introduce a
  `ValidationError` with field paths.

### Coercion
- **Coercion** – attributes will be automatically coerced into the required type

### What stays the same from current `miniattrs.py`
- The core `Field` descriptor with `__set__`/`__get__` and the `_NULL`
  sentinel.
- Mutable defaults are deep‑copied when accessed (unless overridden in
  `__init__`).
- Existing field subclasses (`IntegerField`, `StringField`) continue
  to work.


