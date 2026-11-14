#!/usr/bin/env python3
"""只读校验网页模型与家具引用；不启动业务服务、不修改场景。"""
import base64
import json
from pathlib import Path
import re
import struct
import sys


def read_glb(path):
    raw = base64.b64decode(''.join(path.read_text().split()), validate=True)
    if len(raw) < 20:
        raise ValueError('GLB 文件不完整')
    magic, version, size = struct.unpack_from('<4sII', raw)
    if (magic, version, size) != (b'glTF', 2, len(raw)):
        raise ValueError('GLB 文件头或长度不正确')
    offset, document = 12, None
    while offset < size:
        if offset + 8 > size:
            raise ValueError('GLB 分块头不完整')
        length, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        if length % 4 or offset + length > size:
            raise ValueError('GLB 分块长度不正确')
        if kind == 0x4E4F534A:
            document = json.loads(raw[offset:offset + length])
        offset += length
    if document is None:
        raise ValueError('缺少 GLB JSON 分块')
    return document


def validate(root):
    web = root / '高新店24F整层_第三版_1108' / '网页实时3D'
    source = (web / 'index.html').read_text()
    data, _ = json.JSONDecoder().raw_decode(source.split('const DATA = ', 1)[1])
    match = re.search(r"const files=\[(.*?)\];", source)
    if not match:
        raise ValueError('找不到网页模型清单')
    models = {}
    for name in re.findall(r"'([^']+\.glb)'", match[1]):
        path = web / name.replace('.glb', '.b64.txt')
        models[name] = read_glb(path)
        print(f'通过：{path.name}（GLB v2）')
    if len(models) != 6:
        raise ValueError('预期六个网页模型')
    library = models['library.glb']
    roots = library['scenes'][library.get('scene', 0)]['nodes']
    keys = {library['nodes'][i].get('name', '')[2:] for i in roots
            if library['nodes'][i].get('name', '').startswith('K_')}
    missing = {e['key'] for e in data['layout']} - keys
    if missing:
        raise ValueError('家具原型缺失：' + ', '.join(sorted(missing)))
    print(f"通过：{len(data['layout'])} 个家具实例均有场景根原型（{len(keys)} 种）")
    for room in ('2414', '2415'):
        entries = [e for e in data['layout'] if e.get('room') == room]
        if not entries:
            raise ValueError(f'{room} 样板间没有家具实例')
        print(f"{room}：{len(entries)} 个实例；原型：" + ', '.join(sorted({e['key'] for e in entries})))
    for name in ('banyuexuan_24f_full.blend', 'banyuexuan_24f_staged.blend', 'banyuexuan_staff.blend'):
        path = web.parent / 'Blender源文件' / name
        if not path.is_file() or not path.stat().st_size:
            raise ValueError('Blender 源文件缺失或为空：' + name)
    print('通过：三个 Blender 源文件存在且非空；导出一致性和视觉效果仍需 Blender/浏览器验收')


if __name__ == '__main__':
    try:
        validate(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, IndexError, struct.error) as error:
        print('校验失败：' + str(error), file=sys.stderr)
        sys.exit(1)
