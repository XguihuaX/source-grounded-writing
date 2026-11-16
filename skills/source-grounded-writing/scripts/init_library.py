#!/usr/bin/env python3
"""Initialize a source-grounded writing workspace; never replace existing files.

Python 3.8+, standard library only. Does not inspect or upload source materials.
"""
import argparse
import json
import re
from pathlib import Path


def project_component(value):
    value = value.strip()
    stem = value.split('.')[0].upper()
    reserved = {'CON', 'PRN', 'AUX', 'NUL'} | {
        prefix + str(n) for prefix in ('COM', 'LPT') for n in range(1, 10)
    }
    if (not value or value in ('.', '..') or value.endswith('.')
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
            or stem in reserved):
        raise argparse.ArgumentTypeError('项目名称须为单个有效文件夹名，不含路径分隔符或保留字符。')
    return value


def write_new(path, text, created, retained):
    try:
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    except FileExistsError:
        retained.append(str(path))
    else:
        created.append(str(path))


def initialize(root, project):
    root = root.expanduser().resolve()
    target = root / 'projects' / project
    # Reject project links that escape the selected root, including on Python 3.8.
    target.resolve().relative_to(root)
    dirs = [root, root / 'projects', root / 'requirements', root / 'examples',
            root / 'drafts', target, target / 'originals', target / 'summaries', target / 'images']
    for directory in dirs:
        directory.resolve().relative_to(root)
        directory.mkdir(parents=True, exist_ok=True)
    templates = Path(__file__).resolve().parent.parent / 'templates'
    index = json.loads((templates / 'material-index.json').read_text(encoding='utf-8'))
    index['project'] = project
    created, retained = [], []
    write_new(root / 'project-index.md',
              '# 项目索引\n\n项目位于 `projects/` 下，各项目的 `overview.md` 是阅读入口。\n'
              '初始化只建立文件结构；已读取、已解读和已确认状态由实际工作更新。\n', created, retained)
    write_new(target / 'material-index.json',
              json.dumps(index, ensure_ascii=False, indent=2) + '\n', created, retained)
    overview = (templates / 'project-overview.md').read_text(encoding='utf-8')
    write_new(target / 'overview.md', overview.replace('{{project}}', project), created, retained)
    return {'root': str(root), 'project': project, 'overview': str(target / 'overview.md'),
            'created': created, 'retained': retained,
            'next': '读取用户材料后填写索引和项目全貌；初始化不代表已阅读或审核。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='User-selected workspace directory')
    parser.add_argument('--project', required=True, type=project_component, help='Single project folder name')
    args = parser.parse_args()
    try:
        result = initialize(args.root, args.project)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'初始化失败：{exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
