import typing
import weakref
import collections.abc
import functools
import copy

from . import _helpers
from . import _manage


__all__ = (
    'Tool', 'theme', 'Unit', 'update', 
    'Object', 'keyify', 
    'List', 'Dict', 'add', 'pop', 
    'collect', 'Collection',
    'strip'
)


_DataV = typing.TypeVar('_DataV')


_RootV = typing.TypeVar('_RootV')


_PathV = list[_RootV]


class Tool(typing.NamedTuple):

    """
    Tool(...)

    Holds utilities for handling incoming data.
    """

    identify: typing.Callable[[_PathV, _DataV], collections.abc.Hashable]
    """
    Used for determining the incoming data's unique key for cacheing.
    """
    create  : typing.Callable[[_PathV, _DataV], _RootV]
    """
    Used for converting the incoming data to the "root" form kept in cache.
    """
    update  : typing.Callable[[_PathV, _RootV, _DataV], _RootV]
    """
    Used for updating existing "root"s found in cache with incoming data.
    """


class Info(typing.NamedTuple):

    """
    Info(...)

    Holds utilities for handling incoming data and enabling cacheing.
    """

    tool              : Tool
    cache_unit_to_root: dict['Unit', _RootV]
    cache_name_to_unit: dict[collections.abc.Hashable, 'Unit']


_Unit_infos: dict['Unit', Info] = {}


def _analyze(unit, cls = None, /):

    if cls is None:
        cls = unit.__class__

    info = _Unit_infos[cls]
    root = info.cache_unit_to_root[unit]

    return info, root


def _Unit_expose(name):

    def method(self, *args, **kwargs):
        info, root = _analyze(self)
        return getattr(root, name)(*args, **kwargs)
    
    method.__name__ = name

    return method


class UnitType(type):

    def __new__(cls, name, bases, space, tool = None, expose = ()):
        
        space = dict(space)

        space.setdefault('__slots__', ())

        for attr_name in expose:
            space[attr_name] = _Unit_expose(attr_name)

        self = super().__new__(cls, name, bases, space)

        if not tool is None:
            cache_unit_to_root = weakref.WeakKeyDictionary()
            cache_name_to_unit = weakref.WeakValueDictionary()
            _Unit_infos[self] = Info(tool, cache_unit_to_root, cache_name_to_unit)

        return self
    

_Unit_path: _PathV = []


_theme = _helpers.Theme()


theme = _theme


class Unit(typing.Generic[_DataV], metaclass = UnitType):

    """
    For subclassing only.

    .. code-block:: python

        class User(vessel.Unit, tool = ...):
            ...

        user = User(data)
    """

    __slots__ = ('__weakref__',)

    @_theme.add
    def __new__(cls, data: _DataV, /, *, unique = False):

        path = _Unit_path

        info = _Unit_infos[cls]
        tool = info.tool

        if not unique and not (identify := tool.identify) is None:
            name = identify(path, data)
            try:
                self = info.cache_name_to_unit[name]
            except KeyError:
                forge = match = True
            else:
                forge = match = False
        else:
            forge, match = True, False

        creatable = not (create := tool.create) is None # always True
        updatable = not (update := tool.update) is None
        
        if forge or not updatable:
            root = create(path, data)
            self = super().__new__(cls)
        else:
            root = info.cache_unit_to_root[self]
            root = update(path, root, data)
        
        info.cache_unit_to_root[self] = root

        if match:
            info.cache_name_to_unit[name] = self

        return self
    
    def __copy_any__(self, func):

        cls = self.__class__

        info, root = _analyze(self, cls)

        root = func(root)
        self = super().__new__(cls)

        info.cache_unit_to_root[self] = root

        return self
    
    def __copy__(self):

        func = lambda root: copy.copy(root)

        return self.__copy_any__(func)
    
    def __deepcopy__(self, memo):

        func = lambda root: copy.deepcopy(root, memo)

        return self.__copy_any__(func)
    

