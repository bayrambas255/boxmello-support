"""Load source copy and complete translated catalogs without English fallbacks."""
import json
from pathlib import Path
from pages import CONTENT as SOURCE, EMAIL
from languages import LANGUAGES

CONTENT = dict(SOURCE)
for path in sorted((Path(__file__).parent / 'locales').glob('*.json')):
    assert path.stem in LANGUAGES and path.stem not in SOURCE, path
    translated = json.loads(path.read_text(encoding='utf-8'))
    if translated.get('pages', {}).keys() != SOURCE['en']['pages'].keys():
        raise ValueError(f'{path.name}: incomplete catalog; finish all documents before building')
    CONTENT[path.stem] = translated
CONTENT = {locale: CONTENT[locale] for locale in LANGUAGES if locale in CONTENT}
