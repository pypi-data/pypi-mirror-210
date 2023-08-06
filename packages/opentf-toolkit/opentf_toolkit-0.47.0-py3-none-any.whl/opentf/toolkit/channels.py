# Copyright (c) 2021 Henix, Henix.fr
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

"""Toolkit helpers for channels plugins."""


from typing import Any, Dict, Tuple, Union

from shlex import quote

import base64
import ntpath
import os
import re

from opentf.commons import EXECUTIONRESULT, make_event, make_uuid
from opentf.toolkit import core

## workflow commands

SETOUTPUT_COMMAND = r'^::set-output\s+name=([a-zA-Z_][a-zA-Z0-9_-]*)::(.*)$'
ATTACH_COMMAND = r'^::attach(\s+.*?)?::(.*?)\s*$'
DEBUG_COMMAND = r'^::debug::(.*)$'
WARNING_COMMAND = r'^::warning(\s+(.*)+)?::(.*)$'
ERROR_COMMAND = r'^::error(\s+(.*)+)?::(.*)$'
STOPCOMMANDS_COMMAND = r'^::stop-commands::(\w+)$'
ADDMASK_COMMAND = r'^::add-mask::(.*)$'
PUT_FILE_COMMAND = r'^::put file=(.*?)\s*::(.*?)\s*$'


## step sequence IDs

CHANNEL_REQUEST = -1
CHANNEL_RELEASE = -2
CHANNEL_NOTIFY = -3

DEFAULT_CHANNEL_LEASE = 60  # how long to keep the offer, in seconds

## shells

# For cmd:
#
# - /D: ignore registry autorun commands
# - /E:ON: enable command extensions
# - /V:OFF: disable delayed environment expansion
# - /S: strip " quote characters from command
# - /C: run command then terminate
#
# For bash:
#
# - --noprofile: ignore /etc/profile & al.
# - --norc: ignore /etc/bash.bashrc & al.
# - -e: exit at first error
# - -o pipefail: exit if one of the commands in the pipe fails

SHELL_DEFAULT = {'linux': 'bash', 'macos': 'bash', 'windows': 'cmd'}
SHELL_TEMPLATE = {
    'bash': 'bash --noprofile --norc -eo pipefail {0}',
    'cmd': '%ComSpec% /D /E:ON /V:OFF /S /C "CALL {0}"',
    'python': 'python {0}',
    'powershell': '''powershell -command ". './{0}'"''',
    'pwsh': '''pwsh -command ". './{0}'"''',
}

SCRIPTPATH_DEFAULT = {'linux': '/tmp', 'macos': '/tmp', 'windows': '%TEMP%'}
SCRIPTFILE_DEFAULT = {
    'linux': '{root}/{job_id}_{step_sequence_id}.sh',
    'macos': '{root}/{job_id}_{step_sequence_id}.sh',
    'windows': '{root}\\{job_id}_{step_sequence_id}.cmd',
}

LINESEP = {'linux': '\n', 'macos': '\n', 'windows': '\r\n'}
RUNNER_OS = {'windows', 'macos', 'linux'}

OPENTF_WORKSPACE_TEMPLATE = {
    'linux': '`pwd`/{job_id}',
    'macos': '`pwd`/{job_id}',
    'windows': '%CD%\\{job_id}',
}
OPENTF_VARIABLES_TEMPLATE = {
    'linux': '{root}/{job_id}_dynamic_env.sh',
    'macos': '{root}/{job_id}_dynamic_env.sh',
    'windows': '{root}\\{job_id}_dynamic_env.cmd',
}

## os helpers


