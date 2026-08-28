# 蒲公英（Solar）API 返回字段全解

> 数据来源：真实调用 pgy.xiaohongshu.com 的 /api/solar/* 端点。
> 示例数据：某直播达人（字段值仅为格式示例）。
> 说明：Solar 为「蒲公英合作平台」侧 API（笔记/达人数据），Draco 为「直播分销」侧 API（见 api-fields-draco.md）。

---

## 一、内容标签树 get_all_categories

**端点**：GET /api/solar/cooperator/content/tag_tree

返回**一级标签数组**（无 data 包装，直接是数组）：

| 字段 | 值（示例） | 说明 |
|---|---|---|
| taxonomy1Tag | 美妆 | 一级标签名 |
| taxonomy2Tags | [整体妆容, 唇妆, 眼妆, ...] | 二级标签数组 |

**用途**：搜索达人时的内容标签（contentTag）参数来源，如搜「箱包」用 `时尚 → 箱包`。

---

## 二、商家/账号自身信息 get_self_info

**端点**：GET /api/solar/user/info

| 字段 | 值（示例） | 说明 |
|---|---|---|
| code | -100 | 状态码（-100=无登录信息） |
| success | false | 是否成功 |
| msg | 无登录信息 | 消息 |
| data | {} | 用户信息（userId/nickName 等，需登录态） |

**⚠️ 实测**：当前 Cookie 在 Draco 侧有效，但 **Solar 侧返回 -100 无登录信息**。原因：Solar 接口使用独立的登录会话（`access-token-solar...` 或 `x-user-id-solar...` Cookie），当前 pgy_cookies.json 缺 Solar 专属登录字段。
**影响**：`send_invite`（笔记邀约）、`get_user_by_page`、`search_kols` 的 brandUserId 自动获取依赖此接口；但 `search_kols` 已支持从 `x-user-id-pgy.xiaohongshu.com` 兜底读取，仍可用。

---

## 三、达人数据摘要 get_user_detail

**端点**：GET /api/solar/kol/dataV3/dataSummary
**参数**：`userId`, `business=0`

### data（达人数据摘要）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| dateKey | 2026-08-27 | 数据日期 |
| noteNumber | 6 | 近 30 天笔记数 |
| noteType | [{contentTag: 时尚, percent: 50.0}, ...] | 笔记内容类型占比 |
| tradeNames | [] | 商业合作类目 |
| readMedian | 11343 | 笔记阅读中位数 |
| readMedianBeyondRate | 80.4 | 阅读中位数超越 80.4% 博主 |
| interactionMedian | 523 | 互动中位数（赞藏评） |
| interactionBeyondRate | 74.5 | 互动中位数超越 74.5% 博主 |
| activeDayInLast7 | 7 | 近 7 天活跃天数 |
| isActive | true | 是否活跃 |
| responseRate | 2.2 | 回复率 2.2% |
| inviteNum | 2240 | 被邀请次数 |
| easyConnect | false | 是否易沟通（响应快） |
| pictureReadCost | 0.0 | 图文笔记阅读成本（元） |
| pictureReadBeyondRate | 72.4 | 图文阅读成本超越 72.4% 博主 |
| videoReadCost | 361.6 | 视频笔记阅读成本（元） |
| videoReadBeyondRate | 40.0 | 视频阅读成本超越 40% 博主 |
| fans30GrowthRate | -0.2 | 30 天粉丝增长率 -0.2% |
| fans30GrowthBeyondRate | 30.3 | 粉丝增速超越 30.3% 博主 |
| mengagementNum / mEngagementNum | 606 | 月互动数（两字段同值） |

---

## 四、达人粉丝摘要 get_user_fans_detail

**端点**：GET /api/solar/kol/dataV3/fansSummary
**参数**：`userId`

### data（粉丝摘要）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| fansNum | 250335 | 粉丝总数 |
| fansIncreaseNum | -559 | 粉丝净增（可为负） |
| fansGrowthRate | -0.2 | 粉丝增长率（%） |
| fansGrowthBeyondRate | 30.3 | 增速超越 30.3% 博主 |
| activeFansL28 | 206012 | 近 28 天活跃粉丝数 |
| activeFansRate | 82.3 | 活跃粉丝率 82.3% |
| activeFansBeyondRate | 75.0 | 活跃率超越 75% 博主 |
| engageFansRate | 0.7 | 互动粉丝率 0.7% |
| engageFansL30 | 1765 | 近 30 天互动粉丝数 |
| engageFansBeyondRate | 60.6 | 互动率超越 60.6% 博主 |
| readFansIn30 | 29702 | 近 30 天阅读粉丝数 |
| readFansRate | 11.9 | 阅读粉丝率 11.9% |
| readFansBeyondRate | 70.7 | 阅读率超越 70.7% 博主 |
| payFansUserRate30d | 45.4 | 近 30 天下单粉丝率 45.4% |
| payFansUserNum30d | 113708 | 近 30 天下单粉丝数 |

---

## 五、粉丝历史趋势 get_user_fans_history

**端点**：GET /api/solar/kol/data/{userId}/fans_overall_new_history
**参数**：`dateType=1`, `increaseType=1`

### data

| 字段 | 值（示例） | 说明 |
|---|---|---|
| fansNumInc | -559 | 期间粉丝净增 |
| fansNumIncRate | -0.0022 | 期间粉丝净增率 |
| list[] | [...] | 每日粉丝数序列 |

### data.list[]（每日数据，按日期升序）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| num | 250894 | 当日粉丝总数 |
| dateKey | 2026-07-29 | 日期 |

**用途**：画粉丝增长曲线、判断涨粉/掉粉趋势。

---

## 六、达人笔记表现 get_user_notes_detail

**端点**：GET /api/solar/kol/dataV3/notesRate
**参数**：`userId`, `business=0`, `noteType=3`, `dateType=1`, `advertiseSwitch=1`

### data（笔记总体表现）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| noteNumber | 6 | 笔记数 |
| videoNoteNumber | 6 | 视频笔记数 |
| hundredLikePercent | 100.0 | 点赞过百笔记占比 100% |
| thousandLikePercent | 0.0 | 点赞过千笔记占比 0% |
| noteType | [{contentTag: 时尚, percent: 50.0}] | 笔记类型占比 |
| tradeNames | null | 商业类目 |
| impMedian | 71884 | 曝光中位数 |
| impMedianBeyondRate | 83.8 | 曝光超越 83.8% 博主 |
| readMedian | 11343 | 阅读中位数 |
| readMedianBeyondRate | 80.4 | 阅读超越 80.4% 博主 |
| interactionMedian | 523 | 互动中位数 |
| interactionRate | 5.0 | 互动率 5.0% |
| interactionBeyondRate | 74.5 | 互动超越 74.5% 博主 |
| likeMedian | 409 | 点赞中位数 |
| collectMedian | 77 | 收藏中位数 |
| commentMedian | 37 | 评论中位数 |
| shareMedian | 9 | 分享中位数 |
| videoFullViewRate | 4.8 | 视频完播率 4.8% |
| videoFullViewBeyondRate | 53.3 | 完播率超越 53.3% 博主 |
| picture3sViewRate | 0.0 | 图文 3 秒停留率 |
| notes[] | [...] | 单篇笔记明细 |

### data.notes[]（单篇笔记）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| noteId | 6a747b3c0000000028033ca7 | 笔记ID |
| publishTime | 2026-08-06 | 发布时间 |
| type | 2 | 笔记类型（2=视频） |
| imgUrl | http://ci.xiaohongshu.com/... | 封面图 |
| title | Recently🖤 | 标题 |
| canJump | true | 可跳转 |
| impNum | 82216 | 曝光数 |
| impBeyondRate | 0.143 | 曝光超越率（相对自身均值，可为负） |
| readNum | 15785 | 阅读数 |
| readBeyondRate | 0.391 | 阅读超越率 |
| interactionNum | 1021 | 互动数 |
| interactionBeyondRate | 0.952 | 互动超越率 |
| collectNum | 146 | 收藏数 |
| collectBeyondRate | 0.896 | 收藏超越率 |
| likeNum | 737 | 点赞数 |
| likeBeyondRate | 0.801 | 点赞超越率 |

---

## 七、达人搜索 search_kols

**端点**：POST /api/solar/cooperator/blogger/v2（需先调 /api/solar/cooperator/blogger/track 拿 trackId）

返回**达人数组**（search_kols 封装后）：

| 字段 | 值（示例） | 说明 |
|---|---|---|
| userId | 5a9cec454eacab62a279b25d | 达人用户ID |
| name | 赫蝎子 | 达人昵称 |
| fansNum | 207175 | 粉丝数 |
| kliveCnt30d | 4 | 近 30 天直播场次 |
| tradeType | 服装配饰 美妆个护 | 经营类目 |
| location | 广东 深圳 南山区 | 所在地 |
| avgLiveViewerNum | 8271.17 | 场均直播观看人数 |
| avgAgmv90d | 101696.7 | 近 90 天场均 GMV（元） |

---

## 八、达人搜索原始结构 get_user_by_page（底层）

**端点**：POST /api/solar/cooperator/blogger/v2（内部先调 get_track + get_self_info）

返回：`(user_list, total)`

### user_list[]（原始达人对象，含更多字段）

| 字段 | 说明 |
|---|---|
| userId | 达人用户ID |
| nickName | 昵称 |
| fansNum | 粉丝数 |
| kliveCnt30d | 近30天直播数 |
| avgLiveViewerNum | 场均观看 |
| avgAgmv90d | 近90天场均GMV |
| 等 | 与 search_kols 封装后字段一致 |

### total

| 字段 | 说明 |
|---|---|
| total | 匹配达人总数 |

---

> 补充：Solar 侧登录态（get_self_info 返回 -100）为当前已知限制。若需完整 Solar 能力（笔记邀约 send_invite、brandUserId 自动获取），需在 pgy_cookies.json 补充 Solar 专属登录 Cookie。
