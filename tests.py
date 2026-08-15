import pytest
import math
import decimal
import textwrap
from miniattrs import define, _build_init, Field, validate_length
from hypothesis import given, strategies as st


def test_build_init_with_only_defaults():

    field_names = ["age", "name"]

    assert _build_init(field_names) == (
        textwrap.dedent(
            """
        def __init__(self, *, age, name):
            setattr(self, 'age', age)
            setattr(self, 'name', name)
        """
        )
    )


def test_build_init_with_both_optional_and_defaults():

    field_names = ["age", "name"]
    optional = ["price", "weight"]

    assert _build_init(field_names, optional) == (
        textwrap.dedent(
            """
        def __init__(self, *, age, name, price=_MISSING, weight=_MISSING):
            setattr(self, 'age', age)
            setattr(self, 'name', name)
            if price is not _MISSING: setattr(self, 'price', price)
            if weight is not _MISSING: setattr(self, 'weight', weight)
        """
        )
    )


def test_build_init_with_only_optionals():

    field_names = []
    optional = ["price", "weight"]

    assert _build_init(field_names, optional) == (
        textwrap.dedent(
            """
        def __init__(self, *, price=_MISSING, weight=_MISSING):
            if price is not _MISSING: setattr(self, 'price', price)
            if weight is not _MISSING: setattr(self, 'weight', weight)
        """
        )
    )


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


def test_same_class_same_attrs_should_compare_equal():

    @define
    class Pet:
        name: str
        age: int

    # Given instances with matching attributes
    p1 = Pet(name="tina", age=2)
    p2 = Pet(name="tina", age=2)
    # when compared
    # then they should be equal
    assert p1 == p2


def test_same_class_diff_attrs_should_compare_not_equal():

    @define
    class Pet:
        name: str
        age: int

    # Given instances with different attributes
    p1 = Pet(name="tina", age=2)
    p2 = Pet(name="tommy", age=1)
    # when compared
    # then they should not be equal
    assert p1 != p2


def test_diff_class_same_attrs_should_compare_not_equal():

    @define
    class Cat:
        name: str
        age: int

    @define
    class Dog:
        name: str
        age: int

    # Given different classes with same attributes
    p1 = Cat(name="tina", age=2)
    p2 = Dog(name="tina", age=2)
    # when compared
    # then they should not be equal
    assert p1 != p2


def test_diff_class_diff_attrs_should_compare_not_equal():

    @define
    class Cat:
        name: str
        age: int

    @define
    class Dog:
        name: str
        age: int

    # Given different classes with same attributes
    p1 = Cat(name="tina", age=2)
    p2 = Dog(name="tommy", age=1)
    # when compared
    # then they should not be equal
    assert p1 != p2

    # compare with random objects
    assert p1 != 123
    assert p1 != None
    assert p1 != object()


def test_correct_repr_generated():

    @define
    class Cat:
        name: str
        age: int

    # Given an instantiated class
    p1 = Cat(name="tina", age=2)
    # when repr is output
    assert repr(p1) == "Cat(name='tina', age=2)"
    # then it matches the expected format


@pytest.mark.parametrize("bad_value", ["", "abc", object()])
def test_integer_field_raises_on_non_coerceable_value(bad_value):

    # given a class with an integer field

    @define
    class Pet:
        age: int

    # when a non integer is assigned
    # then a validation error is raised
    with pytest.raises(TypeError):
        _ = Pet(age=bad_value)


def test_integer_field_accepts_integer():

    # given a class with an integer field
    @define
    class Pet:
        age: int

    # when an integer is assigned
    p = Pet(age=2)

    # then it is successfully stored and returned
    assert p.age == 2


def test_float_field_accepts_float():

    # given a class with an float field
    @define
    class Item:
        price: float

    # when an float is assigned
    item = Item(price=2.0)

    # then it is successfully stored and returned
    assert item.price == 2.0


def test_no_annotations_raises():

    # Given a class with no annotated attributes
    # When defined
    # then raise a type error
    with pytest.raises(TypeError):

        @define
        class Foo:
            pass


