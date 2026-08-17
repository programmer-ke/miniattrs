from miniattrs import define, field, validate_length, validate_range
from decimal import Decimal
from pathlib import Path
from fractions import Fraction


# basic usage
@define
class Pet:
    name: str
    age: int


# usage
p = Pet(name="tina", age=2)
reveal_type(p.name)  # should be str
reveal_type(p.age)  # should be int

# assignment
p.name = "tommy"  # should be allowed
p.age = 3  # should be allowed
# p.name = 123        # type checker should flag this
# p.age = "three"     # type checker should flag this


# with defaults
@define
class Item:
    price: float = 0.0
    quantity: int = field(default=1)


i = Item()
reveal_type(i.price)  # float
reveal_type(i.quantity)  # int

# type checker should flag these
# i.price = "free"
# i.quantity = 1.5


# with Field and validators
@define
class User:
    username: str = field(validators=(validate_length(min_length=3, max_length=20),))
    score: int = field(
        default=0, validators=(validate_range(min_value=0, max_value=100),)
    )


u = User(username="alice")
reveal_type(u.username)  # str
reveal_type(u.score)  # int

# type checker should flag these
u.score = "high"
u.username = 123


# inheritance
@define
class Animal:
    sound: str = "..."


@define
class Dog(Animal):
    breed: str


d = Dog(sound="bark", breed="lab")
reveal_type(d.sound)  # str
reveal_type(d.breed)  # str

# type checker should flag these
d.breed = 456
d.sound = True


# using the class in a function with type hints
def get_pet_name(pet: Pet) -> str:
    return pet.name


# type checker should flag these
get_pet_name("not a pet")
get_pet_name(123)


# using the class as a type annotation
pets: list[Pet] = [Pet(name="a", age=1), Pet(name="b", age=2)]

# type checker should flag these
pets.append(Item(price=1.0))
pets[0] = "not a pet"


# decimal
@define
class Price:
    amount: Decimal


price = Price(amount=Decimal("1.5"))
reveal_type(price.amount)  # Decimal

# type checker should flag these
price.amount = 1.5
price.amount = "1.5"


# pathlib.Path
@define
class Config:
    path: Path


c = Config(path=Path("/etc/app.conf"))
reveal_type(c.path)  # Path

# type checker should flag these
c.path = "/etc/app.conf"
c.path = None


# fractions.Fraction
@define
class Ratio:
    value: Fraction


r = Ratio(value=Fraction(1, 3))
reveal_type(r.value)  # Fraction

# type checker should flag these
r.value = 0.333
r.value = "1/3"


# dict
@define
class Settings:
    options: dict


s = Settings(options={"debug": True, "port": 8080})
reveal_type(s.options)  # dict

# type checker should flag these
s.options = [("debug", True)]
s.options = "debug=True"
