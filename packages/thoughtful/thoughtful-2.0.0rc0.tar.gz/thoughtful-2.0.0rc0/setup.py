# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thoughtful',
 'thoughtful.supervisor',
 'thoughtful.supervisor.reporting',
 'thoughtful.supervisor.streaming']

package_data = \
{'': ['*']}

install_requires = \
['aws-requests-auth>=0.4.3,<0.5.0',
 'boto3>=1.24.64,<2.0.0',
 'chevron>=0.14.0,<0.15.0',
 'isodate>=0.6.1,<0.7.0',
 'moto>=4.0.5,<5.0.0',
 'pre-commit>=2.17.0,<3.0.0',
 'pyconfs>=0.5.5,<0.6.0',
 'pydantic-yaml>=0.6.3,<0.7.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyyaml>=5.4.1',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'thoughtful',
    'version': '2.0.0rc0',
    'description': 'Thoughtful is a python package by Thoughtful for helping manage automations with helpful packages like supervisor',
    'long_description': '**thoughtful** is a collection of open-source libraries and tools for Robot Process\nAutomation (RPA) development. The goal of this project is to provide a set of\nfor supervising bot execution, and enabling these bots to do more.\n\n[![PyPi version](https://badgen.net/pypi/v/thoughtful/)](https://pypi.org/project/thoughtful/)\n![Main Branch Tests](https://github.com/Thoughtful-Automation/supervisor/actions/workflows/main-push.yml/badge.svg?branch=main)\n[![Supported Versions](https://img.shields.io/pypi/pyversions/thoughtful.svg)](https://pypi.org/project/thoughtful)\n[![Downloads](https://pepy.tech/badge/thoughtful/month)](https://pepy.tech/project/thoughtful)\n\n[//]: # ([![GitHub release]&#40;https://img.shields.io/github/release/Thoughtful-Automation/supervisor.svg&#41;]&#40;https://GitHub.com/Naereen/StrapDown.js/releases/&#41;)\n\n\nThis project is:\n* Open-source: [GitHub][url:gh]\n* Owned by [thoughtful][url:ta]\n* Licensed under the [Apache License 2.0][url:al]\n\nLinks:\n* [Homepage][url:gh]\n* [Documentation][url:readthedocs]\n* [PyPI][url:pypi]\n\n**thoughtful** is available on [PyPI][url:pypi] and can be installed using pip:\n\n```sh\npip install thoughtful\n```\n\n---\n\n**thoughtful** officially supports Python 3.7+.\n\n---\n\n# Libraries\n\nThis is a list of the available libraries in this project. API Reference\nand User Guide available on [docs][url:readthedocs].\n\n## Supervisor\n\nSupervisor is a Workflow Engine for Digital Workers that constructs\nand broadcasts a detailed and structured telemetric log, called the Run Report.\n\n```python\nfrom thoughtful.supervisor import step, step_scope, supervise, set_step_status\n\n\n# using the step decorator\n@step("2")\ndef step_2(name: str) -> bool:\n    print(f\'Hello {name}\')\n    return True  # some condition\n\ndef main() -> None:\n    # using the step_scope context manager\n    with step_scope(\'1\') as step_context:\n        try:\n            print("Getting credentials")\n            # ...\n        except Exception as e:\n            # set step status using method\n            step_context.set_status("warning")\n\n    if not step_2():\n        # set step status using function\n        set_step_status("2", "fail")\n\nif __name__ == \'__main__\':\n    with supervise():\n        main()\n```\n\n## Contributing\n\nContributions to **thoughtful** are welcome!\n\nTo get started, see the [contributing guide](CONTRIBUTING.md).\n\n---\n\n  Made with ❤️ by\n\n  [![Thoughtful](https://user-images.githubusercontent.com/1096881/141985289-317c2e72-3c2d-4e6b-800a-0def1a05f599.png)][url:ta]\n\n---\n\nThis project is open-source and licensed under the terms of the [Apache License 2.0][url:al].\n\n\n<!--  Link References -->\n\n[url:ta]: https://www.thoughtful.ai/\n[url:gh]: https://github.com/Thoughtful-Automation/supervisor\n[url:pypi]: https://pypi.org/project/thoughtful/\n[git:issues]: https://github.com/Thoughtful-Automation/supervisor/issues\n[url:readthedocs]: https://thoughtful-supervisor.readthedocs-hosted.com/en/latest/\n[url:al]: http://www.apache.org/licenses/LICENSE-2.0\n',
    'author': 'Thoughtful Automation',
    'author_email': 'engineering@thoughtfulautomation.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://thoughtfulautomation.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