def _update(path, unit, data, **kwargs):

    cls = unit.__class__

    if not isinstance(unit, Unit):
        raise ValueError(f'cannot update {cls} with {data}')
    
    info, root = _analyze(unit)

    info.tool.update(path, root, data, **kwargs)

    return unit
    

def update(unit, data, **kwargs):

    """
    Update the unit's root with new data.
    
    :param unit:
        The reference to the root data.
    :param data:
        The new data to update the root with.
    """

    return _update(_Unit_path, unit, data, **kwargs)


_FieldData = typing.TypeVar('_FieldData')


_FieldRoot = typing.TypeVar('_FieldRoot')


class SetField(typing.NamedTuple):

    """
    SetField(...)
    
    Holds information for handling incoming data specific to a key.
    """

    create: typing.Callable[[_PathV, _FieldData], _FieldRoot]
    """
    Used to initially create data.
    """
    update: typing.Callable[[_PathV, _FieldRoot, _FieldData], _FieldRoot] = _update
    """
    Used to update existing data.
    """
    unique: bool = False
    """
    Whether it can be used to compose a ``keyify``.
    """


_FieldValue = typing.TypeVar('_FieldValue')


class GetField(typing.NamedTuple):

    """
    GetField(...)

    Holds information for fetching data specific to an attribute.
    """

    select: typing.Callable[[_RootV], _FieldValue]
    """
    Used to fetch data from the internal root.
    """


class ObjectMeta(typing.NamedTuple): # metadata

    set_fields: dict[str, SetField]
    get_fields: dict[str, GetField]
    keyify    : typing.Callable[[_RootV], collections.abc.Hashable]


_Object_metas: dict['Object', ObjectMeta] = {}


def _analyze_object(unit, cls = None, /):

    if cls is None:
        cls = unit.__class__

    info, root = _analyze(unit, cls)

    meta = _Object_metas[cls]

    return info, root, meta


class ObjectType(UnitType):

    @classmethod
    def _get_fields(cls, space):
        
        fields = {}
        for field_name, field in space.items():
            if not isinstance(field, GetField):
                continue
            fields[field_name] = field

        return fields

    def __new__(cls, 
                name, bases, space, 
                fields  : dict[str, SetField]                                               = None, 
                identify: typing.Callable[[list[_PathV], _DataV], collections.abc.Hashable] = None,
                keyify  : typing.Callable[[_RootV], collections.abc.Hashable]               = None):

        space = dict(space)

        if not (set_fields := fields) is None:
            get_fields = cls._get_fields(space)
            create = functools.partial(_manage.create_object, set_fields)
            update = functools.partial(_manage.update_object, set_fields)
            tool = Tool(identify, create, update)
        else:
            tool = None

        self = super().__new__(cls, name, bases, space, tool = tool)

        if not tool is None:
            _Object_metas[self] = ObjectMeta(set_fields, get_fields, keyify)

        return self
    

def _Object_select(root, field):

    try:
        value = field.select(root)
    except KeyError:
        value = _manage.missing

    return value


class Object(Unit[_DataV], metaclass = ObjectType):

    """
    For subclassing only.
    
    .. code-block:: python

        fields = {
            'id': vessel.SetField(
                create = lambda path, data: str(data),
                unique = True
            ),
            'name': vessel.SetField(
                create = lambda path, data: str(data)
            )
        }

        def identify(path, data):
            return str(data['id'])

        class User(vessel.Unit, fields = fields, identify = identify):
            id: str = vessel.GetField(
                select = lambda root: root['id']
            )
            name: str = vessel.GetField(
                select = lambda root: root['name']
            )

        data0 = {'id': 0, 'name': 'Zero'}
        user0 = User(data0) # <User(id=0, name='Zero')>

        data1 = {'id': 0, 'name': 'One'}
        user1 = User(data1) # <User(id=0, name='One')>

        user0 is user1 # True (identify matches)
    """

    def __getattribute__(self, name):

        if name.startswith('__'):
            return object.__getattribute__(self, name)

        cls = self.__class__

        meta = _Object_metas[cls]

        try:
            field = meta.get_fields[name]
        except KeyError as error:
            raise AttributeError(*error.args)

        info = _Unit_infos[cls]

        root = info.cache_unit_to_root[self]

        value = _Object_select(root, field)
        
        return value
    
    def __repr__(self):

        cls = self.__class__

        info, root, meta = _analyze_object(self, cls)

        pairs = []
        for name, field in meta.get_fields.items():
            value = _Object_select(root, field)
            if value is _manage.missing:
                continue
            pairs.append(f'{name}={repr(value)}')
        
        description = ', '.join(pairs)

        return f'<{cls.__name__}({description})>'