def test_no_init_kwargs_raises():

    # Given a class with annotated attributes
    @define
    class Foo:
        bar: int

    # when no init kwargs are provided
    # Then raise a type error
    with pytest.raises(TypeError):
        f = Foo()


def test_default_integer_value_is_honored():

    # given a class with an integer field with a default
    @define
    class Pet:
        age: int = 3

    # when value is not provided during init
    p = Pet()

    # then the default is returned on access
    assert p.age == 3


def test_both_optional_and_compulsory_are_handled_correctly():

    # given a class with both optional and compulsory attributes
    @define
    class Pet:
        weight: int
        age: int = 3

    # when compulsory is provided on init
    p = Pet(weight=20)

    # then both are set as expected
    assert p.age == 3
    assert p.weight == 20


def test_default_with_explicit_field_must_be_keyword():

    # given a class with an integer field with a default
    with pytest.raises(TypeError):

        @define
        class Pet:
            age: int = Field(3)


def test_default_integer_value_can_be_overwritten():

    # given a class with an integer field with a default
    @define
    class Pet:
        age: int = 3

    # when a non default is set
    p = Pet(age=5)

    # then the default is overriden
    assert p.age == 5


def test_an_incorrect_integer_default_raises():

    # given a class with an integer field and incorrect default
    # when it is instantiated
    # then it raises a type error
    bad_values = ["2", 2.0]
    for v in bad_values:
        with pytest.raises(TypeError):

            @define
            class Pet:
                age: int = v


def test_string_field_rejects_non_string():

    # given a class with a string field
    @define
    class Pet:
        name: str

    # when an object is assigned a non string
    # then it raises a type error
    with pytest.raises(TypeError):
        p = Pet(name=123)


def test_string_field_accepts_strings():
    # given a class with a string field
    @define
    class Pet:
        name: str

    # when an object is assigned a string
    p = Pet(name="tina")

    # then it stored in the instance
    assert p.name == "tina"


def test_string_min_length_is_validated():
    # given a class with a min length string field
    @define
    class Pet:
        name: str = Field(validators=(validate_length(min_length=2),))

    # when if a smaller length str is provided
    # then a value error is raised
    with pytest.raises(ValueError):
        p = Pet(name="a")

    # when a equal or larger string is provided
    valid_strs = ["jo", "bob"]

    # then the string is stored
    for value in valid_strs:
        p = Pet(name=value)
        assert p.name == value


def test_string_max_length_is_validated():
    # given a class with a max length string field
    @define
    class Pet:
        name: str = Field(validators=(validate_length(max_length=4),))

    # when if a larger str is provided
    # then a value error is raised
    with pytest.raises(ValueError):
        _ = Pet(name="tinaturner")

    # when a equal or smaller string is provided
    valid_strs = ["jo", "tina"]

    p1 = Pet(name="lu")
    # then the string is stored
    for value in valid_strs:
        p1.name = value
        assert p1.name == value
        _ = Pet(name=value)


def test_string_field_edge_cases():

    # Both min and max are validated
    @define
    class Pet:
        name: str = Field(validators=(validate_length(min_length=2, max_length=4),))

    valid_strs = ["ab", "abc", "abcd"]

    for val in valid_strs:
        p = Pet(name=val)
        assert p.name == val

    for val in valid_strs:
        p.name = val

    invalid_strs = ["a", "abcde"]
    for val in invalid_strs:
        with pytest.raises(ValueError):
            _ = Pet(name=val)

        with pytest.raises(ValueError):
            p.name = val

    # min length cannot be larger than max length
    with pytest.raises(ValueError):

        class Pet:
            name: str = Field(validators=(validate_length(min_length=3, max_length=2),))


@given(st.integers(), st.integers())
def test_string_field_length_behaviour(min_, max_):

    if min_ > max_:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(
                    validators=(validate_length(min_length=min_, max_length=max_),)
                )

    if min_ < 0:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(validators=(validate_length(min_length=min_),))

    if max_ < 0:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(validators=(validate_length(max_length=max_),))

    if max_ == 0:

        @define
        class Pet:
            name: str = Field(
                default="", validators=(validate_length(max_length=max_),)
            )

        p = Pet()
        with pytest.raises(ValueError):
            p.name = "bob"
        p.name = ""
        assert p.name == ""


