#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

CATEGORY_MAPPING = {
    "基本資訊": ["basic_info", "基本資訊"],
    "技術特性": ["technical_features", "technical_characteristics", "技術特性"],
    "效能指標": ["performance_metrics", "performance", "效能指標"],
    "里程碑意義": ["milestone_significance", "milestones", "里程碑意義"],
    "商業資訊": ["business_info", "commercial_info", "商業資訊"],
    "競爭與生態": ["competition_ecosystem", "competition", "競爭與生態"],
    "歷史沿革": ["history", "歷史沿革"],
    "市場定位": ["market_positioning", "market", "市場定位"],
}

_SKIP_KEYS = {"_source_file", "uncertain"}


def load_fields_yaml(fields_path):
    with fields_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = [
        (field["name"], category["category"], field.get("required", False))
        for category in data.get("field_categories", [])
        for field in category.get("fields", [])
    ]
    all_fields = {name for name, _, _ in items}
    required_fields = {name for name, _, required in items if required}
    field_categories = {name: category for name, category, _ in items}
    return all_fields, required_fields, field_categories


def extract_json_fields(data, category_mapping=None):
    category_mapping = CATEGORY_MAPPING if category_mapping is None else category_mapping
    nested_keys = {k for keys in category_mapping.values() for k in keys}
    fields = set()
    stack = [(data, True)]
    while stack:
        obj, is_category_level = stack.pop()
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in _SKIP_KEYS:
                    continue
                if is_category_level and k in nested_keys:
                    if isinstance(v, dict):
                        stack.append((v, True))
                    continue
                fields.add(k)
        elif isinstance(obj, list):
            stack.extend((item, is_category_level) for item in obj if isinstance(item, dict))
    return fields


def validate_json(json_path, all_fields, required_fields, field_categories):
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    json_fields = extract_json_fields(data)
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields
    missing_required = missing & required_fields
    missing_by_category = defaultdict(list)
    for field in missing:
        missing_by_category[field_categories.get(field, "未知")].append(field)
    return {
        "file": json_path.name,
        "total_defined": len(all_fields),
        "covered": len(covered),
        "missing": len(missing),
        "extra": len(extra),
        "coverage_rate": len(covered) / len(all_fields) * 100 if all_fields else 100,
        "missing_required": sorted(missing_required),
        "missing_optional": sorted(missing - required_fields),
        "missing_by_category": {k: sorted(v) for k, v in missing_by_category.items()},
        "extra_fields": sorted(extra),
        "valid": len(missing_required) == 0,
    }


def print_result(result, verbose=True):
    status = "通過" if result["valid"] else "失敗"
    line = "=" * 60
    print(f"\n{line}")
    print(f"[{status}] {result['file']}")
    print(line)
    print(f"覆蓋率: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")
    if result["missing_required"]:
        print(f"\n[錯誤] 缺少必填欄位 ({len(result['missing_required'])}):")
        print("\n".join(f"  - {f}" for f in result["missing_required"]))
    if verbose and result["missing_optional"]:
        missing_required = set(result["missing_required"])
        print(f"\n[警告] 缺少可選欄位 ({len(result['missing_optional'])}):")
        for cat in sorted(result["missing_by_category"]):
            optional = [f for f in result["missing_by_category"][cat] if f not in missing_required]
            if optional:
                print(f"  [{cat}]: {', '.join(optional)}")
    if verbose and result["extra_fields"]:
        extra = result["extra_fields"]
        print(f"\n[資訊] 額外欄位 ({len(extra)}):")
        print(f"  {', '.join(extra[:10])}")
        if len(extra) > 10:
            print(f"  ... 還有 {len(extra) - 10} 個")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="驗證JSON文件是否覆蓋fields.yaml中定義的所有欄位")
    parser.add_argument("--fields", "-f", type=str, help="fields.yaml路徑", default="fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="要驗證的JSON文件路徑")
    parser.add_argument("--dir", "-d", type=str, help="包含JSON文件的目錄", default="results")
    parser.add_argument("--quiet", "-q", action="store_true", help="僅顯示摘要")
    args = parser.parse_args()
    fields_path = Path(args.fields)
    if not fields_path.exists():
        for p in (Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"):
            if p.exists():
                fields_path = p
                break
    if not fields_path.exists():
        print(f"[錯誤] 找不到fields.yaml: {fields_path}")
        sys.exit(1)
    print(f"欄位定義文件: {fields_path}")
    all_fields, required_fields, field_categories = load_fields_yaml(fields_path)
    print(f"總欄位數: {len(all_fields)} (必填: {len(required_fields)}, 可選: {len(all_fields) - len(required_fields)})")
    json_files = (
        [Path(p) for p in args.json]
        if args.json
        else sorted(Path(args.dir).glob("*.json")) if Path(args.dir).exists() else []
    )
    if not json_files:
        print("[警告] 未找到JSON文件")
        sys.exit(0)
    results = []
    for json_path in json_files:
        if not json_path.exists():
            print(f"[警告] 文件不存在: {json_path}")
            continue
        result = validate_json(json_path, all_fields, required_fields, field_categories)
        results.append(result)
        print_result(result, verbose=not args.quiet)
    line = "=" * 60
    print(f"\n{line}")
    print("匯總")
    print(line)
    passed = sum(1 for r in results if r["valid"])
    avg_coverage = sum(r["coverage_rate"] for r in results) / len(results) if results else 0
    print(f"驗證通過: {passed}/{len(results)}")
    print(f"平均覆蓋率: {avg_coverage:.1f}%")
    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
