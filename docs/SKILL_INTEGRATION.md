# xhs-live — Agent 集成指南

## 技能位置

**技能包根目录**：克隆仓库后任意位置（如 `D:\xhs-live\`）。

## Agent 使用方式

任何 AI Agent 在被触发后，设置 `sys.path` 指向技能包根目录即可导入：

```python
import sys, os
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SKILL_DIR)
from pgy_live_skill import PgyLiveSkill, CookieExpiredError, SkillNotInitializedError, get_default_cookie_path
```

## 初始化（两步）

### 1. 依赖安装（自动识别系统）

```bash
python install_deps.py   # 离线优先: vendor/py（common+win+mac+linux）
npm install              # crypto-js（已随仓库打包, 一般无需执行）
```

### 2. 配置

```bash
cp pgy_cookies.json.example pgy_cookies.json   # 填入浏览器 Cookie
python init_skill.py                             # 交互式品牌配置
```

## 常用操作

### 1. 搜索达人

```python
kols = skill.search_kols_by_name('达人昵称')
kols = skill.search_live_plan_kols(tags=['你的品类'], live_plan_start='20260701', live_plan_end='20260731')
```

### 2. 达人画像

```python
detail = skill.get_kol_detail(kol_id)
shops = skill.get_kol_cooperation_shops_web(kol_id)
goods = skill.get_kol_cooperation_goods_web(kol_id)
cats = skill.get_kol_cooperation_category_web(kol_id)
```

### 3. 商家穿透（看同行）

```python
view = skill.get_seller_full_view(seller_id)
# view = {seller_id, shop_url, products: {total, products}, coo_buyers: {total, buyers}}
```

### 4. 批量邀约（先确认）

```python
results = skill.batch_invite(kols=top_kols, message=skill.default_message)
skill.print_table(results)
```

## Cookie 过期处理

错误码 -100 / 401 → 引导用户重新登录 https://pgy.xiaohongshu.com

## 判断标准

`reference/` 目录：7维达人筛选标准 / 邀约状态判断规则 / 执行方案 / 指标意义 / 商家应用指南 / Excel速查。
