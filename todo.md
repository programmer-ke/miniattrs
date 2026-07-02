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

## Task 6: `RangeField` with Inclusive Numeric Bounds

**As a developer**, I want to use `RangeField(min, max)` that accepts
only `int` or `float` values within inclusive bounds, so that I can
enforce numeric range constraints on my model attributes.

- [ ] Implement `RangeField.__init__` with required `min` and `max`
- [ ] Implement `validate` raising `TypeError` for
      non-`int`/non-`float`
- [ ] Implement `validate` raising `ValueError` for out-of-range
      values
- [ ] Test valid values, type errors, and range errors
- [ ] Test default value behavior

---

## Task 7: Compound Field via Composition — `ListField(IntegerField())`

**As a developer**, I want to define `ListField` that delegates to a
encapsulated field (e.g., `IntegerField`) and validates that every element
in a list passes the parent's validation, so that I can enforce typed
lists in my model classes.

- [ ] Implement `ListField(Field())`
- [ ] Implement `validate` raising `TypeError` for non-`list`
- [ ] Implement `validate` calling members `validate` on each element
- [ ] Test valid list of integers
- [ ] Test invalid list (non-list, non-integer elements)
- [ ] Test default value behavior

---

## Task 8: Integration Test — Model Class with Multiple Fields

**As a developer**, I want to define a model class using all field
types together, so that I can verify the descriptors work correctly as
a cohesive validation layer.

- [ ] Create a test model class with `IntegerField`, `StringField`,
      `RangeField`, and `ListField(IntegerField())`
- [ ] Test setting valid values on all fields
- [ ] Test setting invalid values on each field
- [ ] Test default values and unset attribute access
- [ ] Test that fields are independent (setting one doesn't affect
      others)
