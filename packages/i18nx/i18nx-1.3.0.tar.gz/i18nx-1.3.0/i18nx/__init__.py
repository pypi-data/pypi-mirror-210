"""Internationalization module for Python"""

from typing import Any, Dict, Union

Message = Dict[str, Union[str, int, float, list]]
Message = Dict[str, Union[str, int, float, list, Message]]

class I18nMissingMessageException(Exception):
  """Raised on missing path"""

class I18n:
  """I18n class"""

  raw: Dict[str, Dict[str, Any]]

  def __init__(
    self,
    locale: str,
    fallback_locale: str,
    translations: Dict[str, Message],
    raise_on_missing_path = False
  ):
    """Initializer"""

    self._locale = locale
    self._fallback_locale = fallback_locale
    self._raise_on_missing_path = raise_on_missing_path
    self._raw = translations
    self._translations = {
      lang: self._flatten(messages) for lang, messages in translations.items()
    }

    for lang in [locale, fallback_locale]:
      if lang not in self._translations:
        self._translations[lang] = {}

  @property
  def locale(self):
    """Active locale"""
    return self._locale

  @locale.setter
  def locale(self, value: str):
    """Set active locale"""
    self._locale = value

  @property
  def fallback_locale(self):
    """Fallback locale"""
    return self._fallback_locale

  @fallback_locale.setter
  def fallback_locale(self, value: str):
    """Set active locale"""
    self._fallback_locale = value

  @property
  def available_locales(self):
    """Available locales"""
    return self._translations.keys()

  @property
  def raw(self) -> dict:
    """Raw translations object for the active locale"""
    return self._raw[self._locale]

  def _flatten(self, input_object: Message):
    result = {}

    self._flatten_deep(input_object, None, result)

    return result

  def _flatten_deep(self, message: Message, base_key: str, result: dict):
    if isinstance(message, dict):
      for key in message:
        prop = f'{base_key}.{key}' if base_key else key
        value = message[key]

        self._flatten_deep(value, prop, result)
    elif isinstance(message, list):
      result[base_key] = message

      self._flatten_deep(dict(zip(list(range(len(message))), message)), base_key, result)
    else:
      result[base_key] = f'{message}'

  @staticmethod
  def get_message_variant(message: str, **params):
    """
    Get the appropriate message variant based on the provided parameters.

    Args:
      message (str): The message string containing variants separated by '|'.
      **params: Additional parameters used to determine the variant.

    Returns:
      str: The selected message variant based on the provided parameters.

    Example:
      I18n.get_message_variant("You have |{count} item|{count} items", count=3)
      Returns: "3 items"
    """
    count = params.get('count', 0)
    message = message.split('|')

    if len(message) == 2:
      message = [message[0]] + message

    if count == 0:
      return message[0]

    return message[1] if count == 1 else message[2]

  def get_raw_message(self, path: str) -> Union[str, None]:
    """Get the raw message for the given dot path"""

    if path in self._translations[self._locale]:
      return self._translations[self._locale][path]

    return self._translations[self._fallback_locale].get(path, None)

  @staticmethod
  def format_raw_message(message: str, **params):
    """
    Format a raw message string by replacing placeholders with provided parameter values.

    Args:
      message (str): The raw message string to be formatted.
      **params: Additional parameters used to replace placeholders in the message.

    Returns:
      str: The formatted message string with replaced placeholders.

    Example:
      I18n.format_raw_message("Hello, {name}! You have {count} new messages.", name="John", count=3)
      Returns: "Hello, John! You have 3 new messages."
    """
    if '|' in message:
      message = I18n.get_message_variant(message, **params).strip()

    for param, value in params.items():
      message = message.replace("{" + str(param) + "}", str(value))

    return message

  def tr(self, path: str, **params):
    """Get translated text for the given dot path"""

    message = self.get_raw_message(path)

    if message:
      return I18n.format_raw_message(message, **params)

    if self._raise_on_missing_path:
      raise I18nMissingMessageException(f"Missing translation message for path {path}")

    return path
