# Copyright 2021 Arie Bregman
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging
import os
import subprocess
import sys


LOG = logging.getLogger(__name__)


class AnsibleExecutor(object):

    def __init__(self, playbook=None):
        self.playbook = playbook

    def execute(self, work_dir=os.getcwd(), playbook=None):
        if playbook:
            self.playbook = playbook
        self.playbook = os.path.join(work_dir, playbook)
        ansible_cmd = ['ansible-playbook', self.playbook]
        print("Running playbook: {}".format(self.playbook))
        res = subprocess.run(ansible_cmd, cwd=work_dir)
        if res.returncode != 0:
            LOG.error("Oh no! something went terribly wrong...good bye! :)")
            sys.exit(2)

    def write_inventory(self, path, host):
        self.inventory_path = os.path.join(path, 'inventory')
        with open(self.inventory_path, 'w+') as f:
            f.write(host)
        LOG.info("wrote inventory: {}".format(self.inventory_path))

    def write_config(self, path, conf_file_name='ansible.cfg', **kwargs):
        # TODO(abregman): consider moving this part to Jinja2
        self.conf_file_path = os.path.join(path, conf_file_name)
        with open(self.conf_file_path, 'w+') as f:
            f.write("[DEFAULT]")
            f.write("DEFAULT_MODULE_PATH={}".format(
                kwargs['default_module_path']))
        LOG.info("wrote ansible config: {}".format(self.conf_file_path))
