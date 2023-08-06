#!/bin/bash
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

DEBUG_LEVEL_ARG="${DEBUG_LEVEL:-INFO}"
BUS_HOST_ARG="${BUS_HOST:-127.0.0.1}"
BUS_PORT_ARG="${BUS_PORT:-38368}"
EXTERNAL_HOSTNAME_ARG="${EXTERNAL_HOSTNAME:-127.0.0.1}"
TRUST_FILES_ARG="${TRUST_FILES:-/}"
if [ "$DEBUG_LEVEL_ARG" == "CRITICAL" ]; then DEBUG_LEVEL_ARG="ERROR"; fi;
if [ "$DEBUG_LEVEL_ARG" == "WARNING" ]; then DEBUG_LEVEL_ARG="WARN"; fi;
if [ "$DEBUG_LEVEL_ARG" == "NOTSET" ]; then DEBUG_LEVEL_ARG="TRACE"; fi;
BASE_COMMAND="-Dorg.opentestfactory.insecure=true -Dorg.opentestfactory.auth.trustedAuthorities=$TRUST_FILES_ARG -Dorg.opentestfactory.bus.baseUrl=http://$BUS_HOST_ARG:$BUS_PORT_ARG -Dorg.opentestfactory.tf2.external-hostname=$EXTERNAL_HOSTNAME_ARG -Dlogging.level.org.squashtest.tf2=$DEBUG_LEVEL_ARG -Dlogging.level.web=$DEBUG_LEVEL_ARG -Dlogging.level.org.opentestfactory=$DEBUG_LEVEL_ARG"
if [ -z "$BUS_TOKEN" ]; then OPTIONAL_COMMAND=""; else  OPTIONAL_COMMAND="-Dorg.opentestfactory.bus.authToken=$BUS_TOKEN"; fi;
java $BASE_COMMAND $OPTIONAL_COMMAND $*
