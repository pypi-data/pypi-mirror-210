# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edge_addons_api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'edge-addons-api',
    'version': '0.3.1',
    'description': 'API client for uploading addons to the Edge store',
    'long_description': '# Edge Addons API\n\n[![CI](https://github.com/inverse/python-edge-addons-api/actions/workflows/main.yml/badge.svg)](https://github.com/inverse/python-edge-addons-api/actions/workflows/main.yml)\n\nAn API client for publishing addons to the Edge store.\n\nBased on the [PlasmHQ Edge Addons API](https://github.com/PlasmoHQ/edge-addons-api).\n\n## Usage\n\nObtain the required options for your project. These can be obtained by following the [Microsoft Edge Add-Ons API guide](https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/publish/api/using-addons-api).\n\nOnce obtained you can submit you addon like below:\n\n\n```python\nfrom edge_addons_api.client import Options, Client\n\noptions = Options(\n    product_id="Your product ID",\n    client_id="Your client ID",\n    client_secret="Your client secret",\n    access_token_url="Your access token URL"\n)\n\nclient = Client(options)\n\n# Upload extension\noperation_id = client.submit(\n    file_path="/path/to/extension.zip",\n    notes="Your upload notes"\n)\n\n# Check publish status\nclient.fetch_publish_status(operation_id)\n```\n\n## License\n\nMIT\n',
    'author': 'Malachi Soord',
    'author_email': 'inverse.chi@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
