"""Internationalization (i18n) module for CrewAI Studio."""

import json
import os
from pathlib import Path
import streamlit as st
from streamlit import session_state as ss

# Get the directory where this file is located
I18N_DIR = Path(__file__).parent / "i18n"

# Load all available languages
_translations = {}

# Get default language from environment variable
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")


def _load_translations():
    """Load all translation files."""
    global _translations
    if not _translations:
        for lang_file in I18N_DIR.glob("*.json"):
            lang_code = lang_file.stem
            with open(lang_file, "r", encoding="utf-8") as f:
                _translations[lang_code] = json.load(f)


def get_available_languages():
    """Get list of available language codes."""
    _load_translations()
    return sorted(list(_translations.keys()))


def get_current_language():
    """Get the current language from session state, using DEFAULT_LANGUAGE if not set."""
    if "language" not in ss:
        ss.language = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in get_available_languages() else "en"
    return ss.language


def set_language(lang_code):
    """Set the current language."""
    if lang_code in get_available_languages():
        ss.language = lang_code
        st.rerun()


def t(key: str, **kwargs):
    """
    Translate a key to the current language.

    Args:
        key: Translation key in dot notation (e.g., "page.agents", "button.save")
        **kwargs: Variables to interpolate in the translation string

    Returns:
        Translated string, or the key itself if not found
    """
    _load_translations()
    lang = get_current_language()

    # Navigate through nested keys
    keys = key.split(".")
    translation = _translations.get(lang, {})

    for k in keys:
        if isinstance(translation, dict):
            translation = translation.get(k)
        else:
            return key  # Key not found

    if translation is None:
        # Fallback to English
        translation = _translations.get("en", {})
        for k in keys:
            if isinstance(translation, dict):
                translation = translation.get(k)
            else:
                return key

    # If still not found, return the key
    if translation is None:
        return key

    # Handle interpolation
    if kwargs and isinstance(translation, str):
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError):
            return translation

    return translation


def get_tool_label_variants(i18n_key: str):
    """Return the `tool.<i18n_key>` translation in every available language.

    Used to map historic (translated) tool names back to stable tool
    identifiers. Does not require a Streamlit session.
    """
    _load_translations()
    variants = []
    for translations in _translations.values():
        value = translations.get("tool", {}).get(i18n_key)
        if isinstance(value, str) and value not in variants:
            variants.append(value)
    return variants


def setup_language_selector():
    """Setup language selector in the sidebar."""
    with st.sidebar:
        st.divider()
        languages = get_available_languages()
        lang_names = {
            "en": "English",
            "zh": "简体中文",
        }

        current_lang = get_current_language()
        display_names = [lang_names.get(lang, lang) for lang in languages]

        selected_idx = languages.index(current_lang)
        # Lock the language selector while a crew is running. Switching language
        # calls st.rerun(), which interrupts the run page's live refresh loop and
        # drops the running crew's progress (and can leave the Kickoff page
        # half-rendered). Re-enables automatically once the run finishes.
        running = ss.get("running", False)
        selected_lang = st.radio(
            t("language.select"),
            languages,
            index=selected_idx,
            format_func=lambda x: lang_names.get(x, x),
            label_visibility="collapsed",
            key="lang_selector",
            disabled=running,
        )

        if running:
            st.caption(t("language.locked_while_running"))
        elif selected_lang != current_lang:
            set_language(selected_lang)
