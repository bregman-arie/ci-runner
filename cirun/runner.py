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
from fabric import Connection
import logging
import os
import patchwork.transfers
import subprocess

from cirun.job import Job
from cirun.node import Node
from cirun.context import suppress_output


LOG = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, tenant=None, job_name=None, url=None,
                 project_path=None, host=None, start_playbook=0,
                 **kwargs):
        self.tenant = tenant
        self.job_name = job_name
        self.url = url
        self.project_path = project_path
        self.project_name = project_path.split('/')[-1]
        self.node = Node(address=host)
        self.start_playbook = start_playbook
        self.root_dir = os.path.join(os.path.expanduser('~'), '.cirun')
        self.workspace = self.create_workspace()

    def copy_project_to_host(self):
        if self.node.address != "localhost" and \
           self.node.address != "127.0.0.1":
            conn = Connection(self.node.address)
            dest_path = os.path.dirname(self.project_path)
            LOG.info("copying project {} to {}:{}".format(
                crayons.yellow(self.project_path),
                crayons.yellow(self.node.address),
                crayons.yellow(dest_path)))
            with suppress_output():
                patchwork.transfers.rsync(conn, self.project_path,
                                          dest_path)
                conn.run("chmod +x {}".format(self.project_path))
        else:
            cp_command = "cp -r {0} {0}".format(self.project_path)
            subprocess.run(cp_command, shell=True)

    def create_job(self):
        LOG.info("gathering job info...")
        self.job = Job(name=self.job_name, tenant=self.tenant,
                       start_playbook=self.start_playbook,
                       project_path=self.project_path,
                       workspace=self.workspace)
        self.job.populate_data(url=self.url, tenant=self.tenant)
        self.job.set_playbooks()

    def create_workspace(self):
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        project_job_dir = os.path.join(self.root_dir, "{}_{}".format(
            self.job_name, self.project_name))
        if not os.path.isdir(project_job_dir):
            os.makedirs(project_job_dir)
            LOG.info("created dir: {}".format(crayons.yellow(
                project_job_dir)))
        else:
            LOG.info("using workspace: {}".format(
                crayons.green(project_job_dir)))
        return project_job_dir

    def prepare(self):
        # A Zuul job can't be executed without the project being on the host
        self.create_job()
        if not self.node.address:
            self.node.provision(project=self.project_path)
        else:
            self.copy_project_to_host()

    def run(self):
        LOG.info("{}: {}".format("running the job",
                                 crayons.yellow(self.job_name)))
        self.job.run(node=self.node, project_path=self.project_path,
                     root_dir=self.root_dir)
