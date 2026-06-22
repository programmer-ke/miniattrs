import pytest
from miniattrs import Field, IntegerField


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


def test_integer_field_raises_on_non_integer():

    # given a class with an integer field

    class Pet:
        age = IntegerField()

        def __init__(self, age):
            self.age = age

    # when a non integer is assigned
    bad_values = ["2", 2.0]
    # then a validation error is raised
    for v in bad_values:
        with pytest.raises(TypeError):
            p = Pet(v)


def test_integer_field_accepts_integer():

    # given a class with an integer field
    class Pet:
        age = IntegerField()

        def __init__(self, age):
            self.age = age

    # when an integer is assigned
    p = Pet(2)

    # then it is successfully stored and returned
    assert p.age == 2


def test_default_integer_value_is_honored():

    # given a class with an integer field with a default
    class Pet:
        age = IntegerField(default=3)

    # when an unnassigned attribute is returned
    p = Pet()

    # then the default is returned on access
    assert p.age == 3


def test_default_integer_value_can_be_overwritten():

    # given a class with an integer field with a default
    class Pet:
        age = IntegerField(default=3)

    # when a non default is set
    p = Pet()
    p.age = 5
    # then the default is overriden
    assert p.age == 5


def test_an_incorrect_default_raises():

    # given a class with an integer field and incorrect default
    # when it is instantiated
    # then it raises a type error
    bad_values = ["2", 2.0]
    for v in bad_values:
        with pytest.raises(TypeError):

            class Pet:
                age = IntegerField(default=v)