def make_variable_linux(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for linux runners."""

    def pseudoquote(val):
        if '"' in val:
            val = val.replace('"', '\\"')
        if ' ' in val or '\t' in val:
            val = f'"{val}"'
        return val

    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            value = quote(value)
        else:
            value = pseudoquote(value)
    else:
        value = pseudoquote(variable)
    return f'export {name}={value}'


def make_variable_windows(name: str, variable: Union[str, Dict[str, Any]]) -> str:
    """Prepare variable declaration for windows runners."""
    if isinstance(variable, dict):
        value = variable['value']
        if variable.get('verbatim'):
            for symbol in '^&<>\\':
                value = value.replace(symbol, f'^{symbol}')
            value = value.replace('%', '%%')
    else:
        value = variable
    return f'@set "{name}={value}"'


def add_default_variables(script, job_id, runner_os, root):
    """Prepare default variables."""
    script.append(
        VARIABLE_MAKER[runner_os](
            'OPENTF_WORKSPACE',
            OPENTF_WORKSPACE_TEMPLATE[runner_os].format(job_id=job_id),
        )
    )
    script.append(
        VARIABLE_MAKER[runner_os](
            'OPENTF_VARIABLES',
            OPENTF_VARIABLES_TEMPLATE[runner_os].format(job_id=job_id, root=root),
        )
    )
    script.append(VARIABLE_MAKER[runner_os]('OPENTF_ACTOR', 'dummy'))
    script.append(VARIABLE_MAKER[runner_os]('CI', 'true'))


## masks helpers


class JobState:
    def __init__(self) -> None:
        self.stop_command = None
        self.masks = []


def mask(line: str, state) -> str:
    """Remove masked values."""
    for masked in state.masks:
        line = line.replace(masked, '***')
    return line


def process_output(event, resp, stdout, stderr, jobstate, _get, _put):
    """Process output, filling structures.

    # Required parameters

    - event: an ExecutionCommand event
    - resp: an integer
    - stdout: a list of strings
    - stderr: a list of strings
    - jobstate: a JobState object
    - attach: a function copying a remote file to a local path
    - put: a function copying a local file to a remote environment

    # Returned value

    An ExecutionResult event.

    # Functions arguments

    ## get

    - destination_url: a string
    - remote_path: a string (file location on execution environment)

    May raise exceptions.

    ## put

    - remote_path: a string (file location on execution environment)
    - source_url: a string

    May raise exceptions.
    """

    def _attach(remote, args):
        if is_windows:
            remote = ntpath.normpath(remote)
        try:
            attachment_url = (
                f'/tmp/{job_id}_{step_sequence_id}_{remote.split(separator)[-1]}'
            )
            attachments_metadata[attachment_url] = {'uuid': make_uuid()}
            if args:
                for parameter in args.strip().split(','):
                    if '=' not in parameter:
                        del attachments_metadata[attachment_url]
                        logs.append(
                            f'ERROR,Invalid workflow command parameter: {parameter}.'
                        )
                        return 2
                    key, _, value = parameter.strip().partition('=')
                    attachments_metadata[attachment_url][key] = value
            attachments.append(attachment_url)
            _get(remote, attachment_url)
            return resp
        except Exception as err:
            logs.append(f'ERROR,Could not read {remote}: {err}.')
            return 2

    def _putfile(remote_path, data):
        working_directory = core.join_path(
            job_id, event.get('working-directory'), is_windows
        )
        targeted_remote_path = core.join_path(
            working_directory, remote_path, is_windows
        )
        try:
            file_ = '/tmp/in_{uuid}_{name}'.format(
                uuid=metadata['workflow_id'], name=data
            )
            if not os.path.exists(file_):
                logs.append(f'ERROR,Invalid resources.files reference {data}.')
                return 2
            _put(targeted_remote_path, file_)
            return resp
        except Exception as err:
            logs.append(
                f'ERROR,Could not send file {data} to remote path {remote_path}: {err}.'
            )
            return 2

    metadata = event['metadata']
    job_id = metadata['job_id']
    step_sequence_id = metadata['step_sequence_id']
    is_windows = metadata['channel_os'] == 'windows'
    separator = '\\' if is_windows else '/'
    outputs = {}
    logs = []
    attachments = []
    attachments_metadata = {}

    if step_sequence_id == CHANNEL_RELEASE:
        resp = 0  # windows returns 1 as we remove the running script

    for line in stdout:
        # Parsing stdout for workflow commands
        if jobstate.stop_command:
            if line == jobstate.stop_command:
                jobstate.stop_command = None
            continue

        if wcmd := re.match(ATTACH_COMMAND, line):
            resp = _attach(wcmd.group(2), wcmd.group(1))
        elif wcmd := re.match(PUT_FILE_COMMAND, line):
            resp = _putfile(wcmd.group(2), wcmd.group(1))
        elif wcmd := re.match(SETOUTPUT_COMMAND, line):
            outputs[wcmd.group(1)] = wcmd.group(2)
        elif wcmd := re.match(DEBUG_COMMAND, line):
            logs.append(f'DEBUG,{mask(wcmd.group(1), jobstate)}')
        elif wcmd := re.match(WARNING_COMMAND, line):
            logs.append(f'WARNING,{mask(wcmd.group(3), jobstate)}')
        elif wcmd := re.match(ERROR_COMMAND, line):
            logs.append(f'ERROR,{mask(wcmd.group(3), jobstate)}')
        elif wcmd := re.match(STOPCOMMANDS_COMMAND, line):
            jobstate.stop_command = f'::{wcmd.group(1)}::'
        elif wcmd := re.match(ADDMASK_COMMAND, line):
            jobstate.masks.append(wcmd.group(1))
        else:
            logs.append(mask(line, jobstate).rstrip())

    for line in stderr:
        logs.append(mask(line, jobstate).rstrip())

    result = make_event(EXECUTIONRESULT, metadata=metadata, status=resp)
    if outputs:
        result['outputs'] = outputs
    if logs:
        result['logs'] = logs
    if attachments:
        result['attachments'] = attachments
        result['metadata']['attachments'] = attachments_metadata

    return result


def make_script(command, script_path, runner_os: str) -> Tuple[str, str, str]:
    """Prepare script.

    # Required parameters

    - command: an ExecutionCommand event
    - script_path: a string or None, where to put script on runner
    - runner_os: a string

    # Returned value

    script_path, script_content, script_command.
    """
    job_id = command['metadata']['job_id']
    step_sequence_id = command['metadata']['step_sequence_id']
    root = script_path or SCRIPTPATH_DEFAULT[runner_os]
    script_path = SCRIPTFILE_DEFAULT[runner_os].format(
        root=root, job_id=job_id, step_sequence_id=step_sequence_id
    )
    script_command = SHELL_TEMPLATE[SHELL_DEFAULT[runner_os]].format(f'"{script_path}"')

    script = []
    if runner_os == 'windows':
        script.append('@echo off')
        prefix = '@'
    else:
        script.append('#!/usr/bin/env bash')
        prefix = ''

    add_default_variables(script, job_id, runner_os, root)
    for name, value in command.get('variables', {}).items():
        script.append(VARIABLE_MAKER[runner_os](name, value))

    if step_sequence_id == 0:
        script.append(f'{prefix}mkdir {job_id}')
        if runner_os != 'windows':
            script.append('touch "$OPENTF_VARIABLES"')
        else:
            script.append('@type nul >>"%OPENTF_VARIABLES%"')

    if step_sequence_id == CHANNEL_RELEASE:
        script.append(
            f'rm -rf {job_id}' if runner_os != 'windows' else f'@rmdir /s/q {job_id}'
        )
        script.append(
            f'rm "{root}/{job_id}"_*.sh'
            if runner_os != 'windows'
            else f'@del /q "{root}\\{job_id}_*.cmd"'
        )
    else:
        script.append(f'{prefix}cd {job_id}')
        if runner_os == 'windows':
            script.append('call "%OPENTF_VARIABLES%"')
        else:
            script.append('. "$OPENTF_VARIABLES"')

    if 'working-directory' in command:
        path = command['working-directory']
        if runner_os == 'windows':
            path = path.replace('/', '\\')
        if ' ' in path:
            path = '"' + path.strip('"') + '"'
        script.append(f'{prefix}cd {path}')

    if (shell := command.get('shell')) in (None, SHELL_DEFAULT[runner_os]):
        script += command['scripts']
    else:
        path = f'{job_id}_shell_script_{step_sequence_id}'
        marker = make_uuid()
        shell_script = command['scripts']
        if shell in ('powershell', 'pwsh'):
            path += '.ps1'
            shell_script = (
                ["$ErrorActionPreference = 'stop'"]
                + shell_script
                + [
                    'if ((Test-Path -LiteralPath variable:\\LASTEXITCODE)) { exit $LASTEXITCODE }'
                ]
            )
        content = LINESEP[runner_os].join(shell_script)
        if runner_os == 'windows':
            encoded = str(base64.b64encode(bytes(content, 'utf8')), 'utf8')
            what = f'@echo {encoded} > {marker} & @certutil -f -decode {marker} {path} >nul & @del {marker}'
        else:
            what = f'cat << "{marker}" > {path}\n{content}\n{marker}'
        script.append(what)
        if runner_os == 'windows' and shell == 'bash':
            shell_command = (
                '%USERPROFILE%\\AppData\\Local\\Programs\\Git\\bin\\'
                + SHELL_TEMPLATE[shell]
            )
        else:
            shell_command = SHELL_TEMPLATE.get(shell, shell)
        script.append(shell_command.format(path))

    return script_path, LINESEP[runner_os].join(script), script_command


VARIABLE_MAKER = {
    'linux': make_variable_linux,
    'macos': make_variable_linux,
    'windows': make_variable_windows,
}
