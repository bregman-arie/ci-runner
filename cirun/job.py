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
import requests


class Job(object):

    def __init__(self, data, system_url):
        self.data = data
        self.system_url = system_url
        self.parents_data = {}
        self.pre_runs = []
        self.runs = []
        self.post_runs = []
        self.vars = {}
        self.parents_data = self.get_job_data(self.data['parent'],
                                              self.parents_data)
        self.run()

    def get_job_data(self, job, parents_data):
        job_url = self.system_url + '/api/job/{}'.format(job)
        job_data = requests.get(job_url)
        parents_data[job] = job_data.json()[0]
        if 'parent' in parents_data[job] and parents_data[job]['parent']:
            parents_data = self.get_job_data(parents_data[job]['parent'],
                                             parents_data)
        self.pre_runs.append(job_data.json()[0]['pre_run'])
        self.runs.append(job_data.json()[0]['run'])
        self.post_runs.append(job_data.json()[0]['post_run'])

    def run(self):
        for playbook in self.pre_runs:
            print(playbook)
