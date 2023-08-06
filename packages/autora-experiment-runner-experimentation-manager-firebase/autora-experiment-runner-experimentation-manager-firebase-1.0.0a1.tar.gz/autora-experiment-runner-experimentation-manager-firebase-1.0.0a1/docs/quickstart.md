# Quickstart Guide

You will need:
`python` >=3.8,<4: [https://www.python.org/downloads/](https://www.python.org/downloads/)

!!! It is recommended to use a python environment manger like virtualenv

Install the package via pip:

```shell
pip install -U "aurora[experiment-runner-experimentation-manager-firebase]"
```

## Test
```shell
python -c "from autora.experiment_runner.experimentation_manager.firebase import send_conditions"
```


## Dependencies

autora-core, firebase_admin
