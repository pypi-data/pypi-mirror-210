# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskbadger',
 'taskbadger.internal',
 'taskbadger.internal.api',
 'taskbadger.internal.api.action_endpoints',
 'taskbadger.internal.api.task_endpoints',
 'taskbadger.internal.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.3.0',
 'httpx>=0.15.4,<0.24.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'tomlkit>=0.11.6,<0.12.0',
 'typer[all]>=0.7.0,<0.8.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['taskbadger = taskbadger.cli:app']}

setup_kwargs = {
    'name': 'taskbadger',
    'version': '0.4.0',
    'description': 'The official Python SDK for Task Badger',
    'long_description': '# Task Badger Python Client\n\nThis is the official Python SDK for [Task Badger](https://taskbadger.net/).\n\nFor full documentation go to https://docs.taskbadger.net/python/.\n\n---\n\n## Getting Started\n\n### Install\n\n```bash\npip install --upgrade taskbadger\n```\n\n### Client Usage\n\n#### Configuration\n\n```python\nimport taskbadger\n\ntaskbadger.init(\n    organization_slug="my-org",\n    project_slug="my-project",\n    token="***"\n)\n```\n\n#### API Example\n\n```python\nfrom taskbadger import Task, Action, EmailIntegration\n\n# create a new task with custom data and an action definition\ntask = Task.create(\n    "task name",\n    data={\n        "custom": "data"\n    },\n    actions=[\n        Action(\n            "*/10%,success,error",\n            integration=EmailIntegration(to="me@example.com")\n        )\n    ]\n)\n\n# update the task status to \'processing\' and set the value to 0\ntask.started()\ntry:\n   for i in range(100):\n      do_something(i)\n      if i!= 0 and i % 10 == 0:\n         # update the progress of the task\n         task.update_progress(i)\nexcept Exception as e:\n    # record task errors\n    task.error(data={\n        "error": str(e)\n    })\n    raise\n\n# record task success\ntask.success()\n```\n\n### CLI USage\n\n#### Configuration\n\n```shell\n$ taskbadger configure\n\nOrganization slug: my-org\nProject slug: project-x\nAPI Key: XYZ.ABC\n\nConfig written to ~/.config/taskbadger/config\n```\n\n#### Usage Examples\n\nThe CLI `run` command executes your command whilst creating and updating a Task Badger task.\n\n```shell\n$ taskbadger run "demo task" --action "error email to:me@test.com" -- path/to/script.sh\n\nTask created: https://taskbadger.net/public/tasks/xyz/\n```\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://taskbadger.net/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
