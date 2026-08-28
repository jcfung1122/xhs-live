# xhs-live — 小红书蒲公英直播达人邀约助手

把「打开蒲公英网页 → 翻页找达人 → 逐个点邀约 → 手动复制粘贴到 Excel」这个流程，
变成一句 Python 调用。支持：达人搜索、7维筛选、批量邀约、**商家穿透（看同行）**、Excel 报表。

## 功能

- **达人搜索**：按昵称精确搜索、按品类/直播日期/粉丝数过滤（与蒲公英邀约页同款逻辑）
- **达人画像**：概览详情、电商转化力、合作类目、合作店铺、合作商品、粉丝画像、直播表现
- **7 维筛选**：粉丝/观看/销售额 + 活跃率/下单率/客单价/GPM（标准见 `reference/`）
- **批量邀约**：自动获取联系方式、检查邀约权限、控制频率、配置佣金
- **商家穿透（看同行）**：从任意商家出发，获取其全部商品（含合作达人数量/佣金率）与全部合作达人
- **Excel 追踪**：搜索结果导出、邀约记录追加、追踪表维护
- **Cookie 管理**：过期自动检测（-100/401），引导重新登录

## 目录结构

```
xhs-live/
├── SKILL.md                  ← 技能主文档（Agent 入口）
├── README.md                 ← 本文件
├── pgy_live_skill.py         ← 核心 Python 模块
├── init_skill.py             ← 首次使用初始化引导（交互式）
├── install_deps.py           ← 跨平台依赖安装器（离线优先）
├── requirements.txt          ← Python 依赖声明
├── package.json              ← Node 依赖声明
├── bridge_sign.js            ← Node 签名桥接（XS 签名）
├── vendor/py/                ← 打包的 Python 依赖（common + win + mac + linux）
├── node_modules/crypto-js/   ← 打包的 Node 依赖
├── xhs_utils/                ← 工具模块（cookie/http/签名）
├── apis/                     ← API 封装（Draco 千帆 + Solar 蒲公英）
├── static/                   ← JS 签名文件
├── reference/                ← 判断标准（7维筛选/邀约状态/指标意义等）
├── workspace/                ← 运行时工作区（配置/结果/追踪表，个人数据不入库）
├── agent/                    ← Agent 定义
├── memory/                   ← 持久记忆
└── docs/                     ← API 字段参考与集成指南
```

## 安装

### 1. 克隆

```bash
git clone https://github.com/<你的账号>/xhs-live.git
cd xhs-live
```

### 2. 安装依赖（自动识别系统：Windows / macOS / Linux）

```bash
# 方式一：一键脚本（推荐）
python install_deps.py        # Windows 可运行 install.bat

# 方式二：手动
pip install -r requirements.txt   # Python 依赖（离线优先: vendor/py）
npm install                       # Node 依赖 (crypto-js)
```

> 依赖已按平台打包在 `vendor/py/`（common 通用 + win/mac/linux 平台 wheel），
`install_deps.py` 自动识别当前系统与 Python 版本，离线安装优先，失败回退在线。
> 需要系统已安装 **Node.js**（用于 XS 签名；缺失时自动回退 PyExecJS）。

### 3. 配置 Cookie

