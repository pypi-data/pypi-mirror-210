# PronounDB Python API

![PyPI](https://img.shields.io/pypi/v/pronoundb?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pronoundb?style=flat-square)
![PyPI - License](https://img.shields.io/pypi/l/pronoundb?style=flat-square)

API wrapper for the pronoundb.org API.

## Installation

```bash
pip install pronoundb
```

## Examples

lookup someone's pronouns by their discord id:

```py
from pronoundb import lookup, Platform

lookup(Platform.DISCORD, 123456789012345678)
# -> {123456789012345678: ["he", "him"]}
```

lookup someone's pronouns by their minecraft (java) uuid:

```py
from pronoundb import lookup, Platform

lookup(Platform.MINECRAFT, "12345678-1234-1234-1234-123456789012")
# -> {"12345678-1234-1234-1234-123456789012": ["they", "them"]}
```

lookup multiple users pronouns by their discord id:

```py
from pronoundb import lookup, Platform

lookup(Platform.DISCORD, [123456789012345678, 987654321098765432])
# -> {123456789012345678: ["he", "him"], 987654321098765432: ["she", "her"]}
```

## Supported Platforms

- Discord
- GitHub
- Minecraft (Java)
- Twitch
- Twitter

## Custom Pronouns (Version 2.0.0)

Beginning with version 2.0.0 you can give the lookup function a list of pronouns to translate them for example.

```py
from pronoundb import lookup, Platform

lookup(Platform.DISCORD, 123456789012345678, {
    "unspecified": [],
    "he": ["Er", "Ihn"],
    "she": ["Sie", "Ihr"],
    "they": ["They", "Them"],
    "any": ["Jede"],
    "other": ["Anderes"],
    "ask": ["Frag"],
    "avoid": ["Nutz Name"],
})
# -> {123456789012345678: ["Er", "Ihn"]}
```

## Contributing

Contributions to this library are always welcome and highly encouraged.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
