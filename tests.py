import pytest
import math
from miniattrs import Field, IntegerField, StringField, FloatField
from hypothesis import given, strategies as st


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


def test_default_integer_must_be_keyword():

    # given a class with an integer field with a default
    with pytest.raises(TypeError):

        class Pet:
            age = IntegerField(3)


def test_default_integer_value_can_be_overwritten():

    # given a class with an integer field with a default
    class Pet:
        age = IntegerField(default=3)

    # when a non default is set
    p = Pet()
    p.age = 5
    # then the default is overriden
    assert p.age == 5


def test_an_incorrect_integer_default_raises():

    # given a class with an integer field and incorrect default
    # when it is instantiated
    # then it raises a type error
    bad_values = ["2", 2.0]
    for v in bad_values:
        with pytest.raises(TypeError):

            class Pet:
                age = IntegerField(default=v)


def test_string_field_rejects_non_string():

    # given a class with a string field
    class Pet:
        name = StringField()

    # when an object is assigned a non string
    p = Pet()

    # then it raises a type error
    with pytest.raises(TypeError):
        p.name = 123


def test_string_field_accepts_strings():
    # given a class with a string field
    class Pet:
        name = StringField()

    # when an object is assigned a string
    p = Pet()
    p.name = "tina"
    # then it stored in the instance
    assert p.name == "tina"


def test_string_min_length_is_validated():
    # given a class with a min length string field
    class Pet:
        name = StringField(min_length=2)

    # when if a smaller length str is provided
    # then a value error is raised
    p = Pet()
    with pytest.raises(ValueError):
        p.name = "a"

    # when a equal or larger string is provided
    valid_strs = ["jo", "bosco"]

    # then the string is stored
    for value in valid_strs:
        p.name = value
        assert p.name == value


def test_string_max_length_is_validated():
    # given a class with a max length string field
    class Pet:
        name = StringField(max_length=4)

    # when if a larger str is provided
    # then a value error is raised
    p = Pet()
    with pytest.raises(ValueError):
        p.name = "tinaturner"

    # when a equal or smaller string is provided
    valid_strs = ["jo", "tina"]

    # then the string is stored
    for value in valid_strs:
        p.name = value
        assert p.name == value


def test_string_field_edge_cases():

    # Both min and max are validated
    class Pet:
        name = StringField(min_length=2, max_length=4)

    valid_strs = ["ab", "abc", "abcd"]

    for val in valid_strs:
        p = Pet()
        p.name = val
        assert p.name == val

    invalid_strs = ["a", "abcde"]
    for val in invalid_strs:
        p = Pet()
        with pytest.raises(ValueError):
            p.name = val

    # min length cannot be larger than max length
    with pytest.raises(ValueError):

        class Pet:
            name = StringField(min_length=3, max_length=2)


@given(st.integers(), st.integers())
def test_string_field_length_behaviour(min_, max_):

    if min_ > max_:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(min_length=min_, max_length=max_)

    if min_ < 0:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(min_length=min_)

    if max_ < 0:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(max_length=max_)

    if max_ == 0:

        class Pet:
            name = StringField(max_length=max_)

        p = Pet()

        with pytest.raises(ValueError):
            p.name = "bob"

        p.name = ""
        assert p.name == ""


@given(st.integers(), st.integers(), st.text())
def test_default_string_behaviour(min_, max_, text):

    if len(text) < min_:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(min_length=min_, default=text)

    if len(text) > max_:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(max_length=max_, default=text)

    if not min_ <= len(text) <= max_:
        with pytest.raises(ValueError):

            class Pet:
                name = StringField(min_length=min_, max_length=max_, default=text)

    if min_ <= len(text) <= max_ and min_ >= 0:

        class Pet:
            name = StringField(min_length=min_, max_length=max_, default=text)

        p = Pet()
        assert p.name == text


def test_that_stringfield_lengths_should_be_integers():

    with pytest.raises(TypeError):

        class Pet:
            name = StringField(max_length="foo")

    with pytest.raises(TypeError):

        class Pet:
            name = StringField(min_length=2.5)


def test_stringfield_accepts_only_keyword_arguments():

    with pytest.raises(TypeError):

        class Pet:
            name = StringField(2, 3)

    with pytest.raises(TypeError):

        class Pet:
            name = StringField("hello")


@given(st.one_of(st.integers() | st.floats() | st.text() | st.none()))
def test_floatfield_raises_on_non_float_value(value):

    class Item:
        price = FloatField()

    if not isinstance(value, float):

        # Raises an error when we try to assign non integer
        i = Item()
        with pytest.raises(TypeError):
            i.price = value

        # Raises error with non-float default
        with pytest.raises(TypeError):

            class SomeItem:
                price = FloatField(default=value)

    elif not math.isnan(value):

        # accepts float
        i = Item()
        i.price = value
        assert i.price == value

        # Accepts float as default value
        class SomeItem:
            price = FloatField(default=value)

        i = SomeItem()
        assert i.price == value
