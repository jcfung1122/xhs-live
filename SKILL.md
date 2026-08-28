---
name: xhs-live
description: 小红书蒲公英直播达人邀约助手。搜索有直播计划的达人、获取联系方式、批量发送邀约、商家穿透（看同行）、导出 Excel 追踪报表。适用于品牌方/商家在小红书蒲公英平台进行 KOL 直播合作邀约。
trigger_words:
  - 搜达人
  - 搜索达人
  - 找kol
  - 直播达人
  - 邀约
  - 批量邀约
  - 发邀约
  - 群发
  - 穿透商家
  - 看同行
  - 商家详情
  - 导出Excel
  - 邀约报表
  - cookie过期
  - 蒲公英
  - 重新登录蒲公英
---

# 小红书蒲公英直播达人邀约技能 (xhs-live)

## 概述

把「打开蒲公英网页 → 翻页找达人 → 逐个点邀约 → 手动复制粘贴到 Excel」这个痛苦流程变成一句话的事。

**核心能力**:
- 按昵称精确搜索达人（与邀约页同款）
- 达人完整画像（概览/类目/店铺/商品/粉丝/直播表现）
- 7 维达人筛选（标准见 reference/）
- 批量发送直播合作邀约（自动获取联系方式、控制频率）
- **商家穿透（看同行）**：商家商品 + 合作达人
- Excel 读写（搜索结果导出、邀约追踪表、报表生成）

---

## 首次使用初始化（强制）

安装后第一次使用，**必须先询问用户以下配置**（通过 `python init_skill.py` 或填写 `workspace/config.json`）：

| # | 配置项 | 说明 |
|---|--------|------|
| 1 | 品牌名 | 邀约留言中的品牌称呼 |
| 2 | 主营品类 | 如：箱包 |
| 3 | 平台类目名 | 蒲公英平台的类目全名（如：箱包皮具/热销女包/男包） |
| 4 | 产品价格带 | 用于品类匹配判断（如：500-2000） |
| 5 | 佣金上下限 | 默认 25-35% |
| 6 | 筛选阈值 | 粉丝/观看/销售/活跃率/下单率/客单价/GPM |
| 7 | 留言模板 | 邀约留言内容 |
| 8 | 联系方式 | 联系人/电话/微信 |

**未初始化时调用核心方法会抛出 `SkillNotInitializedError` 并引导初始化**。

### Cookie 配置

复制 `pgy_cookies.json.example` 为 `pgy_cookies.json`，从浏览器 F12 获取：
- 至少：`a1`、`webId`、`gid`
- 邀约需：`_seller_id`（卖家店铺ID）、`_brand_user_id`（品牌账号ID）

---

## 六大工作模式

### 模式 1: 搜索达人

**触发词**: `搜` `搜索` `找达人` `找kol` `直播达人`

流程:
1. 确认搜索条件（昵称 / 品类 / 日期 / 粉丝数）
2. 按昵称精确搜索：`search_kols_by_name(name)`（邀约页同款）
3. 或按条件搜索：`search_live_plan_kols(tags, dates, min_fans)`
4. 展示摘要表格（序号 + 昵称 + 粉丝数 + 城市 + 场均观看 + 场均销售）
5. JSON 保存到 `workspace/results/search/`

### 模式 2: 7 维筛选

**标准**：`reference/7维达人筛选标准.md`（权威版本）

基础筛选（搜索后立即执行）:
- 粉丝 ≥ 50,000 / 场均观看 ≥ 5,000 / 场均销售额 ≥ 10,000

7 维指标（get_user_detail）:
- 活跃粉丝率 ≥ 50% / 下单粉丝率 ≥ 20% / 客单价 500~5,000 / GPM ≥ 5,000
- **客单价豁免规则**：客单价 > 5,000 时，若实际价格带与 500~2,000 有交集则豁免

**筛选阈值必须让用户设定或确认，不自行决定**（参考 `memory/feedback-filter-dimensions.md`）。

### 模式 3: 批量邀约

