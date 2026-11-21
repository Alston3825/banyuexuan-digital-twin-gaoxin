#!/usr/bin/env python3
"""在独立恢复副本校验源文件 SHA256，拒绝危险清单路径及私有目录。"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / 'docs/源码文件校验清单.json').read_text())
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError('清单为空或格式错误')
    failed = []
    for name, digest in manifest.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('清单包含非法路径')
        p = root / name
        if root not in p.resolve().parents or any((root / Path(*relative.parts[:i])).is_symlink()
                                                for i in range(1, len(relative.parts) + 1)):
            raise ValueError('清单路径越界或为符号链接')
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            failed.append(name)
    for p in root.rglob('*'):
        if '.git' in p.relative_to(root).parts:
            continue
        if 'local-private' in p.relative_to(root).parts:
            raise ValueError('恢复副本包含应排除的 local-private')
        if p.is_file() and (p.suffix.lower() in {'.pem', '.key', '.db', '.sqlite', '.sqlite3', '.jks', '.keystore'}
                            or p.name.startswith('.env') and not p.name.endswith(('.example', '.template'))):
            raise ValueError('恢复副本含禁止备份文件：' + str(p.relative_to(root)))
    if failed:
        raise ValueError('文件缺失或哈希不一致：' + ', '.join(failed))
    return len(manifest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(f'校验通过：{verify(args.root)} 个源文件；自动快照/清单不包含自身哈希。')
