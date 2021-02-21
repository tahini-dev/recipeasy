import dataclasses

import pytest

import recipeasy.food


@pytest.mark.parametrize('args, kwargs, type_error, message_error', [
    # only allows positional only arguments
    (
        [],
        dict(state='test'),
        TypeError,
        "__init__() got some positional-only arguments passed as keyword arguments: 'state'",
    ),
    (
        [],
        dict(test='test'),
        TypeError,
        "__init__() got an unexpected keyword argument 'test'",
    ),
])
def test_state_init_error(args, kwargs, type_error, message_error):
    with pytest.raises(type_error) as e:
        recipeasy.food.State(*args, **kwargs)
    assert e.value.args[0] == message_error


@pytest.mark.parametrize('args, kwargs, expected', [
    # empty
    ([], dict(), recipeasy.food.default_state_name),
    # args
    (['test_name'], dict(), 'test_name'),
    # idempotent
    ([recipeasy.food.State('test_name')], dict(), 'test_name'),
])
def test_state_init(args, kwargs, expected):
    state = recipeasy.food.State(*args, **kwargs)
    assert state.name == expected


@pytest.mark.parametrize('args, kwargs, type_error, message_error', [
    # only allows positional only arguments
    (
        [],
        dict(element='test'),
        TypeError,
        "__init__() got some positional-only arguments passed as keyword arguments: 'element'",
    ),
    (
        [],
        dict(test='test'),
        TypeError,
        "__init__() got an unexpected keyword argument 'test'",
    ),
    # first positional input cannot be None
    (
        [None],
        dict(),
        TypeError,
        "First positional input to 'Element' cannot be 'None'",
    ),
])
def test_element_init_error(args, kwargs, type_error, message_error):
    with pytest.raises(type_error) as e:
        recipeasy.food.Element(*args, **kwargs)
    assert e.value.args[0] == message_error


@pytest.mark.parametrize('args, kwargs, expected', [
    # empty state
    (['apple'], dict(), dict(name='apple', state=dataclasses.asdict(recipeasy.food.State()))),
    # with state
    (
        ['apple'],
        dict(state='chopped'),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State('chopped'))),
    ),
    (
        ['apple'],
        dict(state=recipeasy.food.State('chopped')),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State('chopped'))),
    ),
    # idempotent
    (
        [recipeasy.food.Element('apple')],
        dict(),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State())),
    ),
    (
        [recipeasy.food.Element('apple')],
        dict(state='chopped'),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State('chopped'))),
    ),
    (
        [recipeasy.food.Element('apple', state='chopped')],
        dict(),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State('chopped'))),
    ),
    # override state
    (
        [recipeasy.food.Element('apple', state='chopped')],
        dict(state='not_chopped'),
        dict(name='apple', state=dataclasses.asdict(recipeasy.food.State('not_chopped'))),
    ),
])
def test_element_init(args, kwargs, expected):
    element = recipeasy.food.Element(*args, **kwargs)
    assert dataclasses.asdict(element) == expected


@pytest.mark.parametrize('element, args, kwargs, expected', [
    # no state
    (recipeasy.food.Element('apple'), [], dict(), recipeasy.food.Element('apple')),
    # state
    (recipeasy.food.Element('apple'), [], dict(state='chopped'), recipeasy.food.Element('apple', state='chopped')),
    (
        recipeasy.food.Element('apple'),
        [],
        dict(state=recipeasy.food.State('chopped')),
        recipeasy.food.Element('apple', state='chopped'),
    ),
])
def test_element_change(element, args, kwargs, expected):
    element_changed = element.change(*args, **kwargs)
    assert element_changed == expected


@pytest.mark.parametrize('args, kwargs, expected', [
    # empty
    ([], dict(), dict(elements=frozenset())),
    # single
    ([['apple']], dict(), dict(elements=frozenset({recipeasy.food.Element('apple')}))),
    ([], dict(elements=['apple']), dict(elements=frozenset({recipeasy.food.Element('apple')}))),
    # multiple
    (
        [],
        dict(elements=['apple', 'banana']),
        dict(elements=frozenset({
            recipeasy.food.Element('apple'),
            recipeasy.food.Element('banana'),
        })),
    ),
    # element
    ([], dict(elements=[recipeasy.food.Element('apple')]), dict(elements=frozenset({recipeasy.food.Element('apple')}))),
    # state
    (
        [],
        dict(elements=[recipeasy.food.Element('apple', state='chopped')]),
        dict(elements=frozenset({recipeasy.food.Element('apple', state='chopped')})),
    ),
])
def test_food_init(args, kwargs, expected):
    food = recipeasy.food.Food(*args, **kwargs)
    assert dataclasses.asdict(food) == expected


