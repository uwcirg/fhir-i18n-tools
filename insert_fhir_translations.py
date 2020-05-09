import argparse
import json
import os
import sys

translatable_ext_name = 'http://hl7.org/fhir/StructureDefinition/elementdefinition-' \
                        'translatable'


def main(bundle_path, translation_paths):
    with open(bundle_path) as file:
        b = json.load(file)

    t = {}
    for p in translation_paths:
        language_code = os.path.split(p)[1][:2]
        with open(p) as file:
            t[language_code] = json.load(file)

    for language_code in t:
        process_entire_node(b, language_code, t)

    print(f"Added translations for all the strings!", file=sys.stderr)
    json.dump(b, sys.stdout, indent=2)
    print('\n', file=sys.stdout)


def is_translatable(b, key):
    props_key = "_" + key
    if props_key in b and 'extension' in b[props_key]:
        for ext in b[props_key]['extension']:
            if ext['url'] == translatable_ext_name and ext['valueBoolean'] is True:
                return True
    return False


def translation_ext(language_code, translation):
    return {
        "url": "http://hl7.org/fhir/StructureDefinition/translation",
        "extension": [
            {
                "url": "lang",
                "valueCode": language_code
            },
            {
                "url": "content",
                "valueString": translation
            }
        ]
    }


def insert_translation(b, key, language_code, t):
    original = b[key]
    if original not in t[language_code]:
        print(f"The following string is missing the translation to {language_code}:\n"
              f"{original}\n", file=sys.stderr)
        return
    translation = t[language_code][original]
    props_key = "_" + key
    b[props_key]['extension'].append(translation_ext(language_code, translation))


def process_entire_node(b, language_code, t):
    if type(b) is not dict:
        return
    for key in b:
        process_node(b, key, language_code, t)


def process_node(b, key, language_code, t):
    if type(b) is not dict:
        return
    if type(b[key]) is dict:
        for key2 in b[key]:
            process_node(b[key], key2, language_code, t)
    elif type(b[key]) is str:
        if is_translatable(b, key):
            insert_translation(b, key, language_code, t)
    elif type(b[key]) is list:
        for sub_node in b[key]:
            process_entire_node(sub_node, language_code, t)
    else:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This script adds the translations from the given translation files "
                    "to the given FHIR bundle in the appropriate places. The new bundle "
                    "is written to stdout. If any translatable strings in the bundle do"
                    "not have appropriate translations in the translation files, these "
                    "strings will be output to stderr.")
    parser.add_argument("bundle_path",
                        help='Path to the FHIR bundle (JSON file) into which translations '
                             'should be inserted.',
                        type=str)
    parser.add_argument("translations",
                        help='Path(s) to the translations (JSON file(s)), keyed by base '
                             'language strings (en). The script will use the first two '
                             'characters of the file name as language code, so the files'
                             'should be named accordingly, e.g. `mn_fhir.json`',
                        type=str,
                        nargs='+', )
    args = parser.parse_args()

    main(args.bundle_path, args.translations)
