# Copyright (c) 2023 Henix, Henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Selectors helpers"""

from typing import Any, Dict, List, Mapping, Optional, Tuple

import re

########################################################################
## Constants

Object = Dict[str, Any]

NAME_PATTERN = r'^[0-9a-zA-Z]+([0-9A-Za-z-_.]*[0-9a-zA-Z])?$'
LABEL_PATTERN = r'^([^/]+/)?([0-9A-Za-z-_.]{1,63})$'
DNS_LABEL_PATTERN = r'^(?![0-9]+$)(?!-)[a-z0-9-]{1,63}(?<!-)$'

KEY = r'[a-z0-9A-Z-_./]+'
VALUE = r'[a-z0-9A-Z-_./@]+'
EQUAL_EXPR = rf'^({KEY})\s*([=!]?=)\s*({VALUE})(?:,|$)'
SET_EXPR = rf'^({KEY})\s+(in|notin)\s+\(({VALUE}(\s*,\s*{VALUE})*)\)(?:,|$)'
EXISTS_EXPR = rf'^{KEY}(?:,|$)'
NEXISTS_EXPR = rf'^!{KEY}(?:,|$)'


########################################################################
## Selectors helpers


def _split_exprs(exprs: str) -> List[str]:
    """Split a comma-separated list of expressions.

    # Required parameters

    - exprs: a string

    # Returned value

    A (possibly empty) list of _expressions_.  An expression is a
    string, stripped.
    """
    result = []
    while exprs:
        match = re.match(SET_EXPR, exprs)
        if not match:
            match = re.match(EQUAL_EXPR, exprs)
        if not match:
            match = re.match(EXISTS_EXPR, exprs)
        if not match:
            match = re.match(NEXISTS_EXPR, exprs)
        if not match:
            raise ValueError(f'Invalid expression {exprs}')
        result.append(exprs[: match.end()].strip(', '))
        exprs = exprs[match.end() :].strip(', ')

    return result


def _resolve_path(path: str, obj: Object) -> Tuple[bool, Optional[str]]:
    def inner(items, obj) -> Tuple[bool, Optional[str]]:
        head, rest = items[0], items[1:]
        if head in obj:
            return (True, obj[head]) if not rest else inner(rest, obj[head])
        return False, None

    return inner(path.split('.'), obj)


def _evaluate_fields(req: str, obj: Object) -> bool:
    if req == '':
        return True
    if re.match(EXISTS_EXPR, req):
        return _resolve_path(req, obj)[0]
    if re.match(NEXISTS_EXPR, req):
        return not _resolve_path(req[1:], obj)[0]
    expr = re.match(SET_EXPR, req)
    if expr:
        key, ope, list_, _ = expr.groups()
        found, value = _resolve_path(key, obj)
        if found:
            values = [v.strip() for v in list_.split(',')]
            if ope == 'in':
                return value in values
            return value not in values
        return ope == 'notin'
    expr = re.match(EQUAL_EXPR, req)
    if expr is None:
        raise ValueError(f'Invalid expression {req}.')
    key, ope, expected = expr.groups()
    found, value = _resolve_path(key, obj)
    if found:
        if ope in ('=', '=='):
            return value == expected
        return value != expected
    return ope == '!='


def _evaluate(req: str, labels: Mapping[str, str]) -> bool:
    """Evaluate whether req matches labels.

    # Required parameters

    - req: a string
    - labels: a dictionary

    # Returned value

    A boolean.  True if `req` is satisfied by `labels`, False otherwise.

    # Raised exceptions

    A _ValueError_ exception is raised if `req` is not a valid
    expression.
    """
    if req == '':
        return True
    if re.match(EXISTS_EXPR, req):
        return req in labels
    if re.match(NEXISTS_EXPR, req):
        return req[1:] not in labels
    expr = re.match(SET_EXPR, req)
    if expr:
        key, ope, list_, _ = expr.groups()
        if key in labels:
            values = [v.strip() for v in list_.split(',')]
            if ope == 'in':
                return labels[key] in values
            return labels[key] not in values
        return ope == 'notin'
    expr = re.match(EQUAL_EXPR, req)
    if expr is None:
        raise ValueError(f'Invalid expression {req}.')
    key, ope, value = expr.groups()
    if key in labels:
        if ope in ('=', '=='):
            return labels[key] == value
        return labels[key] != value
    return ope == '!='


def match_field_selector(obj: Object, selector: str) -> bool:
    """Return True if the object matches the selector."""
    return all(_evaluate_fields(sel, obj) for sel in _split_exprs(selector))


def match_label_selector(obj: Object, selector: str) -> bool:
    """Return True if the service matches the selector.

    An empty selector always matches.

    The complete selector feature has been implemented.  `selector` is
    of form:

        expr[,expr]*

    where `expr` is one of `key`, `!key`, or `key op value`, with
    `op` being one of `=`, `==`, or `!=`.  The
    `key in (value[, value...])` and `key notin (value[, value...])`
    set-based requirements are also implemented.

    # Required parameters

    - obj: a Definition (a dictionary)
    - selector: a string

    # Returned value

    A boolean.
    """
    metadata = obj.get('metadata', {}).get('labels', {})
    return all(_evaluate(sel, metadata) for sel in _split_exprs(selector))
