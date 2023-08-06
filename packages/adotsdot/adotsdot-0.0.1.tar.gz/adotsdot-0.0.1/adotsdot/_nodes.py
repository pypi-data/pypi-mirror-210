"""Compare JSON serializable data to determine differences."""
from collections import Counter


_SUPPORTED_PRIMITIVES = (int, str)


class DiffNode:
    """General comparison node."""

    def __init__(self, depth):
        self._matches = False
        self._depth = depth

    @property
    def matches(self):
        return self._matches

    def set_match(self):
        """Mark that data compared by the node matches."""
        self._matches = True


class PrimDiffNode(DiffNode):
    """Pure primitive comparison node."""

    def __init__(self, depth):
        super().__init__(depth)
        self._removed = None
        self._added = None

    def set_diff(self, removed, added):
        """Set the differences found."""
        self._removed = removed
        self._added = added

    def __str__(self):
        if self.matches:
            return ''

        tab = ['\t'] * self._depth
        modification = (
            f'{self._removed} {type(self._removed)}'
            f' \u2192 {self._added} {type(self._added)}'
        )
        return ''.join(tab + [modification])

    def as_dict(self):
        if self.matches:
            return {'matches': True}

        return {
            'matches': False,
            'removed': self._removed, 'added': self._added
        }


class PrimListDiffNode(DiffNode):
    """List of primitives comparison node."""

    def __init__(self, depth):
        super().__init__(depth)
        self._removed = Counter()
        self._added = Counter()
        self._type = None

    def set_diff(self, removed, added, type_):
        """Set the differences found."""
        self._removed = removed
        self._added = added
        self._type = type_

    def __str__(self):
        tab = ['\t'] * self._depth
        removals = []
        if self._removed:
            removals = [
                ', '.join(self._removed.elements()),
                f' {self._type} - removed',
            ]
            removals = [''.join(tab + removals)]

        additions = []
        if self._added:
            additions = [
                ', '.join(self._added.elements()),
                f' {self._type} - added',
            ]
            additions = [''.join(tab + additions)]

        return '\n'.join(removals + additions)

    def as_dict(self):
        if self.matches:
            return {'matches': True}

        return {
            'matches': False,
            'removed': list(self._removed.elements()),
            'added': list(self._added.elements()),
        }


class DictDiffNode(DiffNode):
    """Dictionary comparison node."""

    def __init__(self, depth):
        super().__init__(depth)
        self._removed_keys = set()
        self._added_keys = set()
        self._child_diffs = {}

    def has_children(self):
        return bool(self._child_diffs)

    def set_modified_keys(self, removed_keys, added_keys):
        """Set newly inserted and completely removed keys."""
        self._removed_keys = removed_keys
        self._added_keys = added_keys

    def __setitem__(self, key, value):
        """Assign child comparison node to the associated changing key."""
        self._child_diffs[key] = value

    def __str__(self):
        tab = ['\t'] * self._depth
        removals = []
        if self._removed_keys:
            for k in self._removed_keys:
                removals.append(''.join(tab + [f'\'{k}\' - removed']))

            removals = ['\n'.join(removals)]

        additions = []
        if self._added_keys:
            for k in self._added_keys:
                additions.append(''.join(tab + [f'\'{k}\' - added']))

            additions = ['\n'.join(additions)]

        children = []
        if self._child_diffs:
            for k, v in self._child_diffs.items():
                row = ''.join(tab + [f'\'{k}\':\n', str(v)])
                children.append(row)

        return '\n'.join(removals + additions + children)

    def as_dict(self):
        if self.matches:
            return {'matches': True}

        return {
            'matches': False,
            'removed': list(self._removed_keys),
            'added': list(self._added_keys),
            'children': {
                k: n.as_dict()
                for k, n in self._child_diffs.items()
            },
        }


def _diff_dict(prev, curr, schema, depth):
    """Compare two dictionaries for new keys, removed keys, and modified keys."""
    prev_keys = prev.keys()
    curr_keys = curr.keys()
    both = prev_keys & curr_keys
    removed = prev_keys - both
    added = curr_keys - both

    node = DictDiffNode(depth)
    node.set_modified_keys(removed_keys=removed, added_keys=added)
    if not schema or isinstance(schema, str):
        default = schema
        schema = {}
    else:
        default = None

    for k in both:
        child_node = diff(prev[k], curr[k], schema=schema.get(k, default), depth=depth)
        if child_node.matches:
            continue

        node[k] = child_node

    if not removed and not added and not node.has_children():
        node.set_match()

    return node


def _diff_list(primitive, prev, curr, schema, depth):
    """Compare two lists for new elements, removed elements, and modified elements."""
    # NOTE: assume primitives.
    if isinstance(primitive, _SUPPORTED_PRIMITIVES):
        prev_set = Counter(prev)
        curr_set = Counter(curr)
        both = prev_set & curr_set
        removed = prev_set - both
        added = curr_set - both

        node = PrimListDiffNode(depth)
        node.set_diff(removed=removed, added=added, type_=type(primitive))
        if not removed and not added:
            node.set_match()
    else:
        node = DictDiffNode(depth)
        inverted_prev = _invert_list(prev, key=schema)
        inverted_curr = _invert_list(curr, key=schema)
        node = _diff_dict(
            inverted_prev, inverted_curr, schema=schema, depth=depth,
        )

    return node


def _invert_list(l, key):
    """Invert a list on a unique key."""
    try:
        return {e[key]: e for e in l}
    except KeyError:
        raise ValueError("No schema passed to be able to distinguish list of dictionaries")


def _ensure_homogeneity(l):
    """Ensure all types in a non-empty list are equivalent."""
    t = type(l[0])
    for e in l[1:]:
        if type(e) != t:
            raise TypeError("Only homogeneous lists are supported")

    return t


def diff(prev, curr, schema=None, depth=-1):
    if type(prev) != type(curr):
        raise TypeError("Changes in schema not supported")

    depth += 1
    if isinstance(prev, dict):
        node = _diff_dict(prev, curr, schema=schema, depth=depth)
    elif isinstance(prev, list):
        if prev and curr:
            prev_elem_type = _ensure_homogeneity(prev)
            curr_elem_type = _ensure_homogeneity(curr)
            if prev_elem_type != curr_elem_type:
                raise TypeError("Changes in schema not supported")

            node = _diff_list(prev[0], prev, curr, schema=schema, depth=depth)
        elif prev:
            prev_elem_type = _ensure_homogeneity(prev)
            node = _diff_list(prev[0], prev, curr, schema=schema, depth=depth)
            pass
        elif curr:
            curr_elem_type = _ensure_homogeneity(curr)
            node = _diff_list(curr[0], prev, curr, schema=schema, depth=depth)
        else:
            node = PrimListDiffNode(depth)
            node.set_match()
    elif isinstance(prev, _SUPPORTED_PRIMITIVES):
        node = PrimDiffNode(depth)
        if prev != curr:
            node.set_diff(removed=prev, added=curr)
        else:
            node.set_match()
    else:
        raise TypeError('Unsupported type')

    return node
