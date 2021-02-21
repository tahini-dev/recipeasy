from __future__ import annotations
from typing import Optional, Union, FrozenSet, Iterable
from dataclasses import dataclass


default_state_name = 'atomic'


@dataclass(frozen=True)
class State:

    name: str

    def __init__(
            self,
            state: Optional[Union[str, State]] = None,
            /,
    ):
        if isinstance(state, State):
            state = state.name

        if state is None:
            state = 'atomic'

        object.__setattr__(self, 'name', state)


@dataclass(frozen=True)
class Element:
    name: str
    state: State

    def __init__(
            self,
            element: Optional[Union[Element, str]] = None,
            /,
            *,
            state: Optional[Union[State, str]] = None,
    ):

        if isinstance(element, Element):
            if state is None:
                state = element.state
            element = element.name

        if element is None:
            raise TypeError(f"First positional input to '{self.__class__.__name__}' cannot be 'None'")

        state = State(state)

        object.__setattr__(self, 'name', element)
        object.__setattr__(self, 'state', state)

    def change(
            self,
            state: Optional[Union[State, str]] = None,
    ) -> Element:

        element = self.__class__(self, state=state)

        return element


@dataclass(frozen=True)
class Food:
    elements: FrozenSet[Element]

    def __init__(
            self,
            elements: Optional[Iterable[Union[Element, str]]] = None,
    ):
        if elements is None:
            elements = []

        elements = frozenset(Element(item) for item in elements)

        object.__setattr__(self, 'elements', elements)

    def change(
            self,
            state: Optional[Union[State, str]] = None,
    ) -> Food:
        food = Food(elements=(element.change(state=state) for element in self.elements))
        return food

    def mix(
            self,
            other: Union[Food, Element],
    ):

        if isinstance(other, Element):
            other = Food(elements=[other])

        food = Food(elements=frozenset().union(*[self.elements, other.elements]))

        return food

    def remove(
            self,
            other: Union[Food, Element],
    ):

        if isinstance(other, Element):
            other = Food(elements=[other])

        elements = self.elements - other.elements

        food = Food(elements=frozenset(elements))

        return food
