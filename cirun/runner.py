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

    def __init__(self, tenant=None, job_name=None, url=None, **kwargs):
        self.tenant = tenant
        self.job_name = job_name
        self.url = url

    def validate_input(self):
        pass

    def get_job_data(self):
        job_url = self.url + '/api/job/{}'.format(self.job_name)
        job_data = requests.get(job_url)
        return job_data.json()[0]
        

    def run(self):
        LOG.info("Gathering job info...")
        self.job = Job(data = self.get_job_data(), system_url=self.url)

        LOG.info("{}: {}".format("running the job",
                                crayons.yellow(self.job)))