@given(st.integers(), st.integers(), st.text())
def test_default_string_behaviour(min_, max_, text):

    # Invalid length validator parameters should raise ValueError
    if min_ < 0 or max_ < 0 or min_ > max_:
        with pytest.raises(ValueError):
            validate_length(min_length=min_, max_length=max_)
        return

    if len(text) < min_:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(
                    default=text, validators=(validate_length(min_length=min_),)
                )

    if len(text) > max_:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(
                    default=text, validators=(validate_length(max_length=max_),)
                )

    if not min_ <= len(text) <= max_:
        with pytest.raises(ValueError):

            @define
            class Pet:
                name: str = Field(
                    default=text,
                    validators=(validate_length(min_length=min_, max_length=max_),),
                )

    if min_ <= len(text) <= max_:

        @define
        class Pet:
            name: str = Field(
                default=text,
                validators=(validate_length(min_length=min_, max_length=max_),),
            )

        p = Pet()
        assert p.name == text


def test_that_stringfield_lengths_should_be_integers():

    with pytest.raises(TypeError):
        validate_length(max_length="foo")

    with pytest.raises(TypeError):
        validate_length(min_length=2.5)


def test_stringfield_accepts_only_keyword_arguments():

    with pytest.raises(TypeError):
        validate_length(2, 3)

    with pytest.raises(TypeError):
        validate_length("hello")


@given(st.one_of(st.integers() | st.floats() | st.text() | st.none()))
def test_floatfield_raises_on_non_float_value(value):

    @define
    class Item:
        price: float

    if not isinstance(value, float):

        # Raises an error when we try to assign a non-float
        with pytest.raises(TypeError):
            _ = Item(price=value)

        # Raises error with non-float default
        with pytest.raises(TypeError):

            @define
            class SomeItem:
                price: float = value

    elif not math.isnan(value):

        # accepts float
        i = Item(price=value)
        assert i.price == value

        # Accepts float as default value
        @define
        class SomeItem:
            price: float = value

        i = SomeItem()
        assert i.price == value


def test_complex_field_accepts_complex():
    @define
    class Vector:
        value: complex

    v = Vector(value=1 + 2j)
    assert v.value == 1 + 2j


def test_complex_field_rejects_non_complex():
    @define
    class Vector:
        value: complex

    with pytest.raises(TypeError):
        _ = Vector(value=1)
    with pytest.raises(TypeError):
        _ = Vector(value=1.0)
    with pytest.raises(TypeError):
        _ = Vector(value="1+2j")


def test_decimal_field_accepts_decimal():
    @define
    class Price:
        amount: decimal.Decimal

    p = Price(amount=decimal.Decimal("1.5"))
    assert p.amount == decimal.Decimal("1.5")


def test_decimal_field_rejects_non_decimal():
    @define
    class Price:
        amount: decimal.Decimal

    with pytest.raises(TypeError):
        _ = Price(amount=1.5)
    with pytest.raises(TypeError):
        _ = Price(amount=1)
    with pytest.raises(TypeError):
        _ = Price(amount="1.5")


def test_list_field_accepts_list():
    @define
    class ShoppingList:
        items: list

    obj = ShoppingList(items=[1, 2, 3])
    assert obj.items == [1, 2, 3]


def test_list_field_rejects_non_list():
    @define
    class ShoppingList:
        items: list

    with pytest.raises(TypeError):
        _ = ShoppingList(items=(1, 2, 3))
    with pytest.raises(TypeError):
        _ = ShoppingList(items="abc")


def test_mutable_default_not_shared():
    @define
    class ShoppingList:
        items: list = [1, 2]

    a = ShoppingList()
    b = ShoppingList()
    assert a.items == [1, 2]
    assert a.items is not b.items

    a.items = [1, 2, 3]
    assert a.items == [1, 2, 3]
    assert b.items == [1, 2]


