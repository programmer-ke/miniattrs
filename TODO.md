# To Do

# In progress

# Done
## Task 1: Base `Field` Descriptor with `__set_name__` and Storage

**As a developer**, I want to define a `Field` base class that
captures its attribute name via `__set_name__` and stores/retrieves
values from `instance.__dict__`, so that I can build a foundation for
reusable validation descriptors.

- [x] Implement `Field.__init__(self, default=_NULL)`
- [x] Implement `Field.__set_name__(self, owner, name)`
- [x] Implement `Field.__get__` returning stored value, default, or
      raising `AttributeError`
- [x] Implement `Field.__set__` calling `validate` then storing in
      `instance.__dict__`
- [x] Define abstract `validate(self, value)` method raising
      `NotImplementedError`

---

## Task 2: `IntegerField` — Simple Type Validation

**As a developer**, I want to use `IntegerField` that rejects
non-`int` values with `TypeError`, so that I can enforce integer-only
attributes in my model classes.

- [x] Implement `IntegerField(Field)` with `validate` raising
      `TypeError` for non-`int`
- [x] Test that valid `int` values are stored and retrieved correctly
- [x] Test that invalid types raise `TypeError`
- [x] Test default value behavior

---

## Task 3: `StringField` with Optional Length Constraints

**As a developer**, I want to use `StringField` with optional
`min_length`/`max_length` that validates string type and length
bounds, so that I can enforce string constraints on my model
attributes.

- [x] Implement `StringField.__init__` with `min_length=None,
      max_length=None`
- [x] Implement `validate` raising `TypeError` for non-`str`
- [x] Implement `validate` raising `ValueError` for length violations
      (inclusive bounds)
- [x] Test valid strings, type errors, and length errors
- [x] Test default value behavior

---

## Task 4: `FloatField` — Simple Type Validation

**As a developer**, I want to use `FloatField` that rejects
non-`float` values with `TypeError`, so that I can enforce float-only
attributes in my model classes.

- [x] Implement `FloatField(Field)` with `validate` raising
      `TypeError` for non-`float`
- [x] Test that valid `float` values are stored and retrieved correctly
- [x] Test that invalid types raise `TypeError`
- [x] Test default value behavior

---


## Task 5: Refactor to more closely match `attrs` api

- [x] Implement core mechanics:
  - use @define decorator for class creation
  - Validate int type for annotated attributes
  - automatically generate init for annotated attributes
  - Support default values for annotated attributes
- [x] Support additional builtin types
- [x] Support explicit Field declarations
- [ ] Support typechecking with `@dataclass_transform()`
- [x] Automatically generate __eq__
- [x] Automatically generate __repr__
- [x] Support Inheritance

## Task 6: `validate_range` Validator with Inclusive Bounds

**As a developer**, I want to use a validator named
`validate_range(min_value=x, max_value=y)` that accepts any sortable values within
inclusive bounds, so that I can enforce range constraints on my model
attributes.

- [x] Implement `validate_range` with required `min_value` and `max_value` params.
- [x] Implement `validate_range` raising `TypeError` for
      non-sortable parameters
- [x] Implement `validate` raising `ValueError` for out-of-range
      values
- [x] Test default value behavior

# Under Consideration

## Task 7: Compound Field via Composition — `list[int]`

**As a developer**, I want to define `list[int]` that delegates to a
encapsulated type (e.g., `int`) and validates that every element
in a list passes the parent's validation, so that I can enforce typed
lists in my model classes.

- [ ] Implement `list[int]`
- [ ] Implement `validate` raising `TypeError` for non-`list`
- [ ] Implement `validate` calling members `validate` on each element
- [ ] Test valid list of integers
- [ ] Test invalid list (non-list, non-integer elements)
- [ ] Test default value behavior

