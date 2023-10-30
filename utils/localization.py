from localize_py import Translator


def i18n(lang):
    Translator.load_translations(en='utils/locales/en_file.json',
                                 ro='utils/locales/ro_file.json',
                                 ru='utils/locales/ru_file.json')
    _ = Translator(lang)
    return _
