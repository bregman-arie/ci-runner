# WORK IN PROGRESS

The project is not ready yet...patience! :)

## CI Runner

Reproduce CI/CD builds in your environment

## Installation

```
git clone git@github.com:$USERNAME/ci-runner.git && cd ci-runner
virtualenv ~/.ci_runner
source ~/.ci_runner/bin/activate
pip install .
```

## Usage

cirun --url <Zuul URL> --job <JOB NAME>

For example: `cirun --url https://zuul.openstack.org/ --job openstack-tox-pep8`