def _Object_keyify_naive(fields, path, data):

    values = []
    for name, field in fields.items():
        if not field.unique:
            continue
        new_value = data[name]
        cur_value = field.create(path, new_value)
        values.append(cur_value)

    # like operator.itemgetter
    return tuple(values) if len(values) > 1 else values[0]


@functools.cache
def _get_Object_keyify(cls):

    meta = _Object_metas[cls]

    if not (keyify := meta.keyify) is None:
        return keyify

    fields = meta.set_fields

    if not any (field.unique for field in fields.values()):
        return None

    return functools.partial(_Object_keyify_naive, fields)


def keyify(cls: Object, 
           data: _DataV):

    """
    Get the collection key of the incoming data for an Object class.

    :param cls:
        The class to use the keyify function of. 
    :param data:
        The data to use the keyify function on.
    """

    keyify = _get_Object_keyify(cls)

    return keyify(_Unit_path, data)


class ListType(UnitType):

    def __new__(cls, 
                name, bases, space, 
                create: typing.Callable[[_PathV, _DataV], _RootV] = None):
        
        space = dict(space)

        if not create is None:
            manage_args = (create,)
            create = functools.partial(_manage.create_list, *manage_args)
            update = functools.partial(_manage.update_list, *manage_args)
            tool = Tool(None, create, update)
        else:
            tool = None

        expose = ('__contains__', '__getitem__', '__iter__', '__len__', '__repr__', 'count', 'index')

        self = super().__new__(cls, name, bases, space, tool = tool, expose = expose)

        return self


class List(Unit[_DataV], metaclass = ListType):

    """
    For subclassing only.
    
    .. code-block:: py

        def create(path, data):
            return User(data)

        class UserStore(List, create = create):
            pass
            
        data = [{'id': 2, 'name': 'Two'}, {'id': 3, 'name': 'Three'}]

        users = UserStore(data) # [<User(id=2, name='Two')>, <User(id=2, name='Three')>]
    """


class DictType(UnitType):

    def __new__(cls, 
                name, bases, space, 
                create: typing.Callable[[_PathV, _DataV], _RootV]                         = None,
                update: typing.Callable[[_PathV, _DataV], _RootV]                         = _update,
                keyify: typing.Callable[[list[_PathV], _DataV], collections.abc.Hashable] = None):
        
        space = dict(space)

        if not create is None:
            manage_args = (keyify, create, update)
            create = functools.partial(_manage.create_dict, *manage_args)
            update = functools.partial(_manage.update_dict, *manage_args)
            tool = Tool(None, create, update)
        else:
            tool = None

        expose = ('__contains__', '__getitem__', '__iter__', '__len__', '__repr__', 'get', 'items', 'keys', 'values')

        self = super().__new__(cls, name, bases, space, tool = tool, expose = expose)

        return self


class Dict(Unit[_DataV], metaclass = DictType):

    """
    For subclassing only.
    
    .. code-block:: py

        def create(path, data):
            return User(data)
        
        def keyify(path, data):
            reutrn str(data['id\])

        class UserStore(Dict, create = create, keyify = keyify):
            pass
            
        data = [{'id': 4, 'name': 'Four'}, {'id': 5, 'name': 'Five'}]

        users = UserStore(data) # {'4': <User(id=2, name='Two')>, '5': <User(id=2, name='Three')>}
    """

    def __iter__(self):

        info, root = _analyze(self)

        yield from root.values()

    def __contains__(self, value):

        return any(value is other for other in self)


