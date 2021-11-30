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
import crayons
import logging
import os
import subprocess


LOG = logging.getLogger(__name__)


class Git(object):

    @staticmethod
    def clone_project(remote_project, path):
        if os.path.isdir(path):
            Git.sync_project(path)
        else:
            if "http" not in remote_project:
                remote_project = "ssh://{}@".format(
                    os.environ.get('USERNAME')) + remote_project
            clone_cmd = ['git', 'clone', remote_project]
            LOG.info("cloning project {} to {}".format(
                crayons.cyan(remote_project), crayons.cyan(path)))
            subprocess.run(clone_cmd, stdout=subprocess.DEVNULL,
                           cwd=path)

    @staticmethod
    def sync_project(project):
        sync_cmd = ['git', 'pull']
        # LOG.info("syncing project: {}".format(crayons.yellow(project)))
        subprocess.run(sync_cmd, stdout=subprocess.DEVNULL,
                       cwd=project)
