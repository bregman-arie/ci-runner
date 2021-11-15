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
import requests

from cirun.job import Job


LOG = logging.getLogger(__name__)


class Runner(object):

    def __init__(self, tenant=None, job_name=None, url=None,
                 project_name=None, host=None, **kwargs):
        self.tenant = tenant
        self.job_name = job_name
        self.url = url
        self.project_name = project_name
        self.host = host

    def validate_input(self):
        pass

    def run(self):
        LOG.info("Gathering job info...")
        self.job = Job(data=Job.get_job_data(
            job_name=self.job_name, url=self.url, tenant=self.tenant),
                       system_url=self.url,
                       name=self.job_name,
                       tenant=self.tenant,
                       project_name=self.project_name,
                       host=self.host)

        LOG.info("{}: {}".format("running the job",
                                 crayons.yellow(self.job_name)))
        self.job.run()
