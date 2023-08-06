# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opvious',
 'opvious.client',
 'opvious.data',
 'opvious.executors',
 'opvious.modeling',
 'opvious.specifications']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=2.2,<3.0',
 'humanize>=4.4.0,<5.0.0',
 'importnb>=2023.1.7,<2024.0.0',
 'pandas>=1.4,<2.0']

extras_require = \
{'aio': ['aiohttp>=3.8,<4.0', 'Brotli>=1.0.9,<2.0.0']}

setup_kwargs = {
    'name': 'opvious',
    'version': '0.12.4',
    'description': 'Opvious Python SDK',
    'long_description': '# Opvious Python SDK  [![CI](https://github.com/opvious/sdk.py/actions/workflows/ci.yml/badge.svg)](https://github.com/opvious/sdk.py/actions/workflows/ci.yml) [![Pypi badge](https://badge.fury.io/py/opvious.svg)](https://pypi.python.org/pypi/opvious/)\n\nAn optimization SDK for solving linear, mixed-integer, and quadratic models\n\n## Highlights\n\n### Declarative modeling API\n\n+ Extensive static validations\n+ Exportable to LaTeX\n+ Extensible support for high-level patterns (activation variables, masks, ...)\n\n```python\nimport opvious.modeling as om\n\nclass BinPacking(om.Model):\n  items = om.Dimension()\n  weight = om.Parameter.non_negative(items)\n  bins = om.interval(1, om.size(items))\n  bin_max_weight = om.Parameter.non_negative()\n\n  assigned = om.Variable.indicator(items, bins)\n  bin_used = om.Variable.indicator(bins)\n\n  @om.objective\n  def minimize_bins_used(self):\n    return om.total(self.bin_used(b) for b in self.bins)\n\n  @om.constraint\n  def each_item_is_assigned_once(self):\n    for i in self.items:\n      yield om.total(self.assigned(i, b) for b in self.bins) == 1\n\n  @om.constraint\n  def bins_with_assignments_are_used(self):\n    for i, b in om.cross(self.items, self.bins):\n      yield self.assigned(i, b) <= self.bin_used(b)\n\n  @om.constraint\n  def bin_weights_are_below_max(self):\n    for b in self.bins:\n      bin_weight = om.total(self.weight(i) * self.assigned(i, b) for i in self.items)\n      yield bin_weight <= self.bin_max_weight()\n```\n\n\n### Transparent remote solves\n\n+ No local solver installation required\n+ Real-time progress notifications\n+ Seamless data import/export via native support for `pandas`\n+ Flexible multi-objective support: weighted sums, epsilon constraints, ...\n+ Built-in debugging capabilities: relaxations, fully annotated LP formatting,\n  ...\n\n```python\nimport opvious\n\nclient = opvious.Client.from_environment()\n\nresponse = await client.run_solve(\n  specification=BinPacking().specification(),\n  parameters={\n    "weight": {"a": 10.5, "b": 22, "c": 48},\n    "binMaxWeight": 50,\n  },\n)\nsolution = response.outputs.variable("assigned")  # Optimal assignment dataframe\n```\n\nTake a look at https://opvious.readthedocs.io for the full documentation or\n[these notebooks][notebooks] to see the SDK in action.\n\n[notebooks]: https://github.com/opvious/examples/tree/main/notebooks\n',
    'author': 'Opvious Engineering',
    'author_email': 'oss@opvious.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/opvious/sdk.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