def _add(unit, data):

    cls = unit.__class__

    if issubclass(cls, List):
        function = _manage.add_list
    elif issubclass(cls, Dict):
        function = _manage.add_dict
    else:
        raise ValueError(f'cannot add to {cls}')

    info, root = _analyze(unit, cls)

    args = info.tool.create.args

    return function(*args, _Unit_path, root, data) 


def add(unit, data) -> Unit:

    """
    Create, add and return using the data.
    """

    return _add(unit, data)


def _pop(unit, key) -> Unit:

    cls = unit.__class__

    if issubclass(cls, List):
        function = _manage.pop_list
    elif issubclass(cls, Dict):
        function = _manage.pop_dict
    else:
        raise ValueError(f'cannot add to {cls}')

    info, root = _analyze(unit, cls)

    return function(root, key)


def pop(unit, key):

    """
    Remove and return using the key.
    """

    return _pop(unit, key)
    

def _get_Collection_keyify(cls):

    if not (isinstance(cls, type) and issubclass(cls, Object)):
        return None
    
    return _get_Object_keyify(cls)
    

@functools.cache
def _get_Collection(name, keyify, cls):

    space = {}

    def create(path, data):
        return cls(data)

    kwargs = {'create': create}

    if keyify is None:
        keyify = _get_Collection_keyify(cls)

    if keyify is None:
        Base = List
    else:
        Base = Dict
        kwargs['keyify'] = keyify

    if callable(name):
        name = name(Base)

    return type(name, (Base,), space, **kwargs)
    

def _collect(name, keyify, cls, data):

    Collection = _get_Collection(name, keyify, cls)

    return Collection(data)


_ObjectV = typing.TypeVar('_ObjectV')


def collect(cls   : _ObjectV, 
            data  : _DataV, *, 
            keyify: typing.Callable[[list[_PathV], _DataV], collections.abc.Hashable] = None, 
            name  : typing.Callable[[List | Dict], str]                               = lambda cls: f'{cls.__name__}Store') -> collections.abc.Sequence[_ObjectV] | collections.abc.Mapping[collections.abc.Hashable, _ObjectV]:
    
    """
    Creates a collection of :class:`Object`\s based on whether keyification has been provided 
    (either by setting :paramref:`.SetField.unique` to :code:`True` or using :paramref:`.keyify`).

    :param cls:
        Used to create the :code:`create` function.
    :param data:
        Used for filling the collection with instances of :paramref:`.cls`.
    :param keyify:
        Determines whether to use :class:`List` or :class:`Dict` as the collection base.
    :param name:
        Used for fetching the name of the new collection.

    .. note::
        Using this with the same (:paramref:`.cls`, :paramref:`.keyify`, :paramref:`.name`) will re-use existing collection classes.
    """
    
    return _collect(name, keyify, cls, data)


class Collection(collections.abc.Collection[_ObjectV]):

    """
    Same as :func:`.collect`, except can also be used as a typehint.
    """

    def __new__(cls, Object: _ObjectV, *args, **kwargs) -> collections.abc.Sequence[_ObjectV] | collections.abc.Mapping[collections.abc.Hashable, _ObjectV]:

        return collect(Object, *args, **kwargs)
    
    def __getitem__(self, key) -> _ObjectV:

        pass


def _strip(data):

    if isinstance(data, Unit):
        info, root = _analyze(data)
        root = copy.copy(root)
        if isinstance(data, List):
            root = tuple(root)
        if isinstance(data, Dict):
            root = tuple(root.values())
        return _strip(root)
    
    if isinstance(data, (list, tuple, set, frozenset)):
        return [_strip(data) for data in data]
    
    if isinstance(data, dict):
        return {name: _strip(data) for name, data in data.items()}
    
    return data


def strip(unit: Unit):

    """
    Get the fully nested raw underlying data.
    """

    return _strip(unit)