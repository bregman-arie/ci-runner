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
import patchwork.transfers
import subprocess

from cirun.job import Job
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
        self.host = host
        self.start_playbook = start_playbook

    def validate_input(self):
        pass

    def copy_project_to_host(self):
        if self.host != "localhost" and self.host != "127.0.0.1":
            conn = Connection(self.host)
            with suppress_output():
                patchwork.transfers.rsync(conn, self.project_path,
                                          self.project_path)
                conn.run("chmod +x {}".format(self.project_path))
        else:
            cp_command = "cp -r {0} {0}".format(self.project_path)
            subprocess.run(cp_command, shell=True)

    def run(self):
        LOG.info("gathering job info...")
        self.job = Job(data=Job.get_job_data(
            job_name=self.job_name, url=self.url, tenant=self.tenant),
                       system_url=self.url,
                       name=self.job_name,
                       tenant=self.tenant,
                       start_playbook=self.start_playbook,
                       project_path=self.project_path,
                       host=self.host)

        LOG.info("copying project {} to {}".format(
            crayons.yellow(self.project_path),
            crayons.yellow(self.host)))
        self.copy_project_to_host()

        LOG.info("{}: {}".format("running the job",
                                 crayons.yellow(self.job_name)))
        self.job.run()
