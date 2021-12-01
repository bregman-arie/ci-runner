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


class Node(object):

    dockerfiles_dir = os.path.dirname(__file__) + '/dockerfiles'

    def __init__(self, address, node_type="server"):
        self.address = address
        self.type = node_type

    def provision(self, project, address="rhel_8", node_type="container"):
        self.type = node_type
        self.address = address
        # TODO(abregman): move this block of code to its own function or class
        if node_type == "container":
            LOG.info("building_image...")
            self.build_image(dockerfile_name=address)
            LOG.info("running container...")
            self.run_container(address, project)

    def stop_and_remove_container(self, name):
        cmd = "podman container stop {}".format(name)
        subprocess.run(cmd, shell=True)
        cmd = "podman container rm {}".format(name)
        subprocess.run(cmd, shell=True)

    def run_container(self, name, project):
        self.stop_and_remove_container(name)
        cmd = "podman run --name {0} -v {1}:{1}:z -d {0} sleep infinity\
".format(name, project)
        res = subprocess.run(cmd, shell=True)
        if res.returncode != 0:
            LOG.error(res.stdout)
            sys.exit(2)
        return res

    def build_image(self, dockerfile_name):
        """Builds image given df path."""
        cmd = "podman build -f {} -t {} .".format(
            os.path.join(self.dockerfiles_dir, dockerfile_name),
            dockerfile_name)
        LOG.info("running: {}".format(cmd))
        res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
        if res.returncode != 0:
            LOG.error(res.stdout)
            sys.exit(2)
        return res