def test_mutable_default_set_on_first_access():

    default_items = [1, 2]

    @define
    class ShoppingList:
        items: list = default_items

    a = ShoppingList()
    b = ShoppingList()
    assert a.items == [1, 2]
    assert a.items is not b.items

    assert a.items is not default_items
    a.items.append(3)
    assert a.items == [1, 2, 3]


def test_bool_field_accepts_booleans():
    @define
    class Flag:
        enabled: bool

    assert Flag(enabled=True).enabled is True
    assert Flag(enabled=False).enabled is False


def test_bool_field_rejects_non_bool():
    @define
    class Flag:
        enabled: bool

    with pytest.raises(TypeError):
        _ = Flag(enabled=1)
    with pytest.raises(TypeError):
        _ = Flag(enabled=0)
    with pytest.raises(TypeError):
        _ = Flag(enabled="true")


@given(
    st.lists(st.integers(), min_size=0, max_size=10),
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=0, max_value=10),
)
def test_list_length_validator_accepts_valid_lengths(items, min_len, max_len):
    # Ensure min_len <= max_len for a valid validator
    if min_len > max_len:
        return  # skip invalid parameter combos

    @define
    class ShoppingList:
        items: list = Field(
            validators=(validate_length(min_length=min_len, max_length=max_len),)
        )

    if min_len <= len(items) <= max_len:
        obj = ShoppingList(items=items)
        assert obj.items == items
    else:
        with pytest.raises(ValueError):
            _ = ShoppingList(items=items)


@given(
    st.lists(st.integers(), min_size=0, max_size=10),
    st.integers(min_value=0, max_value=10),
)
def test_list_min_length_validator(items, min_len):
    @define
    class ShoppingList:
        items: list = Field(validators=(validate_length(min_length=min_len),))

    if len(items) >= min_len:
        obj = ShoppingList(items=items)
        assert obj.items == items
    else:
        with pytest.raises(ValueError):
            _ = ShoppingList(items=items)


@given(
    st.lists(st.integers(), min_size=0, max_size=10),
    st.integers(min_value=0, max_value=10),
)
def test_list_max_length_validator(items, max_len):
    @define
    class ShoppingList:
        items: list = Field(validators=(validate_length(max_length=max_len),))

    if len(items) <= max_len:
        obj = ShoppingList(items=items)
        assert obj.items == items
    else:
        with pytest.raises(ValueError):
            _ = ShoppingList(items=items)


@given(
    st.lists(st.integers(), min_size=0, max_size=10),
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=0, max_value=10),
)
def test_list_length_validator_on_assignment(list_items, min_len, max_len):
    if min_len > max_len:
        return

    @define
    class ShoppingList:
        items: list = Field(
            validators=(validate_length(min_length=min_len, max_length=max_len),)
        )

    baseline = list(range(min_len))
    obj = ShoppingList(items=baseline)
    assert obj.items == baseline

    if min_len <= len(list_items) <= max_len:
        obj.items = list_items
        assert obj.items == list_items
    else:
        with pytest.raises(ValueError):
            obj.items = list_items
        assert obj.items == baseline


@given(
    st.lists(st.integers(), min_size=0, max_size=10),
    st.integers(min_value=0, max_value=10),
    st.integers(min_value=0, max_value=10),
)
def test_list_default_length_validator(list_items, min_len, max_len):
    if min_len > max_len:
        return

    # Only test when the default itself is valid
    if min_len <= len(list_items) <= max_len:

        @define
        class ShoppingList:
            items: list = Field(
                default=list_items,
                validators=(validate_length(min_length=min_len, max_length=max_len),),
            )

        obj = ShoppingList()
        assert obj.items == list_items
    else:
        # Default is invalid, should raise at class definition time
        with pytest.raises(ValueError):

            @define
            class ShoppingList:
                items: list = Field(
                    default=list_items,
                    validators=(
                        validate_length(min_length=min_len, max_length=max_len),
                    ),
                )
