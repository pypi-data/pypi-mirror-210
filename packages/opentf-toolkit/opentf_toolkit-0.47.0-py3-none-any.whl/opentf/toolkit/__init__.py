# Copyright (c) 2021-2023 Henix, Henix.fr
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

"""A toolkit for creating OpenTestFactory plugins."""

from typing import Any, Callable, Dict, Optional

import inspect
import os
import sys
import time

from collections import defaultdict

from flask import request, g

import yaml

from opentf.commons import (
    make_app,
    run_app,
    subscribe,
    unsubscribe,
    EXECUTIONCOMMAND,
    PROVIDERCOMMAND,
    PROVIDERCONFIG,
    GENERATORCOMMAND,
    SERVICECONFIG,
    CHANNEL_HOOKS,
    validate_schema,
    make_status_response,
)
from opentf.toolkit import core


########################################################################

SUBSCRIPTION_KEY = '__subscription uuid__'
MANIFEST_KEY = '__manifest key__'
KIND_KEY = '__kind key__'
INPUTS_KEY = '__inputs key__'
WATCHEDFILES_KEY = '__watched files__'

WATCHDOG_POLLING_DELAY_SECONDS = 30
WATCHDOG_POLLING_DELAY_KEY = 'watchdog_polling_delay_seconds'

Handler = Callable[[Dict[str, Any]], Any]


########################################################################
# Helpers for provider plugins


def _normalize_inputs(inputs: Dict[str, Any]) -> None:
    """Normalize inputs.

    The 'normalized' form for inputs is with `-` separators, not `_`.

    Non-normalized inputs are removed from the dictionary.

    # Raised exceptions

    A _core.ExecutionError_ is raised if an input is provided twice, in
    a normalized as well as a non-normalized form.
    """
    for key in inputs.copy():
        if '_' in key:
            normalized = key.replace('_', '-')
            if normalized in inputs:
                raise core.ExecutionError(
                    f"Both '{key}' and '{normalized}' specified in inputs."
                )
            inputs[normalized] = inputs.pop(key)


def _ensure_inputs_match(
    plugin, labels: Dict[str, str], inputs: Dict[str, Any]
) -> None:
    """Check inputs.

    Normalize inputs, fills missing optional inputs with their default
    values if specified.

    # Raised exceptions

    A _core.ExecutionError_ is raised if a required entry is missing,
    or if an unexpected entry is found.
    """
    cache = plugin.config['CONTEXT'][INPUTS_KEY]
    prefix = labels.get('opentestfactory.org/categoryPrefix')
    category = labels.get('opentestfactory.org/category')
    version = labels.get('opentestfactory.org/categoryVersion') or None

    for keys in (
        (prefix, category, version),
        (None, category, version),
        (prefix, category, None),
        (None, category, None),
        (prefix, None, None),
    ):
        if (entry := cache.get(keys)) is not None:
            break
    else:
        return

    declaration, additional_inputs = entry
    for key in declaration:
        if key.startswith('{'):
            break
    else:
        _normalize_inputs(inputs)
    for key, definition in declaration.items():
        if key not in inputs:
            if definition.get('required'):
                raise core.ExecutionError(f"Mandatory input '{key}' not provided.")
            if (default := definition.get('default')) is not None:
                inputs[key] = default

    if additional_inputs:
        return

    for key in inputs:
        if key not in declaration and key.replace('_', '-') not in declaration:
            allowed = ', '.join(sorted([f"'{k}'" for k in declaration.keys()]))
            raise core.ExecutionError(
                f"Unexpected input '{key}' found in function step.  Allowed inputs: {allowed}."
            )


def _get_target(
    labels: Dict[str, str], providers: Dict[str, Handler]
) -> Optional[Handler]:
    """Find target for labels.

    Finds the most specific provider.  Returns None if no provider
    matches.

    `prefix/category[@vn]` is more specific than `category[@vn]`.

    `category@vn` is more specific than `category`.

    `category[@vn]` is more specific than `prefix`.
    """
    prefix = labels['opentestfactory.org/categoryPrefix']
    category = labels['opentestfactory.org/category']
    version = labels.get('opentestfactory.org/categoryVersion')

    for template in (f'{prefix}/{category}', category):
        if version:
            parts = version.split('.')
            while parts:
                function = f'{template}@{".".join(parts)}'
                if function in providers:
                    return providers[function]
                parts.pop()
        if template in providers:
            return providers[template]

    return None


