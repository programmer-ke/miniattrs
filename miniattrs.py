"""miniattrs - a collection of validation fields"""

import copy
import inspect


class _MissingType:
    def __repr__(self):
        return "<MISSING>"


_MISSING = _MissingType()


def define(cls):

    annotations = {}

    for klass in reversed(cls.__mro__):
        # walk down the inheritance chain collecting annotations
        annotations.update(inspect.get_annotations(klass))

    if not annotations:
        raise TypeError("@define requires at least one annotated attribute")

    compulsory, optional = [], []
    for name, field_type in annotations.items():
        descriptor_kwargs = {}
        descriptor_instance = None
        attr_with_default = False

        attr = getattr(cls, name, _MISSING)
        if attr is not _MISSING:
            # attribute is reachable in class bodies in the inheritance chain
            # determine whether it is a descriptor instance or actual value
            if isinstance(attr, Field):
                descriptor_instance = attr
                attr_with_default = descriptor_instance._has_default()
            else:
                descriptor_kwargs["default"] = attr
                attr_with_default = True

            # determine whether attr is optional or not
            if attr_with_default:
                optional.append(name)
            else:
                compulsory.append(name)
        else:
            # value missing from class body
            compulsory.append(name)

        if descriptor_instance is None:
            descriptor_instance = Field(**descriptor_kwargs)

        setattr(cls, name, descriptor_instance)
        descriptor_instance.__set_name__(cls, name)

        descriptor_instance._set_type_validator(field_type, name)

        if descriptor_instance._has_default():
            descriptor_instance._validate_default()

    field_names = compulsory + optional
    init_code = _build_init(compulsory, optional)
    cls.__init__ = _make_init(init_code)
    cls.__eq__ = _make_eq(field_names)
    cls.__repr__ = _make_repr(field_names)
    return cls


def _make_repr(field_names):

    def __repr__(self):
        cls_name = type(self).__name__
        kwargs = ", ".join([f"{f}={getattr(self, f)!r}" for f in field_names])
        return f"{cls_name}({kwargs})"

    return __repr__


def _make_eq(field_names):

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all([getattr(self, f) == getattr(other, f) for f in field_names])
        return NotImplemented

    return __eq__


def _make_init(code):
    namespace = {"_MISSING": _MISSING}
    exec(code, namespace)
    return namespace["__init__"]


def _build_init(compulsory=None, optional=None):
    """Creates __init__ based on provided keyword arguments"""

    if not (compulsory or optional):
        raise ValueError(f"Expected compulsory or optional init parameters")

    compulsory_kwargs = ", ".join(compulsory) if compulsory else ""
    optional_kwargs = (
        ", ".join(f"{field}=_MISSING" for field in optional) if optional else ""
    )
    both_provided = all([compulsory, optional])
    kwargs = (
        ", ".join([compulsory_kwargs, optional_kwargs])
        if both_provided
        else compulsory_kwargs + optional_kwargs
    )
    head = f"\ndef __init__(self, *, {kwargs}):\n"
    compulsory_body = (
        [f"    setattr(self, '{n}', {n})\n" for n in compulsory] if compulsory else []
    )
    optional_body = (
        [f"    if {n} is not _MISSING: setattr(self, '{n}', {n})\n" for n in optional]
        if optional
        else []
    )
    return "".join([head] + compulsory_body + optional_body)


def _validate_type(expected_type, attr_name):
    """Creates a type validator for the attribute"""

    def validator(value):
        if not isinstance(value, expected_type):
            expected_type_name = expected_type.__name__
            value_type = type(value).__name__
            raise TypeError(
                f"{attr_name}: expected type {expected_type_name}, instead got type {value_type}"
            )
        return value

    return validator


class Field:
    _NULL = _MissingType()

    def __init__(self, *, default=_NULL, validators=()):
        self._default = default
        self._validators = tuple(validators)

    def __set_name__(self, owner, name):
        self._field_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = instance.__dict__.get(self._field_name, self._default)
        if value is self._NULL:
            msg = f"Attribute '{self._field_name}' not set"
            raise AttributeError(msg)

        if value is self._default:
            # Create instance copy on first access
            value = instance.__dict__[self._field_name] = copy.deepcopy(value)
        return value

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self._field_name] = value

    def validate(self, value):
        for validator in self._validators:
            validator(value)

    def _has_default(self):
        return self._default is not self._NULL

    def _set_type_validator(self, expected_type, attr_name):
        self._validators = (
            _validate_type(expected_type, attr_name),
        ) + self._validators

    def _validate_default(self):
        self.validate(self._default)


def validate_length(*, min_length=None, max_length=None):

    if min_length is not None and not isinstance(min_length, int):
        raise TypeError(f"Expected min_length to be type int, not {type(min_length)}")

    if max_length is not None and not isinstance(max_length, int):
        raise TypeError(f"Expected max_length to be type int, not {type(max_length)}")

    if min_length is not None and max_length is not None and min_length > max_length:
        raise ValueError("min_length cannot be greater than max_length")
    if min_length is not None and min_length < 0:
        raise ValueError("min_length cannot be < 0")
    if max_length is not None and max_length < 0:
        raise ValueError("max_length cannot be < 0")

    def validator(value):
        if min_length is not None and len(value) < min_length:
            raise ValueError(
                f"Expected minimum length of {min_length}, got {len(value)}"
            )
        if max_length is not None and len(value) > max_length:
            raise ValueError(
                f"Expected maximum length of {max_length}, got {len(value)}"
            )

    return validator