@pytest.mark.parametrize('food, args, kwargs, expected', [
    # empty
    (recipeasy.food.Food(), [], dict(), recipeasy.food.Food()),
    (recipeasy.food.Food(), [], dict(state='chopped'), recipeasy.food.Food()),
    # empty state to begin
    (
        recipeasy.food.Food(['apple']),
        [],
        dict(state='chopped'),
        recipeasy.food.Food([recipeasy.food.Element('apple', state='chopped')]),
    ),
    # empty state changed
    (
        recipeasy.food.Food([recipeasy.food.Element('apple', state='chopped')]),
        [],
        dict(state='cooked'),
        recipeasy.food.Food([recipeasy.food.Element('apple', state='cooked')]),
    ),
    # multiple
    (
        recipeasy.food.Food(['apple', 'banana']),
        [],
        dict(state='chopped'),
        recipeasy.food.Food([
            recipeasy.food.Element('apple', state='chopped'),
            recipeasy.food.Element('banana', state='chopped'),
        ]),
    ),
])
def test_food_change(food, args, kwargs, expected):
    food_changed = food.change(*args, **kwargs)
    assert food_changed == expected


@pytest.mark.parametrize('food, args, kwargs, expected', [
    # empty both
    (recipeasy.food.Food(), [], dict(other=recipeasy.food.Food()), recipeasy.food.Food()),
    # empty other food
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Food()), recipeasy.food.Food(['apple'])),
    # empty self
    (recipeasy.food.Food(), [], dict(other=recipeasy.food.Food(['apple'])), recipeasy.food.Food(['apple'])),
    # other food same
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Food(['apple'])), recipeasy.food.Food(['apple'])),
    # other food different
    (
        recipeasy.food.Food(['apple']),
        [],
        dict(other=recipeasy.food.Food(['banana'])),
        recipeasy.food.Food(['apple', 'banana']),
    ),
    # other element same
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Element('apple')), recipeasy.food.Food(['apple'])),
    # other element different
    (
        recipeasy.food.Food(['apple']),
        [],
        dict(other=recipeasy.food.Element('banana')),
        recipeasy.food.Food(['apple', 'banana']),
    ),
])
def test_food_mix(food, args, kwargs, expected):
    food_changed = food.mix(*args, **kwargs)
    assert food_changed == expected


@pytest.mark.parametrize('food, args, kwargs, expected', [
    # empty both
    (recipeasy.food.Food(), [], dict(other=recipeasy.food.Food()), recipeasy.food.Food()),
    # empty other food
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Food()), recipeasy.food.Food(['apple'])),
    # empty self
    (recipeasy.food.Food(), [], dict(other=recipeasy.food.Food(['apple'])), recipeasy.food.Food()),
    # other food same
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Food(['apple'])), recipeasy.food.Food()),
    # other food different
    (
        recipeasy.food.Food(['apple', 'banana']),
        [],
        dict(other=recipeasy.food.Food(['banana'])),
        recipeasy.food.Food(['apple']),
    ),
    (
        recipeasy.food.Food(['apple', 'banana', 'carrot']),
        [],
        dict(other=recipeasy.food.Food(['banana'])),
        recipeasy.food.Food(['apple', 'carrot']),
    ),
    (
        recipeasy.food.Food(['apple', 'banana', 'carrot']),
        [],
        dict(other=recipeasy.food.Food(['banana', 'carrot'])),
        recipeasy.food.Food(['apple']),
    ),
    (
        recipeasy.food.Food(['apple']),
        [],
        dict(other=recipeasy.food.Food(['banana'])),
        recipeasy.food.Food(['apple']),
    ),
    # other element same
    (recipeasy.food.Food(['apple']), [], dict(other=recipeasy.food.Element('apple')), recipeasy.food.Food()),
    # other element different
    (
        recipeasy.food.Food(['apple']),
        [],
        dict(other=recipeasy.food.Element('banana')),
        recipeasy.food.Food(['apple']),
    ),
])
def test_food_remove(food, args, kwargs, expected):
    food_changed = food.remove(*args, **kwargs)
    assert food_changed == expected
