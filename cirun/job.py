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
import requests
import subprocess

from cirun.ansible import AnsibleExecutor

LOG = logging.getLogger(__name__)


class Job(object):

    def __init__(self, data, system_url, name, project_name):
        self.data = data
        self.system_url = system_url
        self.project_name = project_name
        self.name = name
        self.parents_data = {}
        self.pre_runs = []
        self.runs = []
        self.post_runs = []
        self.vars = {}
        self.parents_data = self.get_job_data(self.data['parent'],
                                              self.parents_data)
        self.ansible_executor = AnsibleExecutor()
        self.workspace = self.create_workspace()

    def create_workspace(self):
        root_dir = os.path.join(os.path.expanduser('~'), '.cirun')
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir)
        project_job_dir = os.path.join(root_dir, "{}_{}".format(
            self.name, self.project_name))
        if not os.path.isdir(project_job_dir):
            os.makedirs(project_job_dir)
            LOG.info("created dir: {}".format(crayons.yellow(
                project_job_dir)))
        else:
            LOG.info("using workspace: {}".format(
                crayons.green(project_job_dir)))
        return project_job_dir

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

    def clone_to_workspace(self, remote_project):
        if "http" not in remote_project:
            remote_project = "https://" + remote_project
        clone_cmd = ['git', 'clone', remote_project]
        LOG.info("cloning project {} to {}".format(
            crayons.cyan(remote_project), crayons.cyan(self.workspace)))
        subprocess.run(clone_cmd, stdout=subprocess.DEVNULL,
                       cwd=self.workspace)

    def get_project_to_clone(self, data):
        project = data['source_context']['project']
        for role in data['roles']:
            if project in role['project_canonical_name']:
                return role['project_canonical_name']

    def sync_project(self, project):
        sync_cmd = ['git', 'pull']
        LOG.info("syncing project: {}".format(crayons.yellow(project)))
        subprocess.run(sync_cmd, stdout=subprocess.DEVNULL,
                       cwd=self.workspace)

    def run(self):
        LOG.info("======= Running Pre Playbooks ========")
        for pre_run in self.pre_runs:
            project_to_clone = self.get_project_to_clone(pre_run[0])
            project_local_path = os.path.join(
                self.workspace, project_to_clone.rsplit('/')[-1])
            if not os.path.isdir(os.path.join(project_local_path)):
                self.clone_to_workspace(project_to_clone)
            else:
                self.sync_project(project_local_path)
            self.ansible_executor.execute(playbook=os.path.join(
                project_local_path, pre_run[0]['path']))
