#!/usr/bin/env python3
"""生成交接索引并经独立镜像备份，验证远端分支及检查点；不改开发 Git 历史。"""
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = Path.home() / '.banyuexuan-project-sync'
REPO = 'Alston3825/banyuexuan-digital-twin-gaoxin'
SOURCES = ['AGENTS.md', '备份与交接/交接说明.md', '备份与交接/备份计划.md',
           'docs/AI接手说明.md', 'docs/当前开发任务.md', 'docs/服务器对接状态.md',
           'docs/定位接入/呼叫定位项目对接核验.md', '备份与交接/资料覆盖清单.md']


def prepare(root, now):
    evidence = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}
    note = '# 自动交接索引\n\n'
    note += f'实际整理时间：{now.isoformat(timespec="seconds")}（America/Los_Angeles）。\n\n'
    note += '先读[交接说明](交接说明.md)，再读各入口最新条目。下列哈希只证明读取了文件，不代表软件通过测试或现场已经部署。\n\n'
    note += ''.join(f'- [{name}](../{name})；SHA256 `{digest}`\n' for name, digest in evidence.items())
    note += '\n上传成功须检查远端 main、checkpoint 标签及本机 digital-checkpoint-status.json 的实际时间；旧成功记录不等于本轮成功。\n'
    target = root / '备份与交接/自动交接索引.md'
    target.write_text(note)
    daily = root / '备份与交接/每日交接'
    daily.mkdir(exist_ok=True)
    body = f'# {now:%Y-%m-%d} 当日交接快照\n\n实际捕获时间：{now.isoformat(timespec="seconds")}。不补造停机期间的历史。\n\n'
    for name in ['备份与交接/交接说明.md', 'docs/当前开发任务.md']:
        body += f'\n---\n\n来源：`{name}`\n\n' + (root / name).read_text()
    (daily / f'{now:%Y-%m-%d}.md').write_text(body)


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true', help='只更新本机交接索引，不上传')
    args = parser.parse_args()
    now = datetime.datetime.now(ZoneInfo('America/Los_Angeles'))
    if args.prepare_only:
        prepare(ROOT, now)
        print('交接索引与当日快照已更新，未上传。')
        return
    with (BASE / 'sync.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('其他备份正在运行，请稍后重试；本轮未完成')
        spec = importlib.util.spec_from_file_location('source_sync', BASE / 'sync.py')
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        if not sync.skip_directory(ROOT / 'local-private', Path('local-private')):
            raise RuntimeError('同步服务缺少 local-private 排除规则，停止上传')
        project = next(p for p in json.loads((BASE / 'projects.json').read_text()) if p['id'] == 'digital')
        if Path(project['source']).resolve() != ROOT or project['repo'] != REPO or project['existing']:
            raise RuntimeError('项目目录、固定仓库或分支配置不匹配')
        prepare(ROOT, now)
        result = sync.snapshot(project)
        mirror = BASE / 'repos/digital'
        remote = sync.git(mirror, 'ls-remote', 'origin', 'refs/heads/main').split()[0]
        if remote != result['commit']:
            raise RuntimeError('远端 main 与备份提交不一致')
        # 微秒避免手动连续重跑冲突。标签只标真实执行，不伪造过去的四个时点。
        tag = 'checkpoint/' + now.strftime('%Y%m%d-%H%M%S-%f')
        sync.git(mirror, 'tag', tag, result['commit'])
        sync.git(mirror, 'push', 'origin', 'refs/tags/' + tag)
        remote_tag = sync.git(mirror, 'ls-remote', 'origin', 'refs/tags/' + tag).split()[0]
        if remote_tag != result['commit']:
            raise RuntimeError('远端检查点标签不一致')
        result.update(checkpoint=tag, timezone='America/Los_Angeles', result='ok')
        target = BASE / 'digital-checkpoint-status.json'
        temp = target.with_suffix('.part')
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        os.replace(temp, target)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    run()