INVALID_HOOKS_DEFINITION_TEMPLATE = {
    'name': 'invalid-external-hooks-definition',
    'events': [],
    'before': [
        {
            'run': 'echo ::error::Invalid hooks definition.  Hooks defined by {name}_{type}_HOOKS are disabled.  Please contact your orchestrator administrator for more info.',
            'if': "runner.os == 'windows'",
        },
        {
            'run': 'echo "::error::Invalid hooks definition.  Hooks defined by {name}_{type}_HOOKS are disabled.  Please contact your orchestrator administrator for more info."',
            'if': "runner.os != 'windows'",
        },
    ],
}


def _fill_invalid_hooks_template(name: str, type: str) -> None:
    befores = INVALID_HOOKS_DEFINITION_TEMPLATE['before']
    events = INVALID_HOOKS_DEFINITION_TEMPLATE['events']
    befores[0]['run'] = (
        befores[0]['run']
        .replace('{name}', name.upper())
        .replace('{type}', type.upper())
    )
    befores[1]['run'] = (
        befores[1]['run']
        .replace('{name}', name.upper())
        .replace('{type}', type.upper())
    )
    if type == 'PROVIDER':
        events.append({'category': '_'})
    elif type == 'CHANNEL':
        events.append({'channel': 'setup'})


def _read_hooks_definition(
    plugin, hooksfile: str, schema: str, invalid: Dict[str, Any]
) -> None:
    """Read hooks definition file.

    Try to read hooks definition file and set or replace existing hooks
    with those of `hooksfile`.

    # Required parameters

    - plugin: a Flask object
    - hooksfile: a string, the hooks definition file
    - schema: a string, the schema name
    - invalid: a dictionary, a hook definition
    """
    config = plugin.config['CONFIG']
    try:
        with open(hooksfile, 'r', encoding='utf-8') as src:
            hooks = yaml.safe_load(src)
        if not isinstance(hooks, dict) or not 'hooks' in hooks:
            plugin.logger.error(
                "Hooks definition file '%s' needs a 'hooks' entry, ignoring.", hooksfile
            )
            config['hooks'] = [invalid]
            return

        if config.get('hooks'):
            plugin.logger.info("Replacing hooks definition using '%s'.", hooksfile)
        else:
            plugin.logger.info("Reading hooks definition from '%s'.", hooksfile)

        config['hooks'] = hooks['hooks']
        valid, extra = validate_schema(schema, config)
        if valid:
            return

        plugin.logger.error(
            "Error while verifying '%s' hooks definition: %s.", hooksfile, extra
        )
    except Exception as err:
        plugin.logger.error(
            "Error while reading '%s' hooks definition: %s.", hooksfile, err
        )

    config['hooks'] = [invalid]


########################################################################
# Dispatchers


def _dispatch_providercommand(plugin, handler: Handler, body: Dict[str, Any]) -> None:
    """Provider plugin dispatcher.

    `handler` is expected to return either a list of steps or raise a
    _core.ExecutionError_ exception.
    """
    try:
        plugin.logger.debug('Calling provider function %s.', handler.__name__)
        inputs: Dict[str, Any] = body['step'].get('with', {})
        _ensure_inputs_match(plugin, body['metadata'].get('labels', {}), inputs)
        core.publish_providerresult(handler(inputs))
    except core.ExecutionError as err:
        core.publish_error(str(err))
    except Exception as err:
        core.publish_error(f'Unexpected execution error: {err}.')


def _dispatch_executioncommand(_, handler: Handler, body: Dict[str, Any]):
    """Channel plugin dispatcher."""
    try:
        return handler(body)
    except Exception as err:
        msg = f'Unexpected execution error: {err}.'
        core.publish_error(msg)
        return make_status_response('InternalError', msg)


########################################################################
#  Watchdog


def _run_handlers(plugin, file, handlers):
    """Run file handlers."""
    for handler, args, kwargs in handlers:
        try:
            handler(plugin, file, *args, **kwargs)
        except Exception as err:
            plugin.logger.error(
                "Handler '%s' for file '%s' failed: %s.  Ignoring.", handler, file, err
            )


def _watchdog(plugin, polling_delay):
    """Watch changes and call handlers when appropriate."""
    files_stat = defaultdict(float)
    files_handlers = plugin.config[WATCHEDFILES_KEY]
    while True:
        for file in list(files_handlers):
            try:
                current_modified_time = os.stat(file).st_mtime
            except OSError as err:
                plugin.logger.debug("Could not stat file '%s': %s.", file, err)
                current_modified_time = 0
            if current_modified_time == files_stat[file]:
                continue
            plugin.logger.debug("Watched file '%s' has changed.", file)
            files_stat[file] = current_modified_time
            _run_handlers(plugin, file, list(files_handlers[file]))

        time.sleep(polling_delay)


