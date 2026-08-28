#!/usr/bin/env python3
"""xhs-live 初始化引导 — 交互式询问品牌/品类/佣金/筛选阈值/留言/联系方式

用法:
    python init_skill.py            # 交互式初始化
    python init_skill.py --reset    # 重新初始化
    python init_skill.py --show     # 查看当前配置

生成: workspace/config.json (已被 .gitignore 排除)
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SKILL_DIR, "workspace", "config.json")
EXAMPLE_PATH = os.path.join(SKILL_DIR, "workspace", "config.example.json")


def load_example():
    with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ask(prompt, default=None):
    suffix = f" [默认: {default}]" if default is not None else ""
    val = input(f"{prompt}{suffix}: ").strip()
    if not val and default is not None:
        return default
    return val


def ask_int(prompt, default=None):
    while True:
        val = ask(prompt, default)
        try:
            return int(val)
        except ValueError:
            print(f"  请输入数字 (当前输入: {val})")


def ask_float(prompt, default=None):
    while True:
        val = ask(prompt, default)
        try:
            return float(val)
        except ValueError:
            print(f"  请输入数字 (当前输入: {val})")


def main():
    args = sys.argv[1:]

    if "--show" in args:
        if os.path.exists(CONFIG_PATH):
            print(json.dumps(json.load(open(CONFIG_PATH, encoding="utf-8")), ensure_ascii=False, indent=2))
        else:
            print("未初始化: workspace/config.json 不存在")
        return 0

    if os.path.exists(CONFIG_PATH) and "--reset" not in args:
        print("已存在 workspace/config.json")
        r = input("是否重新初始化? [y/N]: ").strip().lower()
        if r != "y":
            print("保留现有配置")
            return 0

    example = load_example()
    cfg = json.loads(json.dumps(example))  # deep copy structure

    print("=" * 50)
    print("xhs-live 初始化引导")
    print("请按提示填写你的品牌与合作信息")
    print("=" * 50)

    # 1. 品牌
    print("")
    print("[1/8] 品牌信息")
    cfg["brand"]["name"] = ask("品牌名")
    cfg["brand"]["category"] = ask("主营品类")
    cfg["brand"]["platform_category"] = ask("平台类目名(蒲公英类目, 如: 箱包皮具/热销女包/男包)")
    cfg["brand"]["price_band"] = ask("产品价格带(如: 500-2000)")

    # 2. 佣金
    print("")
    print("[2/8] 佣金比例 (%)")
    cfg["commission"]["lower"] = ask_int("佣金下限", example["commission"]["lower"])
    cfg["commission"]["higher"] = ask_int("佣金上限", example["commission"]["higher"])

    # 3. 筛选阈值
    print("")
    print("[3/8] 达人筛选阈值 (参考 reference/7维达人筛选标准.md)")
    cfg["filters"]["min_fans"] = ask_int("最低粉丝数", example["filters"]["min_fans"])
    cfg["filters"]["min_viewers"] = ask_int("最低场均观看", example["filters"]["min_viewers"])
    cfg["filters"]["min_sales"] = ask_int("最低场均销售额(元)", example["filters"]["min_sales"])
    cfg["filters"]["min_active_rate"] = ask_float("最低活跃粉丝率(0-1)", example["filters"]["min_active_rate"])
    cfg["filters"]["min_order_rate"] = ask_float("最低下单粉丝率(0-1)", example["filters"]["min_order_rate"])
    cfg["filters"]["price_min"] = ask_int("客单价下限(元)", example["filters"]["price_min"])
    cfg["filters"]["price_max"] = ask_int("客单价上限(元)", example["filters"]["price_max"])
    cfg["filters"]["min_gpm"] = ask_int("最低GPM", example["filters"]["min_gpm"])

    # 4. 留言模板
    print("")
    print("[4/8] 邀约留言模板")
    print("  提示: 佣金通过 API 参数传入, 留言中可引导加微信")
    cfg["message_template"] = ask("留言模板", example["message_template"])

    # 5. 联系方式
    print("")
    print("[5/8] 商家侧信息 (用于邀约)")
    cfg["seller"]["contact_name"] = ask("联系人姓名")
    cfg["seller"]["contact_phone"] = ask("联系电话")
    cfg["seller"]["contact_wechat"] = ask("微信号")

    # 6. seller_id / brand_user_id
    print("")
    print("[6/8] 平台 ID (可在 pgy_cookies.json 的 _seller_id/_brand_user_id 或环境变量配置)")
    cfg["seller"]["seller_id"] = ask("seller_id (留空则从 cookie/环境变量读取)")
    cfg["seller"]["brand_user_id"] = ask("brand_user_id (留空则从 cookie/环境变量读取)")

    # 确认
    print("")
    print("=" * 50)
    print("配置预览:")
    print(json.dumps(cfg, ensure_ascii=False, indent=2))
    print("=" * 50)
    r = input("确认保存? [Y/n]: ").strip().lower()
    if r == "n":
        print("已取消")
        return 1

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"已保存: {CONFIG_PATH}")
    print("接下来: 1) 配置 pgy_cookies.json (见 README)  2) python install_deps.py 安装依赖")
    return 0


if __name__ == "__main__":
    sys.exit(main())
