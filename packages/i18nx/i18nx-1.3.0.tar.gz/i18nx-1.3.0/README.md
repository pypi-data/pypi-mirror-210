# I18n for Python

[![pypi version](https://badge.fury.io/py/i18nx.svg)](https://pypi.org/project/i18nx/)
[![Build status](https://gitlab.com/demsking/i18nx/badges/main/pipeline.svg)](https://gitlab.com/demsking/i18nx/pipelines)
[![Test Coverage](https://gitlab.com/demsking/i18nx/badges/main/coverage.svg)](https://gitlab.com/demsking/i18nx/-/jobs)
[![Buy me a beer](https://img.shields.io/badge/Buy%20me-a%20beer-1f425f.svg)](https://www.buymeacoffee.com/demsking)

Lightweight i18n for Python.

## Install

```sh
pip install i18nx
```

## Usage

```python
from i18nx import I18n

i18n = I18n(
  locale = 'en',
  fallback = 'fr',
  translations = {
    'en': { 'message': { 'hello': 'Hello World!' } },
    'fr': { 'message': { 'hello': 'Bonjour le monde !' } },
  },
)

print(i18n.tr("message.hello")) # Hello World!
```

## Message Format Syntax

**Interpolation**

`i18nx` use the Mustache like placeholders `{}` syntax for interpolation.

```python
from i18nx import I18n

i18n = I18n(
  locale = 'en',
  fallback = 'fr',
  translations = {
    'en': { 'message': { 'hello': 'Hello {name}!' } },
    'fr': { 'message': { 'hello': 'Bonjour {name} !' } },
  },
)

print(i18n.tr("message.hello", name = 'Mario')) # Hello Mario!
```

**Pluralization**

Use a pipe `|` separator in combination with the param `count` to define
plurals on the locale translations.

```python
from i18nx import I18n

i18n = I18n(
  locale = 'en',
  fallback = 'fr',
  translations = {
    'en': {
      'car': 'car | cars',
      'apple': 'no apples | one apple | {count} apples',
    },
  },
)

print(i18n.tr("car")) # 'car'
print(i18n.tr("car", count = 0)) # 'car'
print(i18n.tr("car", count = 1)) # 'car'
print(i18n.tr("car", count = 2)) # 'cars'
print(i18n.tr("apple", count = 0)) # 'no apples'
print(i18n.tr("apple", count = 1)) # 'one apple'
print(i18n.tr("apple", count = 15)) # '15 apples'
```

**List of Messages**

```python
from i18nx import I18n

i18n = I18n(
  locale = 'en',
  fallback_locale = 'fr',
  translations = {
    'en': {
      "greetings": [
        "Hey {firtname}!",
        "Hi {firtname}!",
      ],
    },
  },
)

print(i18n.tr("greetings.0", firtname = 'Mario')) # 'Hey Mario!'
print(i18n.tr("greetings.1", firtname = 'Mario')) # 'Hi Mario!'
```

## I18n API

```coffee
interface class I18n:
  constructor(locale: str, fallback_locale: str, translations: Dict[str, Dict[str, Any]], show_warning = False)

  # Active locale
  @property locale: str

  # Fallback locale
  @property fallback_locale: str

  # Available locales
  @getter available_locales: List[str]

  # Raw translations object for the active locale
  @getter raw: dict

  # Get translated text for the given dot path
  @method tr(path: str, **params) -> str

  # Get the raw message for the given dot path
  @method get_raw_message(path: str) -> Union[str, None]

  # Format the given raw message with the given params
  @method format_raw_message(message: str, **params) -> str
```

## Development Setup

1. [Install Nix Package Manager](https://nixos.org/manual/nix/stable/installation/installing-binary.html)

2. [Install `direnv` with your OS package manager](https://direnv.net/docs/installation.html#from-system-packages)

3. [Hook it `direnv` into your shell](https://direnv.net/docs/hook.html)

4. At the top-level of your project run:
   ```sh
   direnv allow
   ```

   The next time your launch your terminal and enter the top-level of your
   project, `direnv` will check for changes.

**Scripts**

```sh
# run tests
make test

# run tests with coverage
make coverage

# run linter
make lint

# run build process
make dist

# publish
make publish
```

## License

Under the MIT license.
See [LICENSE](https://gitlab.com/demsking/i18nx/blob/main/LICENSE)
file for more details.
