# CI Runner

Reproduce CI/CD builds in your environment

## Installation

```
git clone git@github.com:$USERNAME/ci-runner.git && cd ci-runner
virtualenv ~/.ci_runner
source ~/.ci_runner/bin/activate
pip install .
```

## Usage

runci --url <Zuul URL> --job <JOB NAME>
