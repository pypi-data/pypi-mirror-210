# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sosecrets']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sosecrets',
    'version': '0.1.0',
    'description': 'Simple wrapper to secure your secrets.',
    'long_description': '# sosecrets\n\n`sosecrets` is a Python module that provides a secure way to handle sensitive data by encapsulating it and only exposing it through a controlled interface.\n\n## Installation\n\nTo install `sosecrets`, you can use pip:\n\n```bash\npip install sosecrets\n```\n\n## Usage\n\nHere\'s an example of how to use `sosecrets`:\n\n```python\nfrom sosecrets import Secret\n\n# Create a secret value\nsecret_value = Secret("my secret value")\n\n# Use the secret value while keeping it encapsulated\nresult = secret_value.apply(len)\nprint(result)  # Output: 14\n\n# Get the value of the secret\nvalue = secret_value.expose_secret()\nprint(value)  # Output: "my secret value"\n```\n\nIn this example, we create a `Secret` object with the value "my secret value". We then use the `apply` method to apply the `len` function to the secret value while keeping it encapsulated. Finally, we use the `expose_secret` method to retrieve the value of the secret.\n\n## Use Cases\nsosecrets can be used in a variety of scenarios where sensitive data needs to be securely handled. Here are some common use cases:\n\nStoring API keys, passwords, and other credentials: sosecrets can be used to securely store sensitive information such as API keys, passwords, and other credentials that are required for authentication or authorization in an application.\n\nHandling personal identifiable information (PII): sosecrets can be used to protect personal identifiable information (PII) such as names, addresses, social security numbers, and other sensitive data that needs to be kept confidential.\n\n## API Reference\n\n### `Secret`\n\nThe `Secret` class encapsulates a secret value and only exposes it through a controlled interface.\n\n```\nSecret(value: Optional[T] = None, func: Optional[Callable[[Any], T]] = None, func_args: Tuple[Any] = tuple(), func_kwargs: Dict[str, Any] = dict()) -> SecretType\n```\n\n- `value`: The secret value to encapsulate.\n- `func`: A function to generate the secret value.\n- `func_args`: The positional arguments to pass to the `func` function.\n- `func_kwargs`: The keyword arguments to pass to the `func` function.\n\n#### `apply`\n\nThe `apply` method applies a function to the secret value while keeping it encapsulated.\n\n```python\napply(self, func: Callable[[Any], Any], *args: Tuple[Any], **kwargs: Dict[str, Any]) -> SecretType:\n```\n\n- `func`: The function to apply to the secret value.\n- `args`: The positional arguments to pass to the `func` function.\n- `kwargs`: The keyword arguments to pass to the `func` function.\n\n#### `expose_secret`\n\nThe `expose_secret` method returns the value of the secret.\n\n```python\ndef expose_secret(self) -> T:\n```\n\n### Exceptions\n\n`sosecrets` defines the following exceptions:\n\n#### `CannotInstantiateExposeSecret`\n\nRaised when attempting to instantiate the `__expose_secret__` class.\n\n#### `CannotInheritFromSecret`\n\nRaised when attempting to subclass the `Secret` class.\n\n#### `FuncAndValueCannotBeBothPassed`\n\nRaised when both `value` and `func` arguments are passed to the `Secret` constructor.\n\n## Contributing\n\nContributions are welcome! Let me know if you need help with anything else.',
    'author': 'Jim Chng',
    'author_email': 'jimchng@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
