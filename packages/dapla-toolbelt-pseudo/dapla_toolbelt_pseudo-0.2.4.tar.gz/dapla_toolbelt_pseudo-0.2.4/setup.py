# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dapla_pseudo', 'dapla_pseudo.v1']

package_data = \
{'': ['*']}

install_requires = \
['cryptography==39.0.1',
 'dapla-toolbelt>=1.3.6,<2.0.0',
 'pydantic>=1.10.2,<2.0.0',
 'pyhumps>=3.8.0,<4.0.0',
 'pylibmagic>=0.2.2,<0.3.0',
 'python-magic>=0.4.27,<0.5.0',
 'types-requests>=2.28.11,<3.0.0']

setup_kwargs = {
    'name': 'dapla-toolbelt-pseudo',
    'version': '0.2.4',
    'description': 'Pseudonymization extensions for Dapla Toolbelt',
    'long_description': '# Pseudonymization extensions for Dapla Toolbelt\n\n[![PyPI](https://img.shields.io/pypi/v/dapla-toolbelt-pseudo.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/dapla-toolbelt-pseudo.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/dapla-toolbelt-pseudo)][python version]\n[![License](https://img.shields.io/pypi/l/dapla-toolbelt-pseudo)][license]\n\n[![Tests](https://github.com/statisticsnorway/dapla-toolbelt-pseudo/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/statisticsnorway/dapla-toolbelt-pseudo/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/dapla-toolbelt-pseudo/\n[status]: https://pypi.org/project/dapla-toolbelt-pseudo/\n[python version]: https://pypi.org/project/dapla-toolbelt-pseudo\n[tests]: https://github.com/statisticsnorway/dapla-toolbelt-pseudo/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/statisticsnorway/dapla-toolbelt-pseudo\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\nPseudonymize, repseudonymize and depseudonymize data on Dapla.\n\n## Usage\n\nSee the [command-line reference] for details.\n\n### Pseudonymize\n\n```python\nfrom dapla_pseudo import pseudonymize\n\n# Pseudonymize fields in a local file using the default key:\npseudonymize(file_path="./data/personer.json", fields=["fnr", "fornavn"])\n\n# Pseudonymize fields in a local file, explicitly denoting the key to use:\npseudonymize(file_path="./data/personer.json", fields=["fnr", "fornavn"], key="ssb-common-key-1")\n\n# Pseudonymize a local file using a custom key:\nimport json\ncustom_keyset = json.dumps(    {\n    "encryptedKeyset": "CiQAp91NBhLdknX3j9jF6vwhdyURaqcT9/M/iczV7fLn...8XYFKwxiwMtCzDT6QGzCCCM=",\n    "keysetInfo": {\n        "primaryKeyId": 1234567890,\n        "keyInfo": [\n            {\n                "typeUrl": "type.googleapis.com/google.crypto.tink.AesSivKey",\n                "status": "ENABLED",\n                "keyId": 1234567890,\n                "outputPrefixType": "TINK",\n            }\n        ],\n    },\n    "kekUri": "gcp-kms://projects/some-project-id/locations/europe-north1/keyRings/some-keyring/cryptoKeys/some-kek-1",\n})\npseudonymize(file_path="./data/personer.json", fields=["fnr", "fornavn"], key=custom_keyset)\n\n# Operate on data in a streaming manner:\nimport shutil\nwith pseudonymize("./data/personer.json", fields=["fnr", "fornavn", "etternavn"], stream=True) as res:\n    with open("./data/personer_deid.json", \'wb\') as f:\n        res.raw.decode_content = True\n        shutil.copyfileobj(res.raw, f)\n\n# Map certain fields to stabil ID\npseudonymize(file_path="./data/personer.json", fields=["fornavn"], sid_fields=["fnr"])\n```\n\n### Repseudonymize\n\n```python\nfrom dapla_pseudo import repseudonymize\n\n# Repseudonymize fields in a local file, denoting source and target keys to use:\nrepseudonymize(file_path="./data/personer_deid.json", fields=["fnr", "fornavn"], source_key="ssb-common-key-1", target_key="ssb-common-key-2")\n```\n\n### Depseudonymize\n\n```python\nfrom dapla_pseudo import depseudonymize\n\n# Depseudonymize fields in a local file using the default key:\ndepseudonymize(file_path="./data/personer_deid.json", fields=["fnr", "fornavn"])\n\n# Depseudonymize fields in a local file, explicitly denoting the key to use:\ndepseudonymize(file_path="./data/personer_deid.json", fields=["fnr", "fornavn"], key="ssb-common-key-1")\n```\n\n_Note that depseudonymization requires elevated access privileges._\n\n## Requirements\n\n- [Dapla Toolbelt](https://github.com/statisticsnorway/dapla-toolbelt)\n\n## Installation\n\nYou can install _dapla-toolbelt-pseudo_ via [pip] from [PyPI]:\n\n```console\npip install dapla-toolbelt-pseudo\n```\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_Pseudonymization extensions for Dapla Toolbelt_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis project was generated from [@cjolowicz]\'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/statisticsnorway/dapla-toolbelt-pseudo/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/statisticsnorway/dapla-toolbelt-pseudo/blob/main/LICENSE\n[contributor guide]: https://github.com/statisticsnorway/dapla-toolbelt-pseudo/blob/main/CONTRIBUTING.md\n[command-line reference]: https://statisticsnorway.github.io/dapla-toolbelt-pseudo\n',
    'author': 'Team Skyinfrastruktur',
    'author_email': 'dapla@ssb.no',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/statisticsnorway/dapla-toolbelt-pseudo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
