# WORK IN PROGRESS

The project is not ready yet...patience! :)

## CI Runner

Reproduce CI/CD builds in your environment

Did you ever try to run a job from Zuul locally on your system? If you did, you know that the only way to do so, is trying to execute the same playbooks and roles that Zuul did. Even then, you might get a different result eventually. This can be quite frustrating.

This project aims to help you reproduce *easily* jobs from Zuul (at least until Zuul will implement a proper built-in mechanism for that).

## Installation

```
git clone git@github.com:$USERNAME/ci-runner.git && cd ci-runner
virtualenv ~/.ci_runner
source ~/.ci_runner/bin/activate
pip install .
```

## Usage

General usage: `cirun --url <Zuul URL> --job <JOB NAME> --project <PROJECT NAME`

For example: `cirun --url https://zuul.openstack.org/ --job openstack-tox-pep8 --project neutron`

## Supported Systems

Currently only `zuul` is a supported system to use for reproducing jobs from.
