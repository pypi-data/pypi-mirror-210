

__all__ = (
    'Missing', 'missing', 
    'add_list', 'pop_list', 'update_list', 'create_list',
    'add_dict', 'pop_dict', 'update_dict', 'create_dict',
    'update_object', 'create_object'
)


class Missing:

    __slots__ = ()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'
    
    def __bool__(self):
        return False
    
    def __iter__(self):
        return iter(())
    
    def __getitem__(self, name):
        raise KeyError(name)
    
    def __len__(self):
        return 0
    
    def __getattr__(self, name):
        return _missing

    def __delattr__(self, name):
        pass
    
    def __eq__(self, other):
        return False
    
    def __ne__(self, other):
        return True
    
    def __hash__(self):
        return id(self)


_missing = Missing()


missing = _missing
"""
Returned when no data exists at the specified location.
"""


def _add_list_naive(create, path, root, new_sub):

    if new_sub is None:
        return _missing

    cur_sub = create(path, new_sub)

    root.append(cur_sub)

    if cur_sub is _missing:
        return _missing

    return cur_sub


def _add_list(create, path, root, new_sub):

    path.append(root)

    result = _add_list_naive(create, path, root, new_sub)

    del path[-1]

    return result


def add_list(create, path, root, new_sub):

    cur_sub = _add_list(create, path, root, new_sub)

    return cur_sub


def _pop_list(root, index):

    if root is _missing:
        raise IndexError(index)

    cur_sub = root.pop(index)

    return cur_sub 


def pop_list(root, index):

    cur_sub = _pop_list(root, index)

    return cur_sub


def _update_list(clean, create, path, root, data):

    if clean:
        root.clear()

    for new_sub in data:
        _add_list(create, path, root, new_sub)

    return root


def update_list(create, path, root, data, clean = True):

    return _update_list(clean, create, path, root, data)


def _create_list(create, path, data):

    root = []

    return _update_list(False, create, path, root, data)


def create_list(create, path, data):

    return _create_list(create, path, data)


def _add_dict_naive(keyify, create, update, path, root, new_sub):

    if new_sub is None:
        return _missing

    name = keyify(path, new_sub)

    if name is _missing:
        return _missing, _missing
    
    try:
        cur_sub = root[name]
    except KeyError:
        forge = True
    else:
        try:
            cur_sub = update(path, cur_sub, new_sub)
        except ValueError:
            forge = True
        else:
            forge = False

    if forge:
        cur_sub = create(path, new_sub)

    if cur_sub is _missing:
        return name, _missing

    root[name] = cur_sub

    return name, cur_sub


def _add_dict(keyify, create, update, path, root, new_sub):

    path.append(root)

    result = _add_dict_naive(keyify, create, update, path, root, new_sub)

    del path[-1]

    return result


def add_dict(keyify, create, update, path, root, new_sub):

    name, cur_sub = _add_dict(keyify, create, update, path, root, new_sub)

    return cur_sub


def _pop_dict(root, name):

    if root is _missing:
        raise KeyError(name)

    cur_sub = root.pop(name)

    return cur_sub


def pop_dict(root, name):

    cur_sub = _pop_dict(root, name)

    return cur_sub


def _update_dict(clean, keyify, create, update, path, root, data):

    seen = set()

    for new_sub in data:
        name, cur_sub = _add_dict(keyify, create, update, path, root, new_sub)
        if cur_sub is _missing:
            continue
        seen.add(name)

    if clean:
        for name in set(root) - seen:
            del root[name]
    
    return root


def update_dict(keyify, create, update, path, root, data, clean = False):

    return _update_dict(clean, keyify, create, update, path, root, data)


def _create_dict(keyify, create, update, path, data):

    root = {}

    return _update_dict(False, keyify, create, update, path, root, data)


def create_dict(keyify, create, update, path, data):

    return _create_dict(keyify, create, update, path, data)


def _update_object(fields, path, root, data):

    def analyze(item):
        name, new_sub = item
        field = fields[name]
        return name, new_sub, field
    
    def keyify(path, item):
        try:
            name, new_sub, field = analyze(item)
        except KeyError:
            return _missing
        return name
    
    def create(path, item):
        try:
            name, new_sub, field = analyze(item)
        except KeyError:
            return _missing
        if new_sub is None:
            return _missing
        return field.create(path, new_sub)
    
    def update(path, cur_sub, item):
        try:
            name, new_sub, field = analyze(item)
        except KeyError:
            return _missing
        if new_sub is None:
            return _missing
        return field.update(path, cur_sub, new_sub)
    
    data = data.items()

    return _update_dict(False, keyify, create, update, path, root, data)


def update_object(fields, path, root, data):

    return _update_object(fields, path, root, data)


def _create_object(fields, path, data):

    root = {}

    return _update_object(fields, path, root, data)


def create_object(fields, path, data):

    return _create_object(fields, path, data)