def _start_watchdog(plugin) -> None:
    """Set up a watchdog that monitors specified files for changes."""
    import threading

    try:
        polling_delay = max(
            WATCHDOG_POLLING_DELAY_SECONDS,
            int(plugin.config['CONTEXT'].get(WATCHDOG_POLLING_DELAY_KEY, 0)),
        )
    except ValueError as err:
        plugin.logger.error(
            'Configuration parameter %s not an integer: %s.',
            WATCHDOG_POLLING_DELAY_KEY,
            str(err),
        )
        sys.exit(2)

    plugin.logger.info('Watchdog configuration:')
    plugin.logger.info(
        '  polling delay in seconds (%s): %d', WATCHDOG_POLLING_DELAY_KEY, polling_delay
    )
    plugin.logger.debug('Starting configuration watchdog thread.')
    threading.Thread(
        target=_watchdog, args=(plugin, polling_delay), daemon=True
    ).start()


def watch_file(plugin, path: str, handler, *args, **kwargs) -> None:
    """Watch file changes.

    There can be more than one handler watching a given file.  A handler
    is a function taking at least two parameters: a `plugin` object and
    a file path (a string).  It may take additional parameters.  It will
    be called whenever the file changes.

    # Required parameters

    - plugin: a Flask application
    - path: a string, the file path
    - handler: a function

    # Optional parameters

    - *args: an array
    - **kwargs: a dictionary

    The provided extra parameters, if any, are passed to the handler
    whenever it is called.
    """
    need_init = plugin.config.get(WATCHEDFILES_KEY) is None
    if need_init:
        plugin.config[WATCHEDFILES_KEY] = defaultdict(list)
    plugin.logger.debug("Adding configuration watcher for '%s'.", path)
    plugin.config[WATCHEDFILES_KEY][path].append((handler, args, kwargs))
    if need_init:
        _start_watchdog(plugin)


def _subscribe(
    plugin, cat_prefix: str, cat: str, cat_version: str, manifest: Dict[str, Any]
) -> str:
    """Subscribe for the relevant event."""
    context = plugin.config['CONTEXT']
    kind = context[KIND_KEY]
    labels = {}
    if cat is not None:
        labels['opentestfactory.org/category'] = cat
    if cat_prefix is not None:
        labels['opentestfactory.org/categoryPrefix'] = cat_prefix
    if cat_version is not None:
        labels['opentestfactory.org/categoryVersion'] = cat_version
    context[INPUTS_KEY][(cat_prefix, cat, cat_version)] = (
        manifest.get('inputs', {}),
        manifest.get('additionalInputs'),
    )
    return subscribe(kind=kind, target='inbox', app=plugin, labels=labels)


def run_plugin(plugin):
    """Start and run plugin.

    Subscribe to the relevant events before startup and tries to
    unsbuscribe in case of errors.

    Spurious subscriptions may remain in case of brutal termination.
    """
    try:
        context = plugin.config['CONTEXT']
        context[SUBSCRIPTION_KEY] = []
        context[INPUTS_KEY] = {}
        if context[KIND_KEY] == PROVIDERCOMMAND:
            for manifest in context[MANIFEST_KEY]:
                if 'action' not in manifest.get('metadata', {}):
                    continue
                for event in manifest.get('events', []):
                    cat_prefix = event.get('categoryPrefix')
                    cat = event.get('category')
                    if cat or cat_prefix:
                        cat_version = event.get('categoryVersion')
                        context[SUBSCRIPTION_KEY].append(
                            _subscribe(plugin, cat_prefix, cat, cat_version, manifest)
                        )
                    else:
                        plugin.logger.warning(
                            "At least one of 'category', 'categoryPrefix' required, ignoring."
                        )
        elif context[KIND_KEY] == EXECUTIONCOMMAND:
            context[SUBSCRIPTION_KEY].append(
                subscribe(kind=EXECUTIONCOMMAND, target='inbox', app=plugin)
            )
        run_app(plugin)
    finally:
        for subscription_id in plugin.config['CONTEXT'][SUBSCRIPTION_KEY]:
            unsubscribe(subscription_id, app=plugin)


