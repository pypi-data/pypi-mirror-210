from snbtlib import dumps, loads
from pathlib import Path


text = Path('ars_noveau.snbt').read_text(encoding='utf-8')
Path('ars_noveau.snbt1').write_text(dumps(loads(text)), encoding='utf-8')