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

requests.packages.urllib3.disable_warnings()
LOG = logging.getLogger(__name__)


class Job(object):

    def __init__(self, data, system_url, name, project_name, host, tenant=None,
                 start_playbook=0):
        self.data = data
        self.system_url = system_url
        self.project_name = project_name
        self.name = name
        self.host = host
        self.root_dir = os.path.join(os.path.expanduser('~'), '.cirun')
        self.start_playbook = start_playbook
        self.parents_data = {}
        self.pre_runs = []
        self.runs = []
        self.post_runs = []
        self.vars = {}
        self.tenant = tenant
        self.parents_data = self.get_parents_jobs_data(
            self.data['parent'], self.parents_data)
        self.playbooks = self.get_playbooks_by_order()
        self.ansible_executor = AnsibleExecutor()
        self.workspace = self.create_workspace()

    def get_playbooks_by_order(self):
        playbooks = []
        for playbook in self.pre_runs:
            if playbook:
                playbooks.append(playbook[0])
        for playbook in self.runs:
            if playbook:
                playbooks.append(playbook[0])
        for playbook in self.post_runs[::-1]:
            if playbook:
                playbooks.append(playbook[0])
        return playbooks

    def create_workspace(self):
        if not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir)
        project_job_dir = os.path.join(self.root_dir, "{}_{}".format(
            self.name, self.project_name))
        if not os.path.isdir(project_job_dir):
            os.makedirs(project_job_dir)
            LOG.info("created dir: {}".format(crayons.yellow(
                project_job_dir)))
        else:
            LOG.info("using workspace: {}".format(
                crayons.green(project_job_dir)))
        return project_job_dir

    @staticmethod
    def get_job_data(url, job_name, tenant=None):
        job_url = url + '/api'
        if tenant:
            job_url = job_url + '/tenant/{}'.format(tenant)
        job_url = job_url + '/job/{}'.format(job_name)
        # TODO(abregman): Enable SSL after fixing SF ssl verification
        job_data = requests.get(job_url, verify=False)
        return job_data.json()[0]

    def get_parents_jobs_data(self, job, parents_data):
        parents_data[job] = Job.get_job_data(job_name=job, url=self.system_url,
                                             tenant=self.tenant)
        if 'parent' in parents_data[job] and parents_data[job]['parent']:
            parents_data = self.get_parents_jobs_data(
                parents_data[job]['parent'], parents_data)
        self.pre_runs.append(parents_data[job]['pre_run'])
        self.runs.append(parents_data[job]['run'])
        self.post_runs.append(parents_data[job]['post_run'])
        return parents_data

    def clone_project(self, remote_project, path):
        if "http" not in remote_project:
            remote_project = "ssh://{}@".format(
                os.environ.get('USERNAME')) + remote_project
        clone_cmd = ['git', 'clone', remote_project]
        LOG.info("cloning project {} to {}".format(
            crayons.cyan(remote_project), crayons.cyan(path)))
        subprocess.run(clone_cmd, stdout=subprocess.DEVNULL,
                       cwd=path)

    def get_project_to_clone(self, data):
        project = data['source_context']['project']
        for role in data['roles']:
            if project in role['project_canonical_name']:
                return role['project_canonical_name']

    def sync_project(self, project):
        sync_cmd = ['git', 'pull']
        # LOG.info("syncing project: {}".format(crayons.yellow(project)))
        subprocess.run(sync_cmd, stdout=subprocess.DEVNULL,
                       cwd=project)

    def clone_zuul(self):
        zuul_dir_path = os.path.join(self.root_dir, 'zuul')
        if os.path.isdir(zuul_dir_path):
            self.sync_project(zuul_dir_path)
        else:
            self.clone_project(
                remote_project='https://opendev.org/zuul/zuul.git',
                path=self.root_dir)
        return zuul_dir_path

    def get_roles_paths(self, job_data):
        roles_paths = ""
        for role in job_data['roles']:
            project_path = os.path.join(self.workspace, role['target_name'])
            if os.path.isdir(project_path):
                self.sync_project(project_path)
            else:
                # TODO(abregman): some zuul instances has the key
                #                 named differently :|
                if 'canonical_project_name' in role:
                    self.clone_project(role['canonical_project_name'],
                                       path=self.workspace)
                else:
                    self.clone_project(role['project_canonical_name'],
                                       path=self.workspace)
            roles_paths = project_path + "/roles" + ":" + roles_paths
        return roles_paths

    def print_playbooks_order(self):
        for i, playbook in enumerate(self.playbooks):
            LOG.info("{}: {}".format(i, playbook['path']))

    def run(self):
        self.zuul_dir_path = self.clone_zuul()
        self.print_playbooks_order()
        LOG.info("======= Running Playbooks ========")
        for playbook in self.playbooks[self.start_playbook:]:
            roles_paths = self.get_roles_paths(playbook)
            LOG.info("roles paths: {}".format(roles_paths))
            project_to_clone = self.get_project_to_clone(playbook)
            project_local_path = os.path.join(
                self.workspace, project_to_clone.rsplit('/')[-1])
            if not os.path.isdir(os.path.join(project_local_path)):
                self.clone_project(remote_project=project_to_clone,
                                   path=self.workspace)
            else:
                self.sync_project(project_local_path)
            self.ansible_executor.write_inventory(
                path=project_local_path, host=self.host)
            self.ansible_executor.write_variables(
                path=project_local_path)
            self.ansible_executor.write_config(
                path=project_local_path,
                default_roles_path=roles_paths,
                default_module_path=os.path.join(
                    self.zuul_dir_path,
                    'zuul/ansible/base/library/'),
                action_plugins="{}:{}".format(os.path.join(
                    self.zuul_dir_path,
                    'zuul/ansible/base/actiontrusted'),
                    os.path.join(self.zuul_dir_path,
                                 'zuul/ansible/base/actiongeneral')))
            self.ansible_executor.execute(
                work_dir=project_local_path,
                playbook=os.path.join(
                    project_local_path, playbook['path']))
