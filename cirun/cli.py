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
import argparse
import logging

from cirun.runner import Runner


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', dest='url', required=True,
                        help='CI/CD system URL')
    parser.add_argument('--job', dest='job_name',
                        required=True,
                        help='The name of the job to reproduce')
    parser.add_argument('--tenant', dest='tenant',
                        default='default',
                        help='The name of the tenant to use')
    parser.add_argument('--project', '-p', dest='project_name',
                        required=True,
                        help='The name of the project')
    parser.add_argument('--host', dest='host',
                        default='default',
                        help='The host on which to execute the job')
    parser.add_argument('--debug', dest='debug',
                        action='store_true', default=False,
                        help='Enable debug')
    return parser


def setup_logging(debug):
    """Sets the logging."""
    format = '%(message)s'
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=format)


def main():
    parser = create_parser()
    args = parser.parse_args()
    setup_logging(args.debug)
    runner = Runner(**vars(args))
    runner.validate_input()
    runner.run()


if __name__ == '__main__':
    main()
