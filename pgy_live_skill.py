"""
蒲公英直播达人邀约技能 (Pugongying Live Invite Skill)
======================================================
独立可复用模块,供 Agent 调用。代码已适配为可安装到任意目录。

用法:
    import os, sys
    # 将本文件所在目录加入 sys.path (确保 xhs_utils/ apis/ static/ 可被导入)
    _SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _SKILL_DIR)

    from pgy_live_skill import PgyLiveSkill, CookieExpiredError, quick_invite, get_default_cookie_path

    # Cookie 文件默认位置: <skill_dir>/pgy_cookies.json
    skill = PgyLiveSkill(cookie_file=get_default_cookie_path())

    kols = skill.search_live_plan_kols(
        live_plan_start='20260701', live_plan_end='20260731',
        content_tags=['你的品类1', '你的品类2'], max_pages=10
    )

    results = skill.batch_invite(
        kols=kols[:10],
        message='您的邀约留言...',
        commission_lower=25, commission_higher=35
    )

    skill.print_table(results)

Cookie 管理:
    - 从文件加载 (cookie_file 参数; 默认查找本目录下的 pgy_cookies.json)
    - 自动检测过期 (API 返回 -100/401 时抛出 CookieExpiredError)
    - 用户更新后调用 update_cookies()
    - 没有 cookie 文件时: 复制 pgy_cookies.json.example 为 pgy_cookies.json 并填入值
"""
import os
os.environ.setdefault('NODE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules'))
import json, sys, time, os, random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xhs_utils.cookie_util import trans_cookies
from apis.xhs_qianfan_apis import QianFanAPI
from apis.xhs_pugongying_apis import PuGongYingAPI


# ============================================================
# 路径工具 (使技能包可安装到任意目录)
# ============================================================

_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


def get_skill_dir():
    """返回技能包根目录 (本文件所在目录)"""
    return _SKILL_DIR


def get_default_cookie_path():
    """返回默认 cookie 文件路径: <skill_dir>/pgy_cookies.json"""
    return os.path.join(_SKILL_DIR, 'pgy_cookies.json')


def get_workspace_dir():
    """返回默认工作区路径: <skill_dir>/workspace/"""
    return os.path.join(_SKILL_DIR, 'workspace')


class CookieExpiredError(Exception):
    """Cookie 已过期,需用户重新登录"""
    pass


class SkillNotInitializedError(Exception):
    """技能未初始化: 需要先运行 init_skill.py 或填写 workspace/config.json"""
    pass


