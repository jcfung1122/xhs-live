#!/usr/bin/env python3
"""xhs-live 依赖安装器（跨平台离线优先）

用法:
    python install_deps.py            # 自动识别平台, 离线优先, 失败回退在线
    python install_deps.py --online   # 强制在线安装
    python install_deps.py --check    # 仅检查依赖状态

依赖打包结构 (vendor/py/):
    common/   - py3-none-any 通用 wheel + PyExecJS sdist (跨平台共用)
    win/      - charset_normalizer 平台 wheel (win_amd64 / win_arm64)
    mac/      - charset_normalizer 平台 wheel (macosx universal2)
    linux/    - charset_normalizer 平台 wheel (manylinux x86_64 / aarch64)
"""
import os
import subprocess
import sys
import platform
import shutil

# Windows GBK 控制台 emoji 兼容
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(SKILL_DIR, "vendor", "py")
REQS = os.path.join(SKILL_DIR, "requirements.txt")


def detect_platform():
    """返回 (vendor_platform_dir, 说明) 或 None(无匹配平台目录)"""
    sysname = sys.platform
    machine = platform.machine().lower()  # x86_64 / arm64 / aarch64 / amd64
    pyver = f"cp{sys.version_info.major}{sys.version_info.minor}"

    if sysname == "win32":
        arch = "arm64" if machine in ("arm64", "aarch64") else "x86_64"
        pdir = os.path.join(VENDOR, "win", f"{pyver}-{arch}")
        return (pdir, f"Windows {arch} / Python {pyver}")
    if sysname == "darwin":
        pdir = os.path.join(VENDOR, "mac", pyver)
        return (pdir, f"macOS {machine} / Python {pyver} (universal2)")
    if sysname.startswith("linux"):
        arch = "aarch64" if machine in ("arm64", "aarch64") else "x86_64"
        pdir = os.path.join(VENDOR, "linux", f"{pyver}-{arch}")
        return (pdir, f"Linux {arch} / Python {pyver}")
    return (None, f"{sysname} {machine} / Python {pyver}")


def find_python():
    """当前解释器; 若为 venv 则用之"""
    return sys.executable


def run(cmd, desc):
    print(f"[install] {desc} ...")
    print(f"          {' '.join(cmd)}")
    r = subprocess.run(cmd)
    return r.returncode == 0


def install_offline(py, plat_dir, label):
    """离线安装: --no-index + find-links common + platform"""
    links = [os.path.join(VENDOR, "common")]
    if plat_dir and os.path.isdir(plat_dir):
        links.append(plat_dir)
    if not os.path.isdir(os.path.join(VENDOR, "common")):
        print("[install] vendor/py/common 不存在, 无法离线安装")
        return False
    cmd = [py, "-m", "pip", "install", "--no-index"]
    for l in links:
        cmd += ["--find-links", l]
    cmd += ["-r", REQS]
    return run(cmd, f"离线安装依赖 ({label})")


def install_online(py):
    return run([py, "-m", "pip", "install", "-r", REQS], "在线安装依赖")


def check_node():
    """检查 Node.js 与 crypto-js"""
    node = shutil.which("node")
    if not node:
        print("[check] [WARN]  未检测到 Node.js — 签名走 execjs 兜底, 但建议安装: https://nodejs.org/")
        return False
    try:
        r = subprocess.run([node, "-e",
                            "require('" + os.path.join(SKILL_DIR, "node_modules", "crypto-js").replace('\\', '/') + "'); console.log('crypto-js OK')"],
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            print(f"[check] [OK] Node.js {node}")
            print("[check] [OK] crypto-js 可加载")
            return True
        print("[check] [WARN]  crypto-js 缺失, 请运行: npm install")
        return False
    except Exception as e:
        print(f"[check] [WARN]  crypto-js 检查失败: {e}")
        return False


def check_imports():
    """检查 Python 依赖是否可导入"""
    missing = []
    for mod in ["requests", "loguru", "openpyxl", "execjs"]:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"[check] [FAIL] 缺失 Python 依赖: {', '.join(missing)}")
        return False
    print("[check] [OK] Python 依赖完整 (requests/loguru/openpyxl/execjs)")
    return True


def main():
    args = sys.argv[1:]
    force_online = "--online" in args
    only_check = "--check" in args

    plat_dir, label = detect_platform()
    if plat_dir is None:
        print(f"[install] 当前平台无预打包依赖: {label}")
        print("[install] 将使用在线安装")
    else:
        print(f"[install] 识别平台: {label}")
        print(f"[install] 平台依赖目录: {os.path.relpath(plat_dir, SKILL_DIR) if os.path.isdir(plat_dir) else '(缺失)'}")

    if only_check:
        check_imports()
        check_node()
        return 0 if (check_imports() or True) else 1

    py = find_python()

    ok = False
    if not force_online:
        ok = install_offline(py, plat_dir, label)
    if not ok:
        print("[install] 离线安装失败, 回退在线安装 ...")
        ok = install_online(py)

    check_imports()
    check_node()

    print()
    if ok:
        print("[install] [OK] 依赖安装完成")
    else:
        print("[install] [FAIL] 依赖安装失败, 请手动执行: pip install -r requirements.txt")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