def make_plugin(
    name,
    description: str,
    channel: Optional[Handler] = None,
    generator: Optional[Handler] = None,
    provider: Optional[Handler] = None,
    providers: Optional[Dict[str, Handler]] = None,
    publisher: Optional[Handler] = None,
    manifest=None,
    schema=None,
    configfile=None,
):
    """Create and return a new plugin service.

    One and only one of `channel`, `generator`, `provider`, `providers`,
    or `publisher` must be specified.

    If no `manifest` is specified, there must be `plugin.yaml` file in
    the same directory as the caller source file.  If none is found the
    execution stops.

    - Create default config
    - Subscribe to eventbus
    - Add publication handler
    - Create service (not started)

    # Required parameters

    - name: a string
    - description: a string
    - `channel`, `generator` or `provider`: a function
    - providers: a dictionary

    # Optional parameters

    - manifest: a dictionary or a list of dictionaries or None (None by
      default)
    - schema: a string or None (None by default)
    - configfile: a string or None (None by default)

    # Raised exceptions

    A _ValueError_ exception is raised if the provided parameters are
    invalid.

    # Returned value

    A plugin service (not started).
    """

    def process_inbox():
        try:
            body = request.get_json() or {}
        except Exception as err:
            return make_status_response('BadRequest', f'Could not parse body: {err}.')

        valid, extra = validate_schema(kind, body)
        if not valid:
            return make_status_response(
                'BadRequest', f'Not a valid {kind} request: {extra}.'
            )

        if workflow_id := body.get('metadata', {}).get('workflow_id'):
            g.workflow_id = workflow_id

        if providers:
            labels = body['metadata']['labels']

            if target := _get_target(labels=labels, providers=providers):
                _dispatch_providercommand(plugin, target, body)
            else:
                plugin.logger.warning(f'Labels {labels} not handled by {name}.')
        elif provider:
            _dispatch_providercommand(plugin, provider, body)
        elif channel:
            return _dispatch_executioncommand(plugin, channel, body)
        else:
            return make_status_response('BadRequest', 'Not implemented yet.')

        return make_status_response('OK', '')

    if len([_ for _ in (channel, generator, provider, providers, publisher) if _]) != 1:
        raise ValueError(
            "One and only one of 'channel', 'generator', 'provider', 'providers', or 'publisher' is required."
        )
    if not (manifest is None or isinstance(manifest, (dict, list))):
        raise ValueError(
            "'manifest', if specified, must be a dictionary or a list of dictionaries."
        )

    kind = (
        EXECUTIONCOMMAND
        if channel
        else GENERATORCOMMAND
        if generator
        else PROVIDERCOMMAND
    )
    if not schema:
        schema = SERVICECONFIG if generator else PROVIDERCONFIG
    configfile = configfile or f'conf/{name}.yaml'
    plugin = make_app(name, description, configfile=configfile, schema=schema)
    plugin.route('/inbox', methods=['POST'])(process_inbox)

    if manifest is None:
        manifestfile = 'plugin.yaml'
        try:
            manifestfile = os.path.join(
                os.path.dirname(inspect.stack()[1].filename), manifestfile
            )
            with open(manifestfile, 'r', encoding='utf-8') as definition:
                manifest = list(yaml.safe_load_all(definition))
        except Exception as err:
            plugin.logger.error(
                "Oops, could not get '%s' manifest, aborting: %s.", manifestfile, err
            )
            sys.exit(2)

    if kind == PROVIDERCOMMAND and os.environ.get(f'{name.upper()}_PROVIDER_HOOKS'):
        _fill_invalid_hooks_template(name, 'PROVIDER')
        watch_file(
            plugin,
            os.environ[f'{name.upper()}_PROVIDER_HOOKS'],
            _read_hooks_definition,
            schema,
            INVALID_HOOKS_DEFINITION_TEMPLATE,
        )

    elif kind == EXECUTIONCOMMAND and os.environ.get(f'{name.upper()}_CHANNEL_HOOKS'):
        _fill_invalid_hooks_template(name, 'CHANNEL')
        watch_file(
            plugin,
            os.environ[f'{name.upper()}_CHANNEL_HOOKS'],
            _read_hooks_definition,
            CHANNEL_HOOKS,
            INVALID_HOOKS_DEFINITION_TEMPLATE,
        )

    plugin.config['CONTEXT'][MANIFEST_KEY] = manifest
    plugin.config['CONTEXT'][KIND_KEY] = kind

    core.register_defaultplugin(plugin)

    return plugin
