#!/usr/bin/env python3
"""校验综合测评规则数据集的结构与质量。

用法:
    python validate.py [path/to/rules.json]

退出码: 0=通过, 1=存在错误。可直接接入 CI。
"""
import json
import re
import sys
from pathlib import Path

# 规则条目的全部字段与期望类型
SCHEMA_FIELDS = {
    "rule_id": int,
    "academic_year": str,
    "dimension": str,
    "item_no": int,
    "category": str,
    "level": str,
    "grade": str,
    "points": (int, float),
    "unit": str,
    "aliases": str,
    "note": str,
}

# 五育框架(硬约束)
DIMENSIONS = {"德育", "智育", "体育", "美育", "劳育"}

# 复合唯一键(与生产库 schema 一致)
UNIQUE_KEY = ("academic_year", "dimension", "item_no", "category", "level", "grade")

# 适配者请替换/追加为本校名称: 防止把含校名的原始文件误提交进数据集。
# 示例: BANNED_SUBSTRINGS = ["某某大学", "某某学院"]
BANNED_SUBSTRINGS: list[str] = []

# 连续 >= 8 位数字: 疑似学号/证件号, 一律拒绝
STUDENT_ID_PATTERN = re.compile(r"\d{8,}")


def type_ok(value, expected) -> bool:
    if isinstance(value, bool):  # bool 是 int 的子类, 单独排除
        return False
    return isinstance(value, expected)


def main() -> int:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).parent / "data" / "rules.v1.json"
    )
    try:
        rules = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] 无法读取 {path}: {exc}")
        return 1
    if not isinstance(rules, list) or not rules:
        print("[FAIL] 顶层必须为非空数组")
        return 1

    errors: list[str] = []
    seen: dict[tuple, int] = {}

    for i, r in enumerate(rules, 1):
        where = f"第{i}条(rule_id={r.get('rule_id')})"

        for field, expected in SCHEMA_FIELDS.items():
            if field not in r:
                errors.append(f"{where} 缺字段 {field}")
            elif not type_ok(r[field], expected):
                errors.append(
                    f"{where} 字段 {field} 类型应为 {expected}, 实为 {type(r[field]).__name__}"
                )

        if r.get("dimension") not in DIMENSIONS:
            errors.append(f"{where} dimension 非法: {r.get('dimension')!r}")

        pts = r.get("points")
        if not type_ok(pts, (int, float)) or pts < 0:
            errors.append(f"{where} points 应为非负数, 实为 {pts!r}")

        key = tuple(r.get(k, "") for k in UNIQUE_KEY)
        if key in seen:
            errors.append(f"{where} 与第{seen[key]}条 UNIQUE 键重复: {key}")
        else:
            seen[key] = i

        blob = json.dumps(r, ensure_ascii=False)
        hit = STUDENT_ID_PATTERN.search(blob)
        if hit:
            errors.append(f"{where} 疑似学号/证件号(连续>=8位数字): {hit.group()}")
        for bad in BANNED_SUBSTRINGS:
            if bad and bad in blob:
                errors.append(f"{where} 含被禁止的字符串: {bad}")

    dims = sorted({r["dimension"] for r in rules})
    print(f"规则总数: {len(rules)}")
    print(f"五育覆盖: {'/'.join(dims)}")
    missing = DIMENSIONS - set(dims)
    if missing:
        print(f"[WARN] 未覆盖全部五育, 缺少: {sorted(missing)}")

    if errors:
        print(f"\n[FAIL] {len(errors)} 个错误:")
        for e in errors[:20]:
            print("  -", e)
        if len(errors) > 20:
            print(f"  ...(其余 {len(errors) - 20} 条省略)")
        return 1
    print("[OK] 校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
