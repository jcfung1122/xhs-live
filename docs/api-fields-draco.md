# 千帆（Draco）API 返回字段全解

> 数据来源：真实调用 pgy.xiaohongshu.com 的 /api/draco/* 端点（Cookie 有效）。
> 示例数据：某女装直播达人（字段值仅为格式示例）。
> 生成时间：2026-08-28。字段值来自真实响应，可直接对照。

---

## 一、达人概览详情 get_user_detail

**端点**：POST /api/draco/distributor-square/distributor/detail/overview/v2
**请求体**：`{"buyer_id": "...", "date_type": 2}`（date_type: 1=近7天, 2=近30天, 3=近90天）

### 顶层

| 字段 | 值 | 说明 |
|---|---|---|
| code | 0 | 状态码（0=成功） |
| success | true | 是否成功 |
| msg | 成功 | 消息文本 |

### data.buyer_overview_info（达人概览信息）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| total_sales | 2399489.93 | 总销售额（元） |
| number_of_oromoted_products | 280 | 推广商品数（平台拼写或为 oromoted，原样保留） |
| number_of_partner_seller | 122 | 合作品牌数（曾合作过的商家数） |
| new_fans_num | 106 | 新增粉丝数 |
| over_buyer_for_proportion_of_order_fans | 0.8308 | 下单粉丝占比超越 83.08% 的达人（0-1） |
| average_view_time | 42155 | 平均观看时长（秒） |
| over_total_sales_buyers | 0.9642 | 总销售额超越 96.42% 的达人 |
| live_gpm | 23185.94 | 千次观看成交金额 GPM（元） |
| interaction_rate | 0.0611 | 互动率 6.11%（赞藏评/播放） |
| over_live_gpm_buyers | 0.9801 | GPM 超越 98.01% 的达人 |
| fans_num | 250335 | 粉丝数 |
| proportion_of_active_fans | 0.8498 | 活跃粉丝占比 84.98% |
| proportion_of_order_fans | 0.6205 | 下单粉丝占比 62.05% |
| fan_unit_price | 4104.40 | 粉丝单价（元/粉，即场均销售额/粉丝数估算） |
| live_days | 2 | 直播天数 |
| live_count | 2 | 直播场次 |
| view_middle_count | 24631 | 场均观看人数 |
| average_sales | 1199744.96 | 场均销售额（元） |
| over_average_sales_buyers | 0.9934 | 场均销售额超越 99.34% 的达人 |
| over_buyer_for_proportion_of_active_fans | 0.2408 | 活跃粉丝占比超越 24.08% 的达人 |
| max_online_viewer | 382 | 最高在线人数 |
| show_data | 1 | 是否展示数据（1=展示，0=隐藏） |

---

## 二、达人合作品类分析 get_user_cooperation

**端点**：POST /api/draco/distributor-square/distributor/cooperative/category/v2
**请求体**：`{"buyer_id", "first_live_category": "", "second_live_category": "", "date_type": 2, "page": 1, "size": 10}`

### data.buyer_coo_categories_analysis_infos[]（合作品类列表，每项）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| first_category_name | 女装/女士精品 | 一级品类名 |
| second_category_name | 连衣裙 | 二级品类名 |
| avg_price | 1071.03 | 该品类平均客单价（元） |
| sale_amount | 352369.5 | 该品类销售额（元） |
| refer_commission_rate | 25 | 参考佣金率（%） |
| show_data | 1 | 是否展示数据 |

### 顶层

| 字段 | 值 | 说明 |
|---|---|---|
| data.total | 43 | 达人合作过的品类总数 |

---

## 三、达人合作店铺清单 get_user_shop ⭐（达人→商家 核心链路）

**端点**：POST /api/draco/distributor-square/distributor/cooperative/shop/v2
**请求体**：`{"buyer_id", "first_live_category": "", "second_live_category": "", "date_type": 2, "page": 1, "size": 20}`

### data.buyer_coo_shop_analysis_infos[]（合作店铺列表，每项）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| shop_name | Mesosph旗舰店 | 店铺名称 |
| seller_id | 65604c269665fd00016db262 | **商家ID（查商家详情的钥匙）** |
| seller_uid | 63f0fe6f000000001001f3cb | 商家用户ID（小红书用户体系） |
| main_category_name | 女装/女士精品 | 店铺主营品类 |
| avg_price | 695.40 | 该店铺平均客单价（元） |
| sale_amount | 265641 | 该店铺合作销售额（元） |
| num_of_promoted_products | 8 | 该店铺推广商品数 |
| show_data | 1 | 是否展示数据 |

### 顶层

| 字段 | 值 | 说明 |
|---|---|---|
| data.total | 113 | 达人合作过的店铺总数 |

**意义**：这是"达人 → 合作商家"的唯一入口。拿到 `seller_id` 后可继续向下探索商家详情/商品/联系方式。

---

## 四、达人合作商品数据 get_user_item

**端点**：POST /api/draco/distributor-square/distributor/cooperative/item/v2
**请求体**：`{"buyer_id", "first_live_category": "", "second_live_category": "", "date_type": 2, "page": 1, "size": 20}`

### data.buyer_coo_product_analysis_infos[]（合作商品列表，每项）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| prodcut_name | To me 系列 春夏奶油白法式吊带衫... | 商品名称（平台拼写为 prodcut，原样保留） |
| product_id | 698b49dea60bac00016e74a0 | 商品ID |
| sku_id | 698b49dea60bac00016e74a1 | SKU ID（下单粒度） |
| shop_name | Carmen says旗舰店 | 所属店铺名 |
| seller_id | 67b20f272891460015b01a9f | 商家ID |
| seller_uid | 5ecbd5b30000000001004835 | 商家用户ID |
| price | 880 | 商品价格（元） |
| sales | 88828 | 销售额（元） |
| live_count | 2 | 直播场次 |
| product_cover | //qimg.xiaohongshu.com/... | 商品封面图 URL（需补 https:） |
| show_data | 1 | 是否展示数据 |

### 顶层

| 字段 | 值 | 说明 |
|---|---|---|
| data.total | 225 | 达人合作商品总数 |

**意义**：商品与店铺通过 `seller_id` 关联，可交叉验证商家的经营数据。

---

## 五、达人粉丝数据 get_user_fans

**端点**：GET /api/draco/distributor-square/distribuitor/detail/fans
**参数**：`distributor_id`, `date_type=2`

### data.fans_data_info（粉丝核心指标）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| active_fans_rate | 0.85 | 活跃粉丝率 85% |
| engage_fans_rate | 0.026 | 互动粉丝率 2.6% |
| order_fans_rate | 0.621 | 下单粉丝率 62.1% |
| fans_num | 250335 | 粉丝总数 |
| fans_increse_num | 106 | 新增粉丝数 |

### data.age_distribution_info[]（年龄分布）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| name | 25-34 | 年龄段 |
| value | 65.3% | 占比（字符串） |

### data.sex_distribution_info[]（性别分布）

| name | value |
|---|---|
| 女 | 94.6% |
| 男 | 5.4% |

### data.province_distribution_info[] / data.city_distribution_info[]（地域分布）

| name | value |
|---|---|
| 上海（城市）/ 浙江（省份） | 6.0% / 11.5% |

### data.hobby_distribution_info[]（兴趣分布）

| name | value |
|---|---|
| 时尚 | 14.6% |
| 娱乐 | 12.8% |
| ... | ... |

---

## 六、商家搜索 search_sellers（看同行）

**端点**：GET /api/draco/sellers/search
**参数**：`keyword`, `page`, `size`, `category?`

### data.sellers[]（商家列表，每项）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| sellerId | 6a90ed93ffe6ad0015dd5cc9 | 商家ID |
| sellerName | WEMAY箱包收纳的店 | 商家名称 |
| sellerAvatar | https://sns-avatar-qc.xhscdn.com/... | 商家头像 URL |

### 顶层

| 字段 | 值 | 说明 |
|---|---|---|
| data.total | 4214 | 搜索结果总数 |

**局限**：只返回 sellerId/sellerName/sellerAvatar，无经营数据。若需商家详情，需按 sellerId 探索其它端点。

---

## 七、邀约权限 get_kol_invite_permission

**端点**：GET /api/draco/invite/kols/{kol_id}/permissions

### data

| 字段 | 值（示例） | 说明 |
|---|---|---|
| permission_type | 0 / 2 | **0=可邀约；2=直播邀约已发出待博主处理**；1=？（不可邀约） |
| hint | 直播邀约已发出，正待博主处理 | 状态提示文案 |

---

## 八、上次邀约信息 get_last_invite_info

**端点**：GET /api/draco/distribution/seller_last_invite_info
**参数**：`current_buyer_id`, `alliance_new_invitation=true`

### data.invitation_info（上次邀约记录）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| invitation_id | 23203146 | 邀约ID |
| buyer_id | 5a58048611be105e0641e329 | 达人ID |
| buyer_nick | Gillianss | 达人昵称 |
| buyer_avatar | https://... | 达人头像 |
| seller_id | 68b53ecfba7d6300155bd627 | 发起邀约的商家ID |
| status | 0 | 邀约状态（0=待处理/已发出） |
| created_at | 1787479901149 | 创建时间（毫秒时间戳） |
| message | 您好！我们是XX品牌... | 邀约留言内容 |

### data.item_infos[]（推荐商品，每项）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| item_id | 6a5cae994f6fde00017e577c | 商品ID |
| name | 【金小妹专属】头层牛皮托特包... | 商品名称 |
| image | https://qimg... | 商品图 URL |
| price_min / price_max | 799.00 / 799.00 | 价格区间（元，字符串） |
| stock | 1511 | 库存 |
| valid_distributor_rate | 20.0 | 有效佣金率（%） |
| buyable | true | 是否可购买 |
| buyer_hot_sale | true | 是否达人热卖款 |
| potential_item | false | 是否潜力商品 |
| trending_product | false | 是否趋势商品 |
| channel_item | false | 是否渠道专供品 |
| carriage_insurance | false | 是否含运费险 |
| category_ids | [...] | 所属品类ID列表 |
| buyer_match_info.main_purchasing_crows | [] | 匹配的主要购买人群 |
| buyer_match_info.match_buyer | false | 是否匹配当前买家 |

---

## 九、达人联系方式 get_kol_contact_info

**端点**：POST /api/draco/selection-center/contact/info/query
**请求体**：`{"source": "BUYER_CONTACT_INFO", "buyer_id": kol_id, "source_page": "/solar/pre-trade/live/kol"}`

### data.contact_info（达人联系方式）

| 字段 | 值（示例） | 说明 |
|---|---|---|
| tel | 15868175809 | 手机号（达人已共享才返回） |
| wechat | 15868175809 | 微信号（达人已共享才返回） |

---

## 十、品类树 get_all_categories

**端点**：GET /api/draco/distributor-square/distributors-tags
**参数**：`types=content_category,distribution_category,user_design_tag,content_tag`

返回 43 个一级品类数组，每项：

| 字段 | 值（示例） | 说明 |
|---|---|---|
| first_category | 女装/女士精品 | 一级品类名 |
| second_category | [连衣裙, T恤, 裤子, ...] | 二级品类数组 |

**用途**：搜索达人/商家时的品类过滤参数来源（配合 search_live_kols 的 live_first_category / live_second_category）。

---

## 十一、商家自身信息 get_seller_info

**端点**：POST /api/draco/sellers/info
**请求体**：`{"basic_info": {"contact_info": {"contact_person_list": []}}, "brand_info": {"uploader_info": {"product_manual": {}}}}`

**实测返回**：仅 `{"code": 0, "success": true, "msg": "成功"}` —— 当前账号未配置商家资料时返回空。
**预期**：返回当前登录账号（商家侧）的店铺名、seller_id、联系人等。**这是"自己"的商家信息，不是任意商家详情。**

---

> 未完：蒲公英（Solar）端点字段说明 + 商家详情端点探索见下一节。
