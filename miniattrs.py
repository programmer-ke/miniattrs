"""miniattrs - a collection of validation fields"""

import abc
import copy


class _MissingType:
    def __repr__(self):
        return "<MISSING>"


class Field(abc.ABC):

    _NULL = _MissingType()

    def __init__(self, default=_NULL):
        self._default = default

    def __set_name__(self, owner, name):
        self._field_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.__dict__.get(self._field_name, self._default)
        if self._default is self._NULL:
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
