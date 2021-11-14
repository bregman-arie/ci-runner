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


def general_usage():
    """Returns general usage string."""
    message = """
Usage Examples:

    Publish local data:
    $ {}

""".format(crayons.red(
        "cirun --url <CI SYSTEM> --tenant <JOBS TENANT> --job <JOB NAME>"))
    return message


def multiple_options(option):
    """Returns multiple options message."""
    message = """
There is more than one {0} defined...can't decide which one to use.
Please specify a single {0} with {1}
""".format(option, crayons.red("--" + option + " NAME"))
    return message


def missing_value(missing_value, possible_values):
    """Returns multiple options message."""
    message = """
There is no such value: {0}
Try one of the following: {1}
""".format(crayons.red(missing_value),
           crayons.green(','.join(possible_values)))
    return message
