# adotsdot (Almost Surely)

## Purpose

Provide the ability to obtain the differences between two JSON serializable Python dictionaries (e.g., configuration files) while treating lists as unordered.*

\* Supporting this functionality requires that the dictionaries in a list of dictionaries have a a field that can be used as a unique marker across all elements in the list.

## Usage
Assuming `prev_state` and `curr_state` are JSON serializable Python dictionaries,

```
from adotsdot import diff

node = diff(prev_state, curr_state)
```
will generate the root of a tree of nodes that represent the changes in state.

This information can be displayed in the terminal via the `str` procedure or transformed into a JSON serializable Python dictionary via `node.as_dict()`.
