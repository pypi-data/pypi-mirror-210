# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tmlt',
 'tmlt.analytics',
 'tmlt.analytics._query_expr_compiler',
 'tmlt.analytics.constraints']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2.0,<2.0.0',
 'pyspark[sql]>=3.0.0,<=3.3.1',
 'sympy>=1.8,<1.10',
 'tmlt.core>=0.9.0,<0.10.0',
 'typeguard>=2.12.1,<2.13.0',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'tmlt-analytics',
    'version': '0.7.1',
    'description': "Tumult's differential privacy analytics API",
    'long_description': '# Tumult Analytics\n\nTumult Analytics is a library that allows users to execute differentially private operations on\ndata without having to worry about the privacy implementation, which is handled\nautomatically by the API. It is built atop the [Tumult Core library](https://gitlab.com/tumult-labs/core).\n\n## Installation\n\nSee the [installation instructions in the documentation](https://docs.tmlt.dev/analytics/latest/installation.html#prerequisites)\nfor information about setting up prerequisites such as Spark.\n\nOnce the prerequisites are installed, you can install Tumult Analytics using [pip](https://pypi.org/project/pip).\n\n```bash\npip install tmlt.analytics\n```\n\n## Documentation\n\nThe full documentation is located at https://docs.tmlt.dev/analytics/latest/.\n\n## Support\n\nIf you have any questions/concerns, please [create an issue](https://gitlab.com/tumult-labs/analytics/-/issues) or reach out to us on [Slack](https://tmltdev.slack.com/join/shared_invite/zt-1bky0mh9v-vOB8azKAVoxmzJDUdWd5Wg#).\n\n## Contributing\n\nWe are not yet accepting external contributions, but please let us know if you are interested in contributing [via Slack](https://tmltdev.slack.com/join/shared_invite/zt-1bky0mh9v-vOB8azKAVoxmzJDUdWd5Wg#).\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md) for information about installing our development dependencies and running tests.\n\n## Citing Tumult Analytics\n\nIf you use Tumult Analytics for a scientific publication, we would appreciate citations to the published software or/and its whitepaper. Both citations can be found below; for the software citation, please replace the version with the version you are using.\n\n```\n@software{tumultanalyticssoftware,\n    author = {Tumult Labs},\n    title = {Tumult {{Analytics}}},\n    month = dec,\n    year = 2022,\n    version = {latest},\n    url = {https://tmlt.dev}\n}\n```\n\n```\n@article{tumultanalyticswhitepaper,\n  title={Tumult {{Analytics}}: a robust, easy-to-use, scalable, and expressive framework for differential privacy},\n  author={Berghel, Skye and Bohannon, Philip and Desfontaines, Damien and Estes, Charles and Haney, Sam and Hartman, Luke and Hay, Michael and Machanavajjhala, Ashwin and Magerlein, Tom and Miklau, Gerome and Pai, Amritha and Sexton, William and Shrestha, Ruchit},\n  journal={arXiv preprint arXiv:2212.04133},\n  month = dec,\n  year={2022}\n}\n```\n\n## License\n\nCopyright Tumult Labs 2023\n\nThe Tumult Platform source code is licensed under the Apache License, version 2.0 (Apache-2.0).\nThe Tumult Platform documentation is licensed under\nCreative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA-4.0).\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.tmlt.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10.0',
}


setup(**setup_kwargs)
