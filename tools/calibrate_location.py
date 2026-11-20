#!/usr/bin/env python3
"""从独立 fit/check 点拟合平面相似变换；仅本机离线处理。"""
import argparse
import csv
import json
import math
from pathlib import Path
import sys


def read_points(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    points, ids = [], set()
    for row in rows:
        name = row['point_id'].strip()
        if not name or name in ids or row['use'] not in ('fit', 'check'):
            raise ValueError('点编号须唯一非空，use 须为 fit 或 check')
        ids.add(name)
        values = [float(row[key]) for key in ('source_x', 'source_y', 'plan_x', 'plan_y')]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('坐标必须为有限数值')
        points.append(dict(id=name, use=row['use'], source=values[:2], plan=values[2:]))
    return points


def require_spread(values):
    n = len(values)
    cx = sum(p[0] for p in values) / n
    cy = sum(p[1] for p in values) / n
    xx = sum((p[0] - cx) ** 2 for p in values)
    yy = sum((p[1] - cy) ** 2 for p in values)
    xy = sum((p[0] - cx) * (p[1] - cy) for p in values)
    if xx + yy <= 1e-12 or xx * yy - xy * xy <= 1e-6 * (xx + yy) ** 2:
        raise ValueError('拟合点重合、共线或分布过窄，请补充横向分散点')


def calibrate(points, threshold, flip_y=False):
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError('检查误差阈值须为正有限数值')
    fit = [p for p in points if p['use'] == 'fit']
    check = [p for p in points if p['use'] == 'check']
    if len(fit) < 3 or len(check) < 2:
        raise ValueError('至少需要 3 个 fit 点和 2 个独立 check 点')
    sign = -1 if flip_y else 1
    sources = [(p['source'][0], sign * p['source'][1]) for p in fit]
    targets = [p['plan'] for p in fit]
    require_spread(sources)
    require_spread(targets)
    # 同一物理点不能以另一编号混入验证集。
    for p in check:
        if any(math.dist(p['source'], q['source']) < 1e-9 or
               math.dist(p['plan'], q['plan']) < 1e-9 for q in fit):
            raise ValueError('check 点不能与 fit 点重合')
    n = len(fit)
    sx, sy = (sum(p[k] for p in sources) / n for k in (0, 1))
    px, py = (sum(p[k] for p in targets) / n for k in (0, 1))
    denom = sum((x - sx) ** 2 + (y - sy) ** 2 for x, y in sources)
    a = sum((x - sx) * (u - px) + (y - sy) * (v - py)
            for (x, y), (u, v) in zip(sources, targets)) / denom
    b = sum((x - sx) * (v - py) - (y - sy) * (u - px)
            for (x, y), (u, v) in zip(sources, targets)) / denom
    if math.hypot(a, b) <= 1e-12:
        raise ValueError('变换退化，请核对对应点与轴向')
    tx, ty = px - a * sx + b * sy, py - b * sx - a * sy
    matrix = [[a, -b * sign, tx], [b, a * sign, ty], [0, 0, 1]]
    errors = []
    for p in points:
        x, y = p['source']
        predicted = [a * x - b * sign * y + tx, b * x + a * sign * y + ty]
        errors.append(dict(point_id=p['id'], use=p['use'], predicted_plan=predicted,
                           error_m=math.dist(predicted, p['plan'])))
    summary = {}
    for group in ('fit', 'check'):
        vals = [e['error_m'] for e in errors if e['use'] == group]
        summary[group] = dict(count=len(vals), rms_m=math.sqrt(sum(v*v for v in vals)/len(vals)),
                              max_error_m=max(vals))
    report = dict(status='geometry_pass' if summary['check']['max_error_m'] <= threshold else 'geometry_fail',
                  field_verified=False, source_to_plan_matrix=matrix, flip_y=flip_y,
                  scale=math.hypot(a, b), rotation_degrees=math.degrees(math.atan2(b, a)),
                  max_check_error_m=threshold, summary=summary, points=errors)
    # 防止极端输入溢出而产生不可用配置。
    json.dumps(report, allow_nan=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path')
    parser.add_argument('--max-check-error-m', type=float, required=True)
    parser.add_argument('--flip-y', action='store_true')
    parser.add_argument('--output', help='新建本机报告文件，拒绝覆盖已有文件')
    args = parser.parse_args()
    try:
        report = calibrate(read_points(args.csv_path), args.max_check_error_m, args.flip_y)
        body = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            with Path(args.output).open('x', encoding='utf-8') as handle:
                handle.write(body)
        else:
            print(body, end='')
        return 0 if report['status'] == 'geometry_pass' else 1
    except (ValueError, KeyError, OSError, OverflowError) as exc:
        print(f'标定失败：{exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