**触发词**: `邀约` `邀请` `发邀约` `批量邀约` `群发`

流程:
1. 确定目标达人（搜索结果 / 用户指定 / Excel 导入）
2. 收集邀约信息（留言模板、佣金 — 默认取 config.json 配置）
3. **展示确认清单** — 达人数 + 名单 + 留言 + 佣金 + 预计耗时
4. 用户确认后执行 `batch_invite()`
5. 打印结果表格（OK/FAIL/SKIP），JSON 落盘 + Excel 追加追踪表

### 模式 4: 商家穿透（看同行）— 两段式 ⭐

**触发词**: `穿透商家` `看同行` `商家详情`

**交互状态机**（重要：不要自动穿透）：

```
① 用户:「搜达人 XXX」
   → 反馈达人信息表（基础信息 + 7维 + 类目 + 店铺Top + 商品Top）
   → 询问:「是否要穿透某家合作商家？(可指定店铺名或从列表选择)」

② 用户:「穿透 XX旗舰店」
   → 执行穿透 get_seller_full_view(seller_id)
   → 返回完整商家情况表格（见下）
```

**商家情况表格标准格式**:

| 区块 | 内容 |
|------|------|
| 商家基本信息 | 店名 / seller_id / 主营 / 联系方式(微信·电话) / 店铺URL |
| 商家商品 Top10 | 商品名 / 价格 / 销售额 / 合作达人数量 / 佣金率 |
| 商家合作达人 Top10 | 昵称 / 粉丝 / 场均销售 / 与店合作销售额 / 合作商品数 |
| 与当前达人的关系 | 该达人在此店的排名 / 合作销售额 / 合作商品数 |
| 结论建议 | 是否值得合作 / 竞品对比 / 谈判参考 |

```python
# 商家穿透 API
products = skill.get_seller_products(seller_id)      # 商家商品（含 coo_buyer_num 合作达人数量）
buyers = skill.get_seller_coo_buyers(seller_id)      # 商家合作达人（画像+合作数据）
view = skill.get_seller_full_view(seller_id)          # 一键完整视角
url = skill.get_seller_shop_url(seller_id)            # https://www.xiaohongshu.com/shop/{seller_id}
```

### 模式 5: Excel 操作

**触发词**: `Excel` `导出` `报表` `追踪表` `导入`

用 openpyxl 读写，速查见 `reference/excel-cheatsheet.md`。

### 模式 6: 维护

**触发词**: `cookie` `登录` `过期` `配额`

- Cookie 过期 → 引导用户重新登录 https://pgy.xiaohongshu.com → F12 取 cookie
- 配额低 → 提醒用户
- **不自动操作** — 涉及登录/安全的步骤交给用户

---

## 安全规则（必须遵守）

### 规则 1: 搜索/查看 = 直接执行
搜达人、查联系方式、看配额、穿透商家 — 不用问，直接干。

### 规则 2: 发送邀约 = 必须先确认
批量邀约前**必须**展示确认清单（达人数 + 名单 + 留言 + 佣金 + 预计耗时），用户明确确认后才执行。
**绝不**在用户确认前调用 `batch_invite()` 或 `invite_single()`。

### 规则 3: 商家穿透 = 两段式
反馈达人信息后**不自动穿透**，先询问用户是否穿透、穿透哪家商家。

### 规则 4: Cookie 过期 = 引导用户
`CookieExpiredError` → 引导重新登录，**不要**尝试浏览器自动化登录。

### 规则 5: 每次操作后必落盘
- 搜索结果 → JSON 保存 `workspace/results/search/`
- 邀约结果 → JSON 保存 `workspace/results/invites/` + Excel 追加追踪表

### 规则 6: 筛选阈值让用户设定
数据维度阈值是业务决策，列出维度让用户设阈值，不自行决定。

---

## Python 调用方式

