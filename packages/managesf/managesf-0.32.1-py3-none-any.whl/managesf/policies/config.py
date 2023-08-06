#
# Copyright (C) 2016 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# -*- coding: utf-8 -*-


from oslo_policy import policy

from managesf.policies import base


BASE_POLICY_NAME = 'managesf.config'
POLICY_ROOT = BASE_POLICY_NAME + ':%s'

rules = [
    policy.RuleDefault(
        name=POLICY_ROOT % 'get',
        check_str=base.RULE_AUTHENTICATED_API),
]


def list_rules():
    return rules