1. 登录 [蒲公英平台](https://pgy.xiaohongshu.com)，F12 → Application → Cookies
2. 复制模板并填写：

```bash
cp pgy_cookies.json.example pgy_cookies.json
```

至少填入 `a1`、`webId`、`gid`；发送邀约还需 `_seller_id` 与 `_brand_user_id`（下划线开头，仅作配置不发送）。

### 4. 初始化品牌配置

```bash
python init_skill.py     # 交互式询问品牌/品类/佣金/筛选阈值/留言/联系方式
```

或手动复制 `workspace/config.example.json` 为 `workspace/config.json` 填写。
**未初始化时调用核心方法会提示先初始化**。

## 快速开始

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pgy_live_skill import PgyLiveSkill, get_default_cookie_path

skill = PgyLiveSkill(cookie_file=get_default_cookie_path())

# 1. 按昵称精确搜索达人（邀约页同款）
kols = skill.search_kols_by_name('达人昵称')

# 2. 达人完整画像
detail = skill.get_kol_detail(kol_id)
shops = skill.get_kol_cooperation_shops_web(kol_id)
goods = skill.get_kol_cooperation_goods_web(kol_id)

# 3. 商家穿透（看同行）—— 商家商品 + 合作达人
products = skill.get_seller_products(seller_id)
buyers = skill.get_seller_coo_buyers(seller_id)

# 4. 批量邀约（发送前必须先人工确认名单和留言）
results = skill.batch_invite(kols=kols[:10], message=skill.default_message)
skill.print_table(results)
```

## 商家穿透（看同行）

两段式交互：

```
① 搜达人 → 反馈达人信息表（基础+7维+类目+店铺Top+商品Top）
② 用户指定要穿透的商家 → 执行穿透 → 返回完整商家情况表格
```

商家情况表格包含：商家基本信息（联系方式/店铺URL）/ 商品Top10 / 合作达人Top10 / 与当前达人的关系 / 结论建议。

## API 方法速查

| 方法 | 用途 | 数据源 |
|------|------|--------|
| `search_live_plan_kols()` | 搜有直播计划的达人 | Draco |
| `search_kols_by_name()` | 按昵称精确搜索 | Draco |
| `get_kol_detail()` | 达人概览详情 | Draco |
| `get_kol_commerce_transformation()` | 电商转化力 | Draco |
| `get_kol_cooperation_shops_web()` | 合作店铺（网页口径） | Draco |
| `get_kol_cooperation_goods_web()` | 合作商品（网页口径） | Draco |
| `get_kol_cooperation_category_web()` | 合作类目 | Draco |
| `get_kol_full_profile()` | 一键达人画像 | Draco |
| `get_kol_cooperative_sellers()` | 达人合作商家穿透 | Draco |
| `get_seller_products()` | 商家商品列表 | Draco |
| `get_seller_coo_buyers()` | 商家合作达人 | Draco |
| `get_seller_full_view()` | 商家完整视角 | Draco |
| `get_seller_shop_url()` | 商家店铺主页 URL | — |
| `get_contact()` / `get_contact_info()` | 达人/商家联系方式 | Draco |
| `check_permission()` | 检查是否可邀约 | Draco |
| `batch_invite()` | 批量邀约 | Draco |
| `quick_invite()` | 一键搜索+邀约 | Draco+Solar |

完整字段说明见 [docs/api-fields-draco.md](docs/api-fields-draco.md) 与 [docs/api-fields-solar.md](docs/api-fields-solar.md)。

## 判断标准（reference/）

| 文件 | 内容 |
|------|------|
| `7维达人筛选标准.md` | 权威筛选标准（基础3维 + 4维指标 + 客单价豁免规则） |
| `邀约状态判断规则.md` | 邀约状态机（OK/SKIP/VERIFY/DEFERRED...） |
| `达人筛选与邀约执行方案.md` | 完整执行流程 |
| `指标意义分析.md` | GPM/客单价等指标深度解读 |
| `API数据商家应用指南.md` | 商家视角的数据应用 |
| `excel-cheatsheet.md` | Excel 操作速查 |

## 安全与隐私

- `pgy_cookies.json`、`workspace/config.json`、`workspace/_state.json`、测试数据均不入库（.gitignore）
- 代码不硬编码任何账号 ID/品牌信息，全部通过配置提供
- 邀约前必须人工确认名单与留言（安全规则见 SKILL.md）
- `vendor/py/` 与 `node_modules/crypto-js/` 为打包的依赖，保证离线安装

## 免责声明

本项目仅供学习与技术研究使用。使用前请自行确认行为符合小红书平台服务条款及相关法律法规，
请勿用于骚扰性群发或其他违规用途。`static/` 下的签名 JS 取自公开网页资源，版权归原权利人所有。

## License

MIT
