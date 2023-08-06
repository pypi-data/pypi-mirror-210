# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bento_mdf']

package_data = \
{'': ['*']}

install_requires = \
['bento-meta>=0.1.3',
 'delfick-project>=0.7.9,<0.8.0',
 'jsonschema>=4.17.3,<5.0.0',
 'pyyaml>=6',
 'requests>=2.28.2,<3.0.0',
 'tqdm>=4.64.1,<5.0.0']

scripts = \
['bin/test-mdf.py', 'bin/load-mdf.py']

setup_kwargs = {
    'name': 'bento-mdf',
    'version': '0.7.2',
    'description': 'Python driver/validator for Bento Model Description Format',
    'long_description': 'bento_mdf\n=======\n\nPython 3 drivers for the graph [Model Description Format](https://github.com/CBIIT/bento-mdf)\n\nThis directory provides ``test-mdf.py``, a standalone command line MDF validator.\n\n## Installation\n\nInstall the latest version (including scripts below) from GitHub using\nan up-to-date pip:\n\n\tpip install bento_mdf@git+https://github.com/CBIIT/bento-mdf.git#egg=subdir\\&subdirectory=drivers/python\n\n## Scripts\n\nScripts [`test-mdf.py`](./test-mdf.py) and\n[`load-mdf.py`](./load-mdf.py) are included in the\ndistribution. `test-mdf` is a verbose validator that can be used to\nfind issues in a set of local MDFs using the [MDF\nJSONSchema](../../schema/mdf-schema.yaml). `load-mdf` will load a\nvalid set of MDFs into an existing [Neo4j](https://neo4j.com) [Metamodel Database](https://github.com/CBIIT/bento-meta).\n\n\n## `test-mdf` Usage\n\n    $ test-mdf.py -h\n    usage: test-mdf.py [-h] [--schema SCHEMA] [--quiet] [--log-file LOG_FILE]\n                       mdf-file [mdf-file ...]\n\n    Validate MDF against JSONSchema\n\n    positional arguments:\n      mdf-file             MDF yaml files for validation\n\n    optional arguments:\n      -h, --help           show this help message and exit\n      --schema SCHEMA      MDF JSONschema file\n      --quiet              Suppress output; return only exit value\n      --log-file LOG_FILE  Log file name\n\nSee "Validator Notes" below.\n\n## `load-mdf` Usage\n\n    $ ./load-mdf.py -h\n    usage: load-mdf.py [-h] --commit COMMIT [--handle HANDLE] [--user USER] [--passw PASSW]\n                       [--bolt BoltURL] [--put]\n                       [MDF-FILE ...]\n\n    Load model in MDF into an MDB\n\n    positional arguments:\n      MDF-FILE         MDF file(s)/url(s)\n\n    optional arguments:\n      -h, --help       show this help message and exit\n      --commit COMMIT  commit SHA1 for MDF instance (if any)\n      --handle HANDLE  model handle\n      --user USER      MDB username\n      --passw PASSW    MDB password\n      --bolt BoltURL   MDB Bolt url endpoint (specify as \'bolt://...\')\n      --put            Load model to database\n\n## Validator `test-mdf.py`Notes\n\nThe ``--schema`` argument is optional. ``test-mdf.py`` will automatically retrieve the latest [mdf-schema.yaml](../../schema/mdf-schema.yaml) in the master branch of [this repo](https://github.com/CBIIT/bento-mdf).\n\nThe script tests both the syntax of the YAML (for both schema and MDF files), and the validity of the files with respect to the JSONSchema (for both schema and MDF files).\n\nThe errors are as emitted from the [PyYaml](https://pyyaml.org/wiki/PyYAMLDocumentation) and [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/) packages, and can be rather obscure.\n\n* Successful test\n\n        $ test-mdf.py samples/ctdc_model_file.yaml samples/ctdc_model_properties_file.yaml \n        Checking schema YAML =====\n        Checking as a JSON schema =====\n        Checking instance YAML =====\n        Checking instance against schema =====\n\n* Bad YAML syntax\n\n        $ test-mdf.py samples/ctdc_model_bad.yaml samples/ctdc_model_properties_file.yaml \n        Checking schema YAML =====\n        Checking as a JSON schema =====\n        Checking instance YAML =====\n        YAML error in \'samples/ctdc_model_bad.yaml\':\n        while parsing a block mapping\n          in "samples/ctdc_model_bad.yaml", line 1, column 1\n        expected <block end>, but found \'<block mapping start>\'\n          in "samples/ctdc_model_bad.yaml", line 3, column 3\n\n* Schema-invalid YAML\n\n        $ test-mdf.py samples/ctdc_model_file_invalid.yaml samples/ctdc_model_properties_file.yaml \n        Checking schema YAML =====\n        Checking as a JSON schema =====\n        Checking instance YAML =====\n        Checking instance against schema =====\n        [\'show_node\', \'specimen_id\', \'biopsy_sequence_number\', \'specimen_type\'] is not of type \'object\'\n        \n        Failed validating \'type\' in schema[\'properties\'][\'Nodes\'][\'additionalProperties\']:\n            {\'$id\': \'#nodeSpec\',\n             \'properties\': {\'Category\': {\'$ref\': \'#/defs/snake_case_id\'},\n                            \'Props\': {\'oneOf\': [{\'items\': {\'$ref\': \'#/defs/snake_case_id\'},\n                                                 \'type\': \'array\',\n                                                 \'uniqueItems\': True},\n                                                {\'type\': \'null\'}]},\n                            \'Tags\': {\'$ref\': \'#/defs/tagsSpec\'}},\n             \'required\': [\'Props\'],\n             \'type\': \'object\'}\n        \n        On instance[\'Nodes\'][\'specimen\']:\n            [\'show_node\', \'specimen_id\', \'biopsy_sequence_number\', \'specimen_type\']\n\n## Testing the tester\n\nThe validator code itself can be tested as follows:\n\n    pip install tox\n    cd bento-mdf/validators/mdf-validate\n    tox\n\n\n\n\n',
    'author': 'Mark A. Jensen',
    'author_email': 'mark.jensen@nih.gov',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'scripts': scripts,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
