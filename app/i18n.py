"""
International (i18n) support for CrewAI Studio
Simple JSON-based translation system
"""

import json
import os
from pathlib import Path
from streamlit import session_state as ss

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ko': '한국어'
}

# Default language
DEFAULT_LANGUAGE = 'en'

# Cache for loaded translations
_translations_cache = {}


def get_locale_path(lang_code: str) -> Path:
    """Get the path to a locale file"""
    return Path(__file__).parent / 'locale' / f'{lang_code}.json'


def load_translations(lang_code: str) -> dict:
    """Load translations for a specific language"""
    if lang_code in _translations_cache:
        return _translations_cache[lang_code]

    locale_file = get_locale_path(lang_code)

    if not locale_file.exists():
        # Fallback to English if translation file doesn't exist
        if lang_code != DEFAULT_LANGUAGE:
            return load_translations(DEFAULT_LANGUAGE)
        return {}

    try:
        with open(locale_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[lang_code] = translations
            return translations
    except Exception as e:
        print(f"Error loading translations for {lang_code}: {e}")
        return {}


def get_current_language() -> str:
    """Get the current language from session state"""
    if 'language' not in ss:
        ss.language = DEFAULT_LANGUAGE
    return ss.language


def set_language(lang_code: str):
    """Set the current language"""
    if lang_code in SUPPORTED_LANGUAGES:
        ss.language = lang_code
    else:
        ss.language = DEFAULT_LANGUAGE


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current language

    Args:
        key: Translation key in dot notation (e.g., 'common.create', 'agents.role')
        **kwargs: Optional format arguments for string interpolation

    Returns:
        Translated string or the key itself if translation not found

    Examples:
        t('common.create')  # "Create" or "생성"
        t('agents.max_iter', count=25)  # "Max Iterations: 25" or "최대 반복: 25"
    """
    lang = get_current_language()
    translations = load_translations(lang)

    # Navigate through nested keys (e.g., 'common.create' -> translations['common']['create'])
    keys = key.split('.')
    value = translations

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # Translation not found, return key as fallback
            return key

    # If value is still a dict, something went wrong
    if isinstance(value, dict):
        return key

    # Apply string formatting if kwargs provided
    if kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value


def get_language_options() -> dict:
    """Get available language options for UI"""
    return SUPPORTED_LANGUAGES


# Convenience alias
_ = t