class PgyLiveSkill:
    """蒲公英直播达人邀约技能"""

    ACTIVITY_LIVE_PLAN = '6a05d7f2e4b078c8db9e1ab8'
    # 账号私有信息不硬编码: 可从 pgy_cookies.json 的 _seller_id/_brand_user_id
    # 或环境变量 PGY_SELLER_ID / PGY_BRAND_USER_ID 读取
    DEFAULT_SELLER_ID = os.environ.get('PGY_SELLER_ID', '')
    DEFAULT_BRAND_USER_ID = os.environ.get('PGY_BRAND_USER_ID', '')

    def __init__(self, cookie_file=None, cookie_dict=None, seller_id=None, brand_user_id=None):
        self._cookie_file = cookie_file
        self._cookies = None
        self._qianfan = QianFanAPI()
        self._pgy = PuGongYingAPI()
        self._seller_id = seller_id or self.DEFAULT_SELLER_ID
        self._brand_user_id = brand_user_id or self.DEFAULT_BRAND_USER_ID
        self._config = self._load_config()

        if cookie_dict:
            self._cookies = cookie_dict
        elif cookie_file:
            self._load_cookies()

    def _load_config(self):
        """从 workspace/config.json 加载用户配置; 不存在返回 None"""
        try:
            cfg_path = os.path.join(_SKILL_DIR, 'workspace', 'config.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def get_config(self):
        """获取用户配置 (品牌/佣金/筛选阈值/留言模板)

        Raises:
            SkillNotInitializedError: 未初始化时
        """
        if self._config is None:
            raise SkillNotInitializedError(
                '技能未初始化: 请先运行 python init_skill.py '
                '或手动填写 workspace/config.json (参考 config.example.json)'
            )
        return self._config

    @property
    def brand_name(self):
        cfg = self.get_config()
        return cfg.get('brand', {}).get('name', '')

    @property
    def default_commission(self):
        cfg = self.get_config()
        return (cfg.get('commission', {}).get('lower', 25),
                cfg.get('commission', {}).get('higher', 35))

    @property
    def default_message(self):
        cfg = self.get_config()
        return cfg.get('message_template', '')

    # ============================================================
    # Cookie 管理
    # ============================================================

    def _load_cookies(self):
        if not self._cookie_file or not os.path.exists(self._cookie_file):
            raise FileNotFoundError(f'Cookie file not found: {self._cookie_file}')
        with open(self._cookie_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
        # 可选私有字段: 以下划线开头, 只作为配置读取, 不发送为 cookie
        if not self._seller_id:
            self._seller_id = d.pop('_seller_id', '')
        if not self._brand_user_id:
            self._brand_user_id = d.pop('_brand_user_id', '')
        cookie_pairs = [f'{k}={v}' for k, v in d.items()]
        self._cookies = trans_cookies('; '.join(cookie_pairs))

    def _check_response(self, resp, action='API call'):
        if resp is None:
            raise CookieExpiredError(f'{action}: no response')
        code = resp.get('code', 0)
        if code == -100 or code == 401:
            raise CookieExpiredError(
                f'{action}: Cookie expired (code={code}). '
                f'Please re-login at https://pgy.xiaohongshu.com '
                f'and update: {self._cookie_file}'
            )
        return resp

    @property
    def cookies(self):
        if self._cookies is None:
            self._load_cookies()
        return self._cookies

    def update_cookies(self, cookie_dict):
        """Update cookies after user re-login"""
        self._cookies = cookie_dict
        if self._cookie_file:
            with open(self._cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_dict, f, ensure_ascii=False, indent=2)
            print(f'Cookies saved to {self._cookie_file}')

    # ============================================================
    # 达人搜索
    # ============================================================

    # Category tag -> full API category name mapping (built lazily)
    _category_map = None  # {short_tag: full_first_category_name}
    _category_tree = None  # [{first_category: str, second_category: [str]}, ...]

    def _load_category_tree(self):
        """Load the Draco distribution category tree and build tag mapping.
        Called lazily on first use of category resolution."""
        if self._category_tree is not None:
            return
        try:
            tree = self._qianfan.get_all_categories(self.cookies)
            self._category_tree = tree
            self._category_map = {}
            for cat in tree:
                fc = cat.get('first_category', '')
                if not fc:
                    continue
                # Exact match: full name -> full name
                self._category_map[fc] = fc
                # Short match: extract key terms from the full name
                # e.g. "女装/女士精品" -> "女装", "女士精品"
                # e.g. "箱包皮具/热销女包/男包" -> "箱包", "皮具", "女包", "男包"
                parts = fc.replace('/', ' ').replace('、', ' ').split()
                for part in parts:
                    if len(part) >= 2:
                        # Only map if not already taken by a more specific match
                        if part not in self._category_map:
                            self._category_map[part] = fc
            print(f'  [INFO] Loaded {len(self._category_tree)} Draco categories, '
                  f'{len(self._category_map)} tag mappings')
        except Exception as e:
            print(f'  [WARN] Failed to load Draco categories: {e}')
            self._category_tree = []
            self._category_map = {}

    def _resolve_tags(self, content_tags):
        """Resolve user-friendly content tags to Draco API category parameters.

        Args:
            content_tags: list of tag strings, e.g. ['你的品类']

        Returns:
            (live_first_category, live_second_category) tuple of lists
            live_first_category: list of full first-category names
            live_second_category: list of all second-category names under matched first-categories
        """
        self._load_category_tree()
        if not self._category_tree or not content_tags:
            return None, None

        matched_first = []
        matched_second = []
        seen_first = set()

        for tag in content_tags:
            # Try exact match first
            fc = self._category_map.get(tag)
            if fc is None:
                # Fuzzy match: check if tag is substring of any category name
                for cat_name in self._category_map:
                    if tag in cat_name and len(tag) >= 2:
                        fc = self._category_map[cat_name]
                        print(f'  [INFO] Fuzzy match: "{tag}" -> "{fc}" (via "{cat_name}")')
                        break
            if fc is None:
                print(f'  [WARN] Tag "{tag}" not found in Draco categories, skipping')
                continue

            if fc in seen_first:
                continue
            seen_first.add(fc)
            matched_first.append(fc)

            # Collect all second_category values for this first_category
            for cat in self._category_tree:
                if cat.get('first_category', '') == fc:
                    sc_list = cat.get('second_category', [])
                    matched_second.extend(sc_list)
                    break

        if not matched_first:
            print(f'  [WARN] No tags resolved to Draco categories: {content_tags}')
            return None, None

        print(f'  [INFO] Resolved tags {content_tags} -> '
              f'first_category={matched_first}, '
              f'second_category count={len(matched_second)}')
        return matched_first, matched_second

    def search_live_plan_kols(self, live_plan_start=None, live_plan_end=None,
                              content_tags=None, max_pages=10, min_fans=0):
        """Draco API: 搜索有直播计划的达人 + 服务端品类过滤 + 去重

        现在使用 live_first_category + live_second_category 参数进行服务端过滤，
        与网页端行为一致。移除了不准确的客户端 distribution_category 字符串匹配。
        """
        # Resolve tags to Draco API categories
        live_first_cat, live_second_cat = None, None
        if content_tags:
            live_first_cat, live_second_cat = self._resolve_tags(content_tags)

        seed = random.randint(1000, 9999)
        seen_ids = set()
        all_kols = []

        for page in range(1, max_pages + 1):
            try:
                r = self._qianfan.search_live_kols(
                    self.cookies, page=page, page_size=20,
                    has_live_plan=True,
                    live_plan_start=live_plan_start,
                    live_plan_end=live_plan_end,
                    live_first_category=live_first_cat,
                    live_second_category=live_second_cat,
                    seed=seed
                )
            except Exception as e:
                print(f'  [WARN] Page {page}: {e}')
                break

            kols = r.get('distributors', [])
            if not kols:
                break

            # Dedup by distributor_id
            new_kols = []
            for k in kols:
                kid = k.get('distributor_id', '')
                if kid and kid not in seen_ids:
                    seen_ids.add(kid)
                    new_kols.append(k)
            kols = new_kols

            # Client-side min_fans filter (API doesn't support this natively)
            if min_fans > 0:
                kols = [k for k in kols if k['fans_num'] >= min_fans]

            all_kols.extend(kols)

            # Stop if we've exhausted results
            total = r.get('total', 0)
            if page == 1 and content_tags:
                print(f'  [INFO] API total with category filter: {total}')
            if total <= page * 20:
                break

        all_kols.sort(key=lambda k: k['fans_num'], reverse=True)
        return all_kols

    def search_kols_by_name(self, name, max_pages=1):
        """按昵称精确搜索达人（与蒲公英邀约页同款逻辑）

        Args:
            name: 达人昵称（如 '达人昵称'）
            max_pages: 最大翻页数（默认1页足够精确命中）

        Returns:
            list of distributor dicts（同 search_live_plan_kols 结构）
        """
        import requests as _requests
        from xhs_utils.xhs_qianfan_util import generate_qianfan_signed_headers

        api = '/api/draco/distributor-square/live/buyers'
        url = 'https://pgy.xiaohongshu.com' + api
        all_kols = []
        for page in range(1, max_pages + 1):
            body = {'query_param': {'page': page, 'limit': 20, 'seed': random.randint(1000, 9999)},
                    'nick_name': name}
            data = json.dumps(body, separators=(',', ':'))
            headers = generate_qianfan_signed_headers(self.cookies['a1'], api, data)
            r = _requests.post(url, headers=headers, cookies=self.cookies, data=data, timeout=30)
            j = r.json()
            infos = j.get('data', {}).get('distributor_info_list', [])
            if not infos:
                break
            for it in infos:
                info = it.get('distributor_data_info', {})
                inv = it.get('invitation_info', {})
                all_kols.append({
                    'distributor_id': info.get('distributor_id', ''),
                    'name': info.get('distributor_name', ''),
                    'fans_num': info.get('fans_num', 0),
                    'city': info.get('city', ''),
                    'sex': info.get('sex', ''),
                    'red_id': info.get('red_id', ''),
                    'avg_sale_amount': info.get('avg_sale_amount', ''),
                    'avg_live_viewer_num': info.get('avg_live_viewer_num', '0'),
                    'max_online_people_num': info.get('max_online_people_num', 0),
                    'distribution_category': info.get('distribution_category', []),
                    'content_categorys': info.get('content_categorys', []),
                    'can_invite': inv.get('can_invite', False) if inv else None,
                })
        return all_kols

    # ============================================================
    # 联系方式
    # ============================================================

    def get_contact(self, kol_id):
        """获取达人完整联系方式(未屏蔽)"""
        try:
            r = self._qianfan.get_kol_contact_info(kol_id, self.cookies)
            return r.get('data', {}).get('contact_info', {})
        except Exception as e:
            return {'error': str(e)}

    # ============================================================
    # 达人详情数据
    # ============================================================

    def get_kol_detail(self, kol_id):
        """获取达人概览详情数据

        Returns:
            dict with keys: fans_num, view_middle_count, average_sales,
            total_sales, live_gpm, live_count, live_days, interaction_rate,
            proportion_of_active_fans, proportion_of_order_fans,
            fan_unit_price, number_of_partner_seller, number_of_oromoted_products,
            max_online_viewer, new_fans_num, etc.
        """
        try:
            r = self._qianfan.get_user_detail(kol_id, self.cookies)
            return r.get('data', {}).get('buyer_overview_info', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_cooperation_categories(self, kol_id, date_type=2):
        """获取达人合作品类分析数据

        Args:
            kol_id: 达人ID
            date_type: 1=近7天, 2=近30天, 3=近90天

        Returns:
            list of category info, each with: first_category_name,
            second_category_name, avg_price, sale_amount,
            refer_commission_rate, show_data
        """
        try:
            r = self._qianfan.get_user_cooperation(kol_id, self.cookies)
            return r.get('data', {}).get('buyer_coo_categories_analysis_infos', [])
        except Exception as e:
            return [{'error': str(e)}]

    def get_kol_shops(self, kol_id, date_type=2, page=1, size=20):
        """获取达人合作店铺清单

        Args:
            kol_id: 达人ID (distributor_id)
            date_type: 1=近7天, 2=近30天, 3=近90天
            page: 页码，从1开始
            size: 每页数量，最大50

        Returns:
            dict with keys: total, shops
            shops is a list of shop info, each with:
            shop_name, seller_id, seller_uid, main_category_name,
            avg_price, sale_amount, num_of_promoted_products, show_data
        """
        try:
            r = self._qianfan.get_user_shop(kol_id, self.cookies,
                                             date_type=date_type, page=page, size=size)
            return {
                'total': r.get('data', {}).get('total', 0),
                'shops': r.get('data', {}).get('buyer_coo_shop_analysis_infos', [])
            }
        except Exception as e:
            return {'total': 0, 'shops': [{'error': str(e)}]}

    def get_kol_products(self, kol_id, date_type=2, page=1, size=20):
        """获取达人合作商品数据

        Args:
            kol_id: 达人ID (distributor_id)
            date_type: 1=近7天, 2=近30天, 3=近90天
            page: 页码，从1开始
            size: 每页数量，最大50

        Returns:
            dict with keys: total, products
            products is a list of product info, each with:
            prodcut_name, product_id, sku_id, shop_name, seller_id,
            seller_uid, price, sales, live_count, product_cover, show_data
        """
        try:
            r = self._qianfan.get_user_item(kol_id, self.cookies,
                                             date_type=date_type, page=page, size=size)
            return {
                'total': r.get('data', {}).get('total', 0),
                'products': r.get('data', {}).get('buyer_coo_product_analysis_infos', [])
            }
        except Exception as e:
            return {'total': 0, 'products': [{'error': str(e)}]}

    def get_kol_fans(self, kol_id):
        """获取达人粉丝数据

        Returns:
            dict with keys: fans_data_info, sex_distribution_info,
            age_distribution_info, province_distribution_info,
            city_distribution_info, hobby_distribution_info
        """
        try:
            r = self._qianfan.get_user_fans(kol_id, self.cookies)
            return r.get('data', {})
        except Exception as e:
            return {'error': str(e)}

    # ============================================================
    # 电商转化力（网页端达人详情口径，2026-08 从浏览器抓包发现）
    # ============================================================

    def get_kol_commerce_transformation(self, kol_id, date_type=1):
        """达人电商转化力总览（网页端「电商转化力」口径）

        Returns: {cooperate_seller_count, cooperate_goods_count, total_sale_amount,
                  single_max_sale_amount, average_sale_amount, brand_average_sale_amount,
                  customer_price, single_average_customer_price}
        """
        try:
            r = self._qianfan.get_kol_commerce_transformation(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_cooperation_shops_web(self, kol_id, date_type=1, first_category_name=''):
        """达人合作店铺（网页端口径，含直播销售额/均价/售出商品数）

        Returns: {total, shops: [{shop_name, seller_id, main_category_name,
                  average_sale_price, live_sale_amount, sold_goods_count}]}
        """
        try:
            r = self._qianfan.get_kol_cooperation_shop(kol_id, self.cookies, date_type=date_type,
                                                       first_category_name=first_category_name)
            d = r.get('data', {}).get('data', {})
            infos = d.get('detail_infos', [])
            return {
                'total': d.get('total', len(infos)),
                'shops': infos
            }
        except Exception as e:
            return {'error': str(e)}

    def get_kol_cooperation_goods_web(self, kol_id, date_type=1, first_category_name=''):
        """达人合作商品（网页端口径，含直播销售额/均价/相关直播场次）

        Returns: {total, goods: [{goods_name, sku_id, seller_id, shop_name,
                  average_sale_price, live_sale_amount, relevance_live_count, goods_img}]}
        """
        try:
            r = self._qianfan.get_kol_cooperation_goods(kol_id, self.cookies, date_type=date_type,
                                                        first_category_name=first_category_name)
            d = r.get('data', {}).get('data', {})
            infos = d.get('detail_infos', [])
            return {
                'total': d.get('total', len(infos)),
                'goods': infos
            }
        except Exception as e:
            return {'error': str(e)}

    def get_kol_cooperation_category_web(self, kol_id, date_type=1):
        """达人合作类目（网页端口径，含直播销售额/均价/佣金率）

        Returns: {total, categories: [{first_category_name, second_category_name,
                  average_sale_price, live_sale_amount, refer_commission_rate}]}
        """
        try:
            r = self._qianfan.get_kol_cooperation_category(kol_id, self.cookies, date_type=date_type)
            d = r.get('data', {}).get('data', {})
            infos = d.get('detail_infos', [])
            return {
                'total': d.get('total', len(infos)),
                'categories': infos
            }
        except Exception as e:
            return {'error': str(e)}

    def get_kol_detail_overview_web(self, kol_id, date_type=1):
        """达人详情总览（网页端「数据概览」口径，含直播时长/观播/客单价等）

        Returns: {average_sale_amount, customer_price, average_live_duration,
                  single_live_viewer_number, order_fans_rate, recent_live_days, ...}
        """
        try:
            r = self._qianfan.get_kol_detail_overview(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_live_input(self, kol_id, date_type=1):
        """达人直播投入度（订阅数/直播时长/关联笔记数）"""
        try:
            r = self._qianfan.get_kol_live_input(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_live_perception(self, kol_id, date_type=1):
        """达人直播表现力（观播时长/互动率/封面点击率/最高在线）"""
        try:
            r = self._qianfan.get_kol_live_perception(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_fans_buy(self, kol_id, date_type=1):
        """达人粉丝购买力（下单粉丝数/单价/占比）"""
        try:
            r = self._qianfan.get_kol_fans_buy(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data', {})
        except Exception as e:
            return {'error': str(e)}

    def get_kol_live_forecast(self, kol_id, date_type=1):
        """达人直播预告笔记（订阅数/进房数）"""
        try:
            r = self._qianfan.get_kol_live_forecast(kol_id, self.cookies, date_type=date_type)
            return r.get('data', {}).get('data_list', [])
        except Exception as e:
            return {'error': str(e)}

    def get_kol_cooperative_sellers(self, kol_id, date_type=2, page=1, size=20,
                                    with_contact=True, with_products=True):
        """获取达人合作商家清单 + 商家联系方式 + 代表商品（穿透链路）

        链路: 达人 -> 合作店铺(get_user_shop) -> 商家联系方式(get_contact_info)
               -> 代表商品(get_user_item 按 seller_id 过滤)

        Args:
            kol_id: 达人ID (distributor_id)
            date_type: 1=近7天, 2=近30天, 3=近90天
            page/size: 店铺分页
            with_contact: 是否附加商家联系方式（tel/wechat，需商家已共享）
            with_products: 是否附加该商家的代表商品（从达人合作商品中按 seller_id 过滤）

        Returns:
            dict: {
                total: 合作商家总数,
                sellers: [{
                    shop_name, seller_id, seller_uid, main_category_name,
                    avg_price, sale_amount, num_of_promoted_products,
                    contact: {tel, wechat} | {} | {error},
                    products: [{prodcut_name, price, sales, live_count, product_cover}, ...]
                }, ...]
            }
        """
        shops = self.get_kol_shops(kol_id, date_type=date_type, page=page, size=size)
        sellers = list(shops.get('shops', []))

        # All cooperative products of this KOL (filtered by seller later)
        products_by_seller = {}
        if with_products:
            all_items = self.get_kol_products(kol_id, date_type=date_type, page=1, size=50)
            for p in all_items.get('products', []):
                sid = p.get('seller_id', '')
                products_by_seller.setdefault(sid, []).append({
                    'prodcut_name': p.get('prodcut_name', ''),
                    'price': p.get('price', 0),
                    'sales': p.get('sales', 0),
                    'live_count': p.get('live_count', 0),
                    'product_cover': p.get('product_cover', ''),
                })

        enriched = []
        for s in sellers:
            item = dict(s)
            sid = s.get('seller_id', '')
            if with_contact:
                try:
                    c = self._qianfan.get_contact_info(sid, self.cookies)
                    item['contact'] = c.get('data', {}).get('contact_info', {})
                except Exception as e:
                    item['contact'] = {'error': str(e)}
            if with_products:
                item['products'] = products_by_seller.get(sid, [])[:10]
            enriched.append(item)

        return {'total': shops.get('total', 0), 'sellers': enriched}

    def get_kol_full_profile(self, kol_id, date_type=2):
        """获取达人完整画像（一键获取所有详情数据）

        Args:
            kol_id: 达人ID
            date_type: 1=近7天, 2=近30天, 3=近90天

        Returns:
            dict with keys: detail, contact, cooperation_categories,
            shops, products, fans, can_invite
        """
        return {
            'detail': self.get_kol_detail(kol_id),
            'contact': self.get_contact(kol_id),
            'cooperation_categories': self.get_kol_cooperation_categories(kol_id, date_type),
            'shops': self.get_kol_shops(kol_id, date_type),
            'products': self.get_kol_products(kol_id, date_type),
            'fans': self.get_kol_fans(kol_id),
            'can_invite': self.check_permission(kol_id)
        }

    # ============================================================
    # 商家搜索（看同行）
    # ============================================================

    def get_seller_products(self, seller_id, page=1, size=20):
        """商家商品列表（看同行）

        Returns: {total, products: [{prodcut_name, product_id, new_sku_id, price,
                  sales, commission, coo_buyer_num, product_cover}]}
        """
        try:
            r = self._qianfan.get_seller_item_list(seller_id, self.cookies, page=page, size=size)
            d = r.get('data', {})
            prods = d.get('seller_products', [])
            return {'total': d.get('total', len(prods)), 'products': prods}
        except Exception as e:
            return {'error': str(e)}

    def get_seller_coo_buyers(self, seller_id, page=1, size=20, is_new_coo_buyer=False):
        """商家合作达人列表（看同行）—— 核心穿透能力

        Returns: {total, buyers: [{distributor_data_info, distributor_seller_data_info,
                  distributor_extra_info, invitation_info}]}
        """
        try:
            r = self._qianfan.get_seller_coo_buyer_list(
                seller_id, self.cookies, page=page, size=size,
                is_new_coo_buyer=is_new_coo_buyer)
            d = r.get('data', {})
            buyers = d.get('pgy_seller_coo_buyer_infos', [])
            return {'total': d.get('total', len(buyers)), 'buyers': buyers}
        except Exception as e:
            return {'error': str(e)}

    def get_seller_full_view(self, seller_id, page=1, size=20):
        """商家完整视角（看同行）：商品 + 合作达人 + 店铺链接

        Returns: {seller_id, shop_url, products: {...}, coo_buyers: {...}}
        """
        return {
            'seller_id': seller_id,
            'shop_url': self.get_seller_shop_url(seller_id),
            'products': self.get_seller_products(seller_id, page=page, size=size),
            'coo_buyers': self.get_seller_coo_buyers(seller_id, page=page, size=size),
        }

    def get_seller_shop_url(self, seller_id):
        """商家店铺主页 URL（小红书店铺端）

        通过 https://www.xiaohongshu.com/shop/{seller_id} 可直接打开商家店铺主页，
        展示：商家粉丝、已售量、好评率、服务评分、全部商品及销量、
        以及商品名中的合作达人（如【Jessica专属】）等完整商家详情。

        Args:
            seller_id: 商家ID（来自 get_kol_cooperative_sellers / get_kol_shops 的 seller_id）

        Returns:
            str: 店铺主页 URL
        """
        return f'https://www.xiaohongshu.com/shop/{seller_id}'

    def search_sellers(self, keyword, page=1, size=20, category=None):
        """搜索商家/店铺（看同行功能）

        Args:
            keyword: 搜索关键词（必填，如你的品类名）
            page: 页码，从1开始
            size: 每页数量，默认20
            category: 可选品类过滤（如你的品类的平台类目名）

        Returns:
            dict with keys: total, sellers
            sellers is a list of shop info, each with:
            sellerId, sellerName, sellerAvatar
        """
        try:
            r = self._qianfan.search_sellers(keyword, self.cookies,
                                              page=page, size=size, category=category)
            return {
                'total': r.get('data', {}).get('total', 0),
                'sellers': r.get('data', {}).get('sellers', [])
            }
        except Exception as e:
            return {'total': 0, 'sellers': [{'error': str(e)}]}

    # ============================================================
    # 邀约
    # ============================================================

    def get_items(self, kol_id):
        """获取可用商品 ID 列表"""
        try:
            r = self._qianfan.get_last_invite_info(kol_id, self.cookies)
            items = r.get('data', {}).get('item_infos', [])
            if items:
                return [it.get('item_id', '') for it in items[:8]]
        except Exception:
            pass
        # 无可用商品: 返回空列表（需在蒲公英后台为该达人配置可推商品）
        return []

    def get_invite_permission_detail(self, kol_id):
        """返回完整权限响应；仅明确的已邀约/已接受提示可用于跳过。"""
        r = self._qianfan.get_kol_invite_permission(kol_id, self.cookies)
        self._check_response(r, f'Permission {kol_id}')
        return r

    def check_permission(self, kol_id):
        """检查达人是否可邀约"""
        try:
            r = self.get_invite_permission_detail(kol_id)
            return r.get('data', {}).get('permission_type') == 0
        except Exception:
            return False

    def invite_single(self, kol_id, message, commission_lower=25, commission_higher=35,
                      target_ids=None):
        """向单个达人发送直播邀约"""
        if not self._seller_id:
            raise ValueError(
                'seller_id 未配置: 请在 pgy_cookies.json 中加入 "_seller_id" 字段, '
                '或设置环境变量 PGY_SELLER_ID, 或在初始化时传入 seller_id 参数'
            )
        if target_ids is None:
            target_ids = self.get_items(kol_id)

        try:
            r = self._qianfan.send_live_invite_batch(
                kol_ids=[kol_id], target_ids=target_ids,
                message=message, seller_id=self._seller_id,
                commission_lower=commission_lower, commission_higher=commission_higher,
                cookies=self.cookies
            )
            self._check_response(r, f'Invite {kol_id}')

            if r.get('success'):
                inv = r['data']['invitation_kol_results'][0]
                return {
                    'success': True,
                    'invitation_id': inv.get('invitation_id', ''),
                    'kol_name': inv.get('kol_nick_name', ''),
                    'rest_quota': r['data'].get('rest_quota', 0)
                }
            return {'success': False, 'error_msg': r.get('msg', 'unknown')}
        except CookieExpiredError:
            raise
        except Exception as e:
            return {'success': False, 'error_msg': str(e)}

    def batch_invite(self, kols, message, commission_lower=25, commission_higher=35,
                     rate_limit=2.0, collect_contacts=True):
        """批量邀约达人,自动获取联系方式"""
        today = datetime.now().strftime('%Y-%m-%d')
        results = []

        for i, kol in enumerate(kols):
            dist_id = kol.get('distributor_id', kol.get('userId', ''))
            name = kol.get('name', '?')
            fans = kol.get('fans_num', kol.get('fansNum', 0))

            # Get contact
            contact_str = ''
            if collect_contacts:
                try:
                    ci = self.get_contact(dist_id)
                    parts = []
                    if ci.get('wechat'):
                        parts.append('wechat:' + ci['wechat'])
                    phone = ci.get('phone') or ci.get('tel') or ci.get('mobile')
                    if phone:
                        parts.append('phone:' + phone)
                    contact_str = ', '.join(parts) if parts else '(not shared)'
                except Exception as e:
                    contact_str = f'(error: {e})'

            # Check permission
            if not self.check_permission(dist_id):
                results.append({
                    'name': name, 'fans': fans, 'contact': contact_str,
                    'date': today, 'invite_id': '', 'status': 'SKIP'
                })
                print(f'  [{i+1:>2}] {name[:25]:25s} | SKIP (no permission)')
                continue

            # Send invite
            inv = self.invite_single(dist_id, message, commission_lower, commission_higher)

            results.append({
                'name': name, 'fans': fans, 'contact': contact_str,
                'date': today,
                'invite_id': str(inv.get('invitation_id', '')),
                'status': 'OK' if inv.get('success') else f'FAIL: {inv.get("error_msg", "?")}'
            })

            status = results[-1]['status']
            print(f'  [{i+1:>2}] {name[:25]:25s} | {fans:>8} fans | {contact_str[:45]:45s} | {status}')

            if i < len(kols) - 1:
                time.sleep(rate_limit)

        return results

    # ============================================================
    # 结果输出
    # ============================================================

    @staticmethod
    def print_table(results, title='Results'):
        """打印结果表格"""
        print()
        print(f'=== {title} ===')
        hdr = f'{"#":>2} | {"Name":22s} | {"Fans":>8} | {"WeChat":25s} | {"Phone":15s} | {"Date":10s} | {"InviteID":>10} | {"Status"}'
        print(hdr)
        print('-' * len(hdr))
        for i, r in enumerate(results):
            c = r.get('contact', '')
            w = p = ''
            for part in c.split(', '):
                if 'wechat:' in part:
                    w = part.replace('wechat:', '')
                if 'phone:' in part:
                    p = part.replace('phone:', '')
            print(f'{i+1:>2} | {r["name"][:22]:22s} | {r["fans"]:>8} | {w:25s} | {p:15s} | {r["date"]:10s} | {r.get("invite_id","?"):>10} | {r["status"]}')
        print('-' * len(hdr))

    @staticmethod
    def save_results(results, filepath):
        """保存结果到 JSON 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'Saved to {filepath}')


def quick_invite(cookie_file, tags, live_start, live_end, message,
                 commission_lower=25, commission_higher=35, max_kols=10):
    """一键邀约:搜索 + 联系方式 + 批量邀约"""
    skill = PgyLiveSkill(cookie_file=cookie_file)
    print('Searching live KOLs...')
    kols = skill.search_live_plan_kols(
        live_plan_start=live_start, live_plan_end=live_end,
        content_tags=tags, max_pages=10
    )
    print(f'Found {len(kols)} matching KOLs, taking top {max_kols}')
    top = kols[:max_kols]
    print(f'Inviting {len(top)} KOLs...')
    results = skill.batch_invite(top, message, commission_lower, commission_higher)
    skill.print_table(results, f'Live Invite ({live_start}-{live_end})')
    return results
