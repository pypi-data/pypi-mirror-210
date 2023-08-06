# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pronoundb']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8,<4.0']

setup_kwargs = {
    'name': 'pronoundb',
    'version': '2.0.0',
    'description': 'API wrapper for the pronoundb.org API.',
    'long_description': '# PronounDB Python API\n\n![PyPI](https://img.shields.io/pypi/v/pronoundb?style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pronoundb?style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/pronoundb?style=flat-square)\n\nAPI wrapper for the pronoundb.org API.\n\n## Installation\n\n```bash\npip install pronoundb\n```\n\n## Examples\n\nlookup someone\'s pronouns by their discord id:\n\n```py\nfrom pronoundb import lookup, Platform\n\nlookup(Platform.DISCORD, 123456789012345678)\n# -> {123456789012345678: ["he", "him"]}\n```\n\nlookup someone\'s pronouns by their minecraft (java) uuid:\n\n```py\nfrom pronoundb import lookup, Platform\n\nlookup(Platform.MINECRAFT, "12345678-1234-1234-1234-123456789012")\n# -> {"12345678-1234-1234-1234-123456789012": ["they", "them"]}\n```\n\nlookup multiple users pronouns by their discord id:\n\n```py\nfrom pronoundb import lookup, Platform\n\nlookup(Platform.DISCORD, [123456789012345678, 987654321098765432])\n# -> {123456789012345678: ["he", "him"], 987654321098765432: ["she", "her"]}\n```\n\n## Supported Platforms\n\n- Discord\n- GitHub\n- Minecraft (Java)\n- Twitch\n- Twitter\n\n## Custom Pronouns (Version 2.0.0)\n\nBeginning with version 2.0.0 you can give the lookup function a list of pronouns to translate them for example.\n\n```py\nfrom pronoundb import lookup, Platform\n\nlookup(Platform.DISCORD, 123456789012345678, {\n    "unspecified": [],\n    "he": ["Er", "Ihn"],\n    "she": ["Sie", "Ihr"],\n    "they": ["They", "Them"],\n    "any": ["Jede"],\n    "other": ["Anderes"],\n    "ask": ["Frag"],\n    "avoid": ["Nutz Name"],\n})\n# -> {123456789012345678: ["Er", "Ihn"]}\n```\n\n## Contributing\n\nContributions to this library are always welcome and highly encouraged.\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.\n',
    'author': 'SteffoSpieler',
    'author_email': 'steffo@steffospieler.de',
    'maintainer': 'SteffoSpieler',
    'maintainer_email': 'steffo@steffospieler.de',
    'url': 'https://gitlab.com/SteffoSpieler/pronoundb-library',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
