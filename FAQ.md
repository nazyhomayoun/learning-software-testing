# Frequently Asked Questions

1. **Why use `Decimal` instead of `float`?**

    `Decimal` is a more precise and accurate way to represent numbers. It is more accurate than `float` and is less prone to rounding errors.
    When dealing with money, we want to avoid rounding errors and ensure that the calculations are accurate.
    Here's an example:
    A family of 5 wants to buy tickets for an event. The price of a ticket is $33.33. Therefore, the total price for the family is ($33.33 + 10%) * 5 = $183.315. Let's see how `float` and `Decimal` handle this:
    ```python
    >>> price = 33.33
    >>> quantity = 5
    >>> total = price * 1.10 * quantity
    >>> print(total)
    183.31500000000003

    >>> from decimal import Decimal
    >>> price = Decimal("33.33")
    >>> quantity = 5
    >>> total = price * Decimal("1.10") * quantity
    >>> print(total)
    183.3150
    ```

1. **What is `typing.Protocol` and why use it?**

    Python uses a typing system called _duck typing_. This means that the type of an object is determined by the methods and attributes it implements, rather than the class it belongs to. `typing.Protocol` is a way to define a contract for a class. It is a way to ensure that a class implements a certain interface. When a `Protocol` class is used as the type hint, it implies that _ANY_ type that implements the methods and attributes of the `Protocol` class is valid and the type checker will not raise an error. This is called _static duck typing_. `Protocol` classes are used in the repository layer because they allow us to define the interface and worry about the concrete implementation later. This way, it is very easy to switch implementation of the repository (e.g. from SQLAlchemy to an in-memory implementation) without having to change the code that uses the repository. Here's an example:
    ```python
    >>> from typing import Protocol
    >>> class RepoInterface(Protocol):
    ...     def get_all_records(self) -> list[int]:
    ...         ...
    ...     def get_record_by_id(self, id: int) -> int:
    ...         ...
    ...
    >>> class SQLAlchemyRepo(RepoInterface):
    ...     def __init__(self, persistent_store: SQLAlchemyStore):
    ...         self.persistent_store = persistent_store
    ...     def get_all_records(self) -> list[int]:
    ...         return self.persistent_store.get_all_records()
    ...     def get_record_by_id(self, id: int) -> int:
    ...         return self.persistent_store.get_record_by_id(id)
    ...
    >>> class InMemoryRepo(RepoInterface):
    ...     def __init__(self, in_memory_store: dict[int, int]):
    ...         self.in_memory_store = in_memory_store or {}
    ...     def get_all_records(self) -> list[int]:
    ...         return list(self.in_memory_store.keys())
    ...     def get_record_by_id(self, id: int) -> int:
    ...         return self.in_memory_store.get(id, None)
    ...
    >>> def get_records(repo: RepoInterface) -> list[int]:
    ...     return repo.get_all_records()
    ...
    >>> get_records(SQLAlchemyRepo(persistent_store=SQLAlchemyStore()))
    [1, 2, 3]
    >>> get_records(InMemoryRepo(in_memory_store={1: "record1", 2: "record2", 3: "record3"}))
    [1, 2, 3]
    ```

1. **Why use `BaseSettings` from `pydantic-settings` instead of loading from environment?**

    refer to [this medium article](https://medium.com/@jayanthsarma8/config-management-with-pydantic-base-settings-de22b79fd191).

1. **What is the purpose of `pydantic.SecretStr` as opposed to `str`?**

    [Pydantic documentations](https://docs.pydantic.dev/2.2/usage/types/secrets/) explain it most clearly:
    > You can use the SecretStr and the SecretBytes data types for storing sensitive information that you do not want to be visible in _logging_ or _tracebacks_.
