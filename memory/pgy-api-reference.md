---
name: pgy-api-reference
description: 蒲公英 API 端点速查表
metadata:
  type: reference
---

# PGY API 速查

## Python 模块路径

```python
import sys, os
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))  # 或硬编码技能包根目录
sys.path.insert(0, _SKILL_DIR)
from pgy_live_skill import PgyLiveSkill, CookieExpiredError, quick_invite, get_default_cookie_path
```

## Cookie 文件

`<skill_dir>/pgy_cookies.json`（默认位置，可通过 `get_default_cookie_path()` 获取）

## 核心方法

| 方法 | 用途 | 来源 API |
|------|------|----------|
| `search_live_plan_kols()` | 搜有直播计划的达人 | Draco |
| `search_by_tags()` | 按标签搜达人 | Solar |
| `get_contact(kol_id)` | 获取联系方式 | Draco |
| `check_permission(kol_id)` | 检查是否可邀约 | Draco |
| `invite_single(kol_id, msg, ...)` | 单人邀约 | Draco |
| `batch_invite(kols, msg, ...)` | 批量邀约 | Draco |
| `quick_invite(cookie, tags, ...)` | 一键搜索+邀约 | Draco+Solar |

## 默认值

- Seller ID / Brand User ID: 账号私有信息，从 `pgy_cookies.json` 的 `_seller_id` /
  `_brand_user_id` 读取，或通过环境变量 `PGY_SELLER_ID` / `PGY_BRAND_USER_ID` 设置
- Commission: lower=25, higher=35
- Rate limit: 2.0s

## 返回结构

### search_live_plan_kols()
```python
[{
    'distributor_id': '...',
    'name': '达人昵称',
    'fans_num': 496854,
    'avg_live_viewer_num': '31027',
    'live_day_cnt': 22,
    'distribution_category': [{'first_category': '女装/女士精品', ...}],
    'city': '上海',
    'avg_sale_amount': '100w-200w',
}]
```

### batch_invite() 返回
```python
[{
    'name': '达人昵称',
    'fans': 496854,
    'contact': 'wechat:your_wechat_id, phone:13800000000',
    'date': '2026-06-18',
    'invite_id': '22064022',
    'status': 'OK'  # OK | FAIL: xxx | SKIP
}]
```

## Cookie 过期处理

错误码 -100 或 401 → 引导用户重新登录 https://pgy.xiaohongshu.com
