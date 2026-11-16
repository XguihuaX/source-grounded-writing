#!/usr/bin/env python3
"""Build standard and WorkBuddy skill ZIPs using Python's standard library."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'source-grounded-writing'
VERSION = '1.1.0'
SKILL = ROOT / 'skills' / NAME
FILES = [
    'SKILL.md',
    'references/material-library.md', 'references/redaction.md',
    'references/writing-review.md', 'references/natural-writing.md',
    'templates/project-overview.md', 'templates/material-index.json',
    'templates/writing-task.md', 'scripts/init_library.py',
    'references/material-handoff.md',
    'references/humanizer-zh/SKILL.md', 'references/humanizer-zh/README.md',
    'references/humanizer-zh/LICENSE', 'references/humanizer-zh/SOURCE.json',
]


def workbuddy_skill(source):
    _, front, body = source.split('---', 2)
    match = re.search(r'^description: (.+)$', front, re.M)
    if not match:
        raise ValueError('Missing single-line description')
    fields = {
        'name': NAME,
        'display_name': '材料驱动的文档编写与审核',
        'display_name_en': 'Source Grounded Writing',
        'description': match.group(1),
        'description_zh': '先建立可复用资料库，再按模板编写、核对事实与图文并润色；支持人工脱敏确认与已有解读复用。',
        'description_en': 'Build reusable project material libraries, then draft and review documents against templates and source evidence.',
        'version': VERSION,
        'author': 'XguihuaX',
        'examples_zh': ['整理上传材料，先复用已有解读，建立项目资料库。',
                        '根据已确认的项目资料按模板写报告，先给框架。'],
        'examples_en': ['Organize my project materials and reuse existing summaries.',
                        'Draft and review a report using my template and project sources.'],
    }
    # JSON scalar and array syntax is valid YAML; avoids a YAML runtime dependency.
    return '---\n' + '\n'.join(k + ': ' + json.dumps(v, ensure_ascii=False)
                               for k, v in fields.items()) + '\n---' + body


def validate_sources():
    for name in FILES:
        path = SKILL / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('Missing or linked skill resource: ' + name)
        text = path.read_text(encoding='utf-8')
        if '/Users/' in text or 'C:\\Users\\' in text:
            raise ValueError('Personal absolute path in ' + name)
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                resolved = (path.parent / target.split('#')[0]).resolve()
                resolved.relative_to(SKILL.resolve())
                if not resolved.is_file():
                    raise ValueError('Broken relative link: ' + target)
    json.loads((SKILL / 'templates/material-index.json').read_text(encoding='utf-8'))
    compile((SKILL / 'scripts/init_library.py').read_text(encoding='utf-8'), 'init_library.py', 'exec')


def build(output=None):
    validate_sources()
    dest = Path(output) if output else ROOT / 'dist'
    dest.mkdir(parents=True, exist_ok=True)
    source = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    artifacts = []
    for variant in ('standard', 'workbuddy'):
        path = dest / f'{NAME}-{variant}-v{VERSION}.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            contents = {name: (SKILL / name).read_bytes() for name in FILES}
            contents['LICENSE'] = (ROOT / 'LICENSE').read_bytes()
            if variant == 'workbuddy':
                contents['SKILL.md'] = workbuddy_skill(source).encode('utf-8')
            for name, data in sorted(contents.items()):
                info = zipfile.ZipInfo(NAME + '/' + name, date_time=(2026, 11, 16, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError('ZIP integrity failure')
        artifacts.append(path)
    checksums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                        for p in artifacts)
    (dest / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
    return artifacts


if __name__ == '__main__':
    for artifact in build():
        print(artifact)