```python
import sys, os
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SKILL_DIR)

from pgy_live_skill import (
    PgyLiveSkill, CookieExpiredError, SkillNotInitializedError,
    quick_invite, get_skill_dir, get_default_cookie_path, get_workspace_dir,
)

skill = PgyLiveSkill(cookie_file=get_default_cookie_path())

# 按昵称搜索
kols = skill.search_kols_by_name('达人昵称')

# 达人画像
detail = skill.get_kol_detail(kol_id)
shops = skill.get_kol_cooperation_shops_web(kol_id)
goods = skill.get_kol_cooperation_goods_web(kol_id)

# 商家穿透
view = skill.get_seller_full_view(seller_id)

# 批量邀约（需先确认）
results = skill.batch_invite(kols=top_10, message=skill.default_message)
skill.print_table(results)
```

## 常用方法一览

| 方法 | 用途 | 来源 API |
|------|------|----------|
| `search_live_plan_kols()` | 搜有直播计划的达人（品类+日期过滤） | Draco |
| `search_kols_by_name()` | 按昵称精确搜索 | Draco |
| `get_contact(kol_id)` | 获取达人联系方式 | Draco |
| `get_kol_detail(kol_id)` | 达人概览详情 | Draco |
| `get_kol_cooperation_categories(kol_id)` | 合作品类分析 | Draco |
| `get_kol_shops(kol_id)` | 合作店铺清单 | Draco |
| `get_kol_products(kol_id)` | 合作商品数据 | Draco |
| `get_kol_fans(kol_id)` | 粉丝数据 | Draco |
| `get_kol_full_profile(kol_id)` | 一键达人完整画像 | Draco |
| `get_kol_cooperative_sellers(kol_id)` | 达人合作商家穿透（商家+联系方式+代表商品） | Draco |
| `get_kol_commerce_transformation(kol_id)` | 电商转化力（网页口径） | Draco |
| `get_kol_cooperation_shops_web(kol_id)` | 合作店铺（网页口径） | Draco |
| `get_kol_cooperation_goods_web(kol_id)` | 合作商品（网页口径） | Draco |
| `get_kol_cooperation_category_web(kol_id)` | 合作类目（网页口径） | Draco |
| `get_seller_products(seller_id)` | 商家商品列表（看同行） | Draco |
| `get_seller_coo_buyers(seller_id)` | 商家合作达人列表（看同行） | Draco |
| `get_seller_full_view(seller_id)` | 商家完整视角（商品+达人+店铺链接） | Draco |
| `get_seller_shop_url(seller_id)` | 商家店铺主页 URL | — |
| `get_contact_info(seller_id)` | 商家联系方式 | Draco |
| `check_permission(kol_id)` | 检查达人是否可邀约 | Draco |
| `invite_single(kol_id, msg, ...)` | 单人邀约 | Draco |
| `batch_invite(kols, msg, ...)` | 批量邀约 | Draco |
| `quick_invite(...)` | 一键搜索+邀约 | Draco |

字段全解见 `docs/api-fields-draco.md`（千帆）与 `docs/api-fields-solar.md`（蒲公英）。

## 执行注意事项

- 路径用正斜杠 `/` 或双反斜杠 `\\`
- 长脚本写到临时 `.py` 文件再执行，避免 bash 引号地狱
- 输出中文用 `json.dumps(..., ensure_ascii=False)`
- 邀约配额约 50 次/天，注意配额管理
- 频率控制默认 2 秒间隔，不建议修改
- Cookie 约 24 小时过期，需定期更新

## 常见问题

**Q: Cookie 过期了怎么办?**
A: 打开 https://pgy.xiaohongshu.com 重新登录 → F12 → Application → Cookies → 更新 pgy_cookies.json

**Q: 提示未初始化?**
A: 运行 `python init_skill.py` 完成品牌/佣金/阈值配置

**Q: 怎么知道达人有没有共享联系方式?**
A: `get_contact()` 返回空 `{}` 表示未共享

**Q: SKIP 状态是什么意思?**
A: 达人不可邀约（已在邀约中 / 不接受新合作 / 配额耗尽），详细规则见 `reference/邀约状态判断规则.md`
