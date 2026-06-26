"""miniattrs - a collection of validation fields"""

import abc
import copy


class _MissingType:
    def __repr__(self):
        return "<MISSING>"


class Field(abc.ABC):

    _NULL = _MissingType()

    def __init__(self, default=_NULL):
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
            msg = f"Attribute {self._field_name} not set"
            raise AttributeError(msg)
        return value if value is not self._default else copy.deepcopy(value)

    def __set__(self, instance, value):
        value = self.validate(value)
        instance.__dict__[self._field_name] = value

    @abc.abstractmethod
    def validate(self, value):
        """Returns the validated field value"""
        return value


class IntegerField(Field):

    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Expected an integer, not {type(value)}")
        return value


class StringField(Field):

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
        if not isinstance(value, str):
            raise TypeError(f"Expected a string, not {type(value)}")

        if self._min_length is not None and len(value) < self._min_length:
            raise ValueError(
                f"Expected minimum length of {self._min_length}, got {len(value)}"
            )
        if self._max_length is not None and len(value) > self._max_length:
            raise ValueError(
                f"Expected maximum length of {self._max_length}, got {len(value)}"
            )
        return value
