import pytest
from miniattrs import Field


class SubField(Field):

    def validate(self, value):
        # override `validate` to allow tests to run
        return value


def test_base_field():
    f = SubField()

    class Klass: ...

    instance = Klass()

    f.__set_name__(Klass, "attr")
    assert f._default is f._NULL
    assert f._field_name == "attr"

    # __get__ should return self when called on the class
    assert f.__get__(None, Klass) is f

    # without a default, should raise AttributeError on access
    with pytest.raises(AttributeError):
        _ = f.__get__(instance, Klass)

    # should now return the set value
    f.__set__(instance, "assigned")
    assert f.__get__(instance, Klass) == "assigned"

    # default value is correctly set
    f = SubField(default="foobar")
    instance = Klass()

    f.__set_name__(Klass, "attr")
    assert f._default == "foobar"

    # should match default value if not set
    assert f.__get__(instance, Klass) == f._default

    # should return set value when set
    f.__set__(instance, "somevalue")
    assert f.__get__(instance, Klass) == "somevalue"


def test_mutable_default_copied():
    f = SubField()

    class Klass: ...

    instance = Klass()

    mutable_default = [1, 2, [3]]
    f = SubField(default=mutable_default)
    f.__set_name__(Klass, "attr")

    # should be equal but not same identity as default
    default_value = f.__get__(instance, Klass)

    assert default_value == mutable_default
    assert default_value is not mutable_default
    assert default_value[2] is not mutable_default[2]

    default_value.append("some other value")

    new_instance = Klass()
    second_default_value = f.__get__(new_instance, Klass)

    # The default value on a different instance should not be the
    # same as that of the first instance
    assert second_default_value is not default_value
