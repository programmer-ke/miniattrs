"""miniattrs - a collection of validation fields"""

import copy
import inspect


class _MissingType:
    def __repr__(self):
        return "<MISSING>"


_MISSING = _MissingType()


def define(cls):
    annotations = inspect.get_annotations(cls)

    if not annotations:
        raise TypeError("@define requires at least one annotated attribute")

    typed_classes = dict(_typed_classes)

    compulsory, optional = [], []
    for name, field_type in annotations.items():
        descriptor_kwargs = {}

        if name in cls.__dict__:
            descriptor_kwargs["default"] = cls.__dict__[name]
            optional.append(name)
        else:
            compulsory.append(name)
        descriptor_instance = globals().get(typed_classes[field_type])(
            **descriptor_kwargs
        )
        setattr(cls, name, descriptor_instance)
        descriptor_instance.__set_name__(cls, name)

    init_code = _build_init(compulsory, optional)
    cls.__init__ = _make_init(init_code)

    return cls


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


class Validator:

    def validate(self, value):
        return value


class Typed(Validator):
    expected_type = object
    _field_name = "typed"

    def validate(self, value):
        """Returns the validated field value"""

        if not isinstance(value, self.expected_type):
            expected_type = self.expected_type.__name__
            value_type = type(value).__name__
            raise TypeError(
                f"{self._field_name}: expected type {expected_type}, instead got type {value_type}"
            )
        return value


class Field(Typed):
    _NULL = _MissingType()

    def __init__(self, *, default=_NULL):
        if default is self._NULL:
            self._default = default
        else:
            self._default = self.validate(default)

    def __set_name__(self, owner, name):
        self._field_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__.get(self._field_name, self._default)
        if value is self._NULL:
            msg = f"Attribute '{self._field_name}' not set"
            raise AttributeError(msg)
        return value if value is not self._default else copy.deepcopy(value)

    def __set__(self, instance, value):
        value = self.validate(value)
        instance.__dict__[self._field_name] = value


_typed_classes = ((int, "Integer"),)


class Integer(Field):
    expected_type = int


class Float:
    expected_type = float


class String(Field):
    expected_type = str

    def __init__(self, *, min_length=None, max_length=None, **kwargs):

        if min_length is not None and not isinstance(min_length, int):
            raise TypeError(
                f"Expected min_length to be type int, not {type(min_length)}"
            )

        if max_length is not None and not isinstance(max_length, int):
            raise TypeError(
                f"Expected max_length to be type int, not {type(max_length)}"
            )

        if (
            min_length is not None
            and max_length is not None
            and min_length > max_length
        ):
            raise ValueError(f"min_length cannot be greater than max_length")
        if min_length is not None and min_length < 0:
            raise ValueError(f"min_length cannot be < 0")
        if max_length is not None and max_length < 0:
            raise ValueError("max_length cannot be < 0")

        self._min_length = min_length
        self._max_length = max_length

        super().__init__(**kwargs)

    def validate(self, value):

        super().validate(value)

        if self._min_length is not None and len(value) < self._min_length:
            raise ValueError(
                f"Expected minimum length of {self._min_length}, got {len(value)}"
            )
        if self._max_length is not None and len(value) > self._max_length:
            raise ValueError(
                f"Expected maximum length of {self._max_length}, got {len(value)}"
            )
        return value
