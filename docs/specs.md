## MVP Spec: Reusable Field Descriptors

### Core Concept
A set of Python descriptor classes that perform validation and type
coercion on instance attributes. Fields are declared as class
attributes in user-defined model-like classes.

### Base Class: `Field`
- **`__init__(self, default=None)`** — accepts an optional static
  default value.
- **`__set_name__(self, owner, name)`** — automatically captures the
  attribute name.
- **`__get__(self, instance, owner)`** — returns the stored value from
  `instance.__dict__[self.name]` if set; otherwise returns `default`
  if provided; otherwise raises `AttributeError`.
- **`__set__(self, instance, value)`** — calls `self.validate(value)`,
  then stores the validated value in `instance.__dict__[self.name]`.
- **`validate(self, value)`** — abstract method; subclasses override
  with their validation logic. Raises `TypeError` for wrong type,
  `ValueError` for constraint violations.

### Concrete Fields

#### `IntegerField(Field)`
- **`validate`**: raises `TypeError` if value is not `int`. No
  coercion.

#### `StringField(Field)`
- **`__init__(self, default=None, min_length=None, max_length=None)`**
- **`validate`**: raises `TypeError` if value is not `str`. Raises
  `ValueError` if `min_length` is set and `len(value) < min_length`,
  or if `max_length` is set and `len(value) > max_length`. Bounds are
  inclusive.

#### `RangeField(Field)`
- **`__init__(self, default=None, min=None, max=None)`** — both `min`
  and `max` are required.
- **`validate`**: raises `TypeError` if value is not `int` or
  `float`. Raises `ValueError` if `value < min` or `value >
  max`. Bounds are inclusive.

### Compound Fields (via Inheritance)

#### `ListField(ParentField)`
- Inherits from a concrete field (e.g., `ListField(IntegerField)`).
- **`validate`**: raises `TypeError` if value is not a `list`. Then
  calls the parent's `validate` on every element of the list. If any
  element fails, the corresponding exception propagates.
- Constructor accepts the same arguments as the parent field.

### Error Handling
- `TypeError` for type mismatches.
- `ValueError` for constraint violations (range, length, etc.).

### Storage
- Validated values are stored directly in `instance.__dict__` under
  the public field name.
- Default values are returned on access but **not stored** in
  `instance.__dict__`.
