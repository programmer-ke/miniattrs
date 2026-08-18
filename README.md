# miniattrs - A minimal validation Data Class

miniattrs is a lightweight, zero dependency and pure Python validation
utility.

It allows your to define a data class with type annotations that are
validated at runtime in addition to being checked statically (the
latter requires Python >= 3.11).

This is useful where you need a data class-like functionality with
runtime validation that can easily be vendored into your project.

## Usage

Define a class that is validated at runtime. An `__init__` with the
expected keyword arguments will be automatically generated.

```python
>>> from miniattrs import define
>>>
>>> @define
... class Pet:
...   name: str
...   age: int
... 
>>> tina = Pet(name='tina', age=2)
>>> tina.age, tina.name
(2, 'tina')
>>> tina.age = 2.0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/projects/miniattrs/miniattrs.py", line 131, in __set__
    self.validate(value)
  File "/projects/miniattrs/miniattrs.py", line 136, in validate
    validator(value)
  File "/projects/miniattrs/miniattrs.py", line 211, in validator
    raise TypeError(
TypeError: age: expected type int, instead got type float
```

Set field defaults.

```python

>>> @define
... class Item:
...   price: float = 0.0
...   quantity: int = 1
... 
>>> i = Item()
>>> i.price, i.quantity
(0.0, 1)
>>> pricy_item = Item(price=2000.0)
>>> pricy_item.price, pricy_item.quantity
(2000.0, 1)
```

Specify length and range validators.

```python

>>> from miniattrs import define, field, validate_length, validate_range
>>> 
>>> @define
... class User:
...   username: str = field(
...     validators=(validate_length(min_length=3, max_length=20),)
...   )
...   score: int = field(
...     default=0,
...     validators=(validate_range(min_value=0, max_value=100),)
...   )
... 
>>> alice = User(username="alice", score=50)
>>> k = User(username="k", score=30)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 3, in __init__
  File "/projects/miniattrs/miniattrs.py", line 131, in __set__
    self.validate(value)
  File "/projects/miniattrs/miniattrs.py", line 136, in validate
    validator(value)
  File "/projects/miniattrs/miniattrs.py", line 237, in validator
    raise ValueError(
ValueError: Expected minimum length of 3, got 1
>>> alice.score = -1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/projects/miniattrs/miniattrs.py", line 131, in __set__
    self.validate(value)
  File "/projects/miniattrs/miniattrs.py", line 136, in validate
    validator(value)
  File "/projects/miniattrs/miniattrs.py", line 262, in validator
    raise ValueError(f"Expected minimum value of {min_value}, got {value}")
ValueError: Expected minimum value of 0, got -1
```

Define custom validators. These are functions that accept a value and
raise either a `ValueError` or `TypeError` when it is invalid.

```Python
>>> def validate_even(value):
...   if value % 2 != 0:
...     raise ValueError(f"Expected even number, got {value}")
... 
>>> @define
... class EvenNumber:
...   value: int = field(validators=(validate_even,))
... 
>>> n = EvenNumber(value=4)
>>> 
>>> m = EvenNumber(value=13)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<string>", line 3, in __init__
  File "/projects/miniattrs/miniattrs.py", line 131, in __set__
    self.validate(value)
  File "/projects/miniattrs/miniattrs.py", line 136, in validate
    validator(value)
  File "<stdin>", line 3, in validate_even
ValueError: Expected even number, got 13
```

Mutable defaults are deep-copied.


```Python
>>> @define
... class ShoppingList:
...   items: list = [1, 2, 3]
... 
>>> a, b = ShoppingList(), ShoppingList()
>>> a.items == b.items
True
>>> a.items is b.items
False
>>> a.items.append(4)
>>> a.items, b.items
([1, 2, 3, 4], [1, 2, 3])
```

Type validation uses `isinstance`, so it works with any object
that passes `isinstance` checks.

```Python

>>> from pathlib import Path
>>> from decimal import Decimal
>>> from fractions import Fraction
>>> 
>>> @define
... class Config:
...   path: Path
...   amount: Decimal
...   ratio: Fraction
... 

>>> Config(path=Path('/etc/app.conf'), amount=Decimal('1.5'), ratio=Fraction(1, 3))
Config(path=PosixPath('/etc/app.conf'), amount=Decimal('1.5'), ratio=Fraction(1, 3))
>>> class Color:
...   def __init__(self, rgb):
...     self.rgb = rgb
... 
>>> @define
... class Pixel:
...   color: Color
... 
>>> p = Pixel(color=Color((255, 0, 0)))
>>> p.color.rgb
(255, 0, 0)
```
## How it works

Each annotated attribute becomes a descriptor that validates the
attribute whenever it is set on an instance.

## Installation

Simply drop [miniattrs.py](miniattrs.py) into your project wherever
convenient and import `define` to start defining your classes.

## License

Public Domain
