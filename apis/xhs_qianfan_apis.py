import json
import requests
from loguru import logger
from xhs_utils.cookie_util import trans_cookies
from xhs_utils.http_util import REQUEST_TIMEOUT
from xhs_utils.xhs_qianfan_util import get_qianfan_headers_template, generate_qianfan_data, get_qianfan_userDetail_headers_template, generate_qianfan_signed_headers, get_live_invite_headers_template

class QianFanAPI:
    def get_all_categories(self, cookies):
        headers = get_qianfan_headers_template()
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributors-tags"
        params = {
            "types": "content_category,distribution_category,user_design_tag,content_tag"
        }
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        distribution_category = response.json()["data"]['distributor_tag_map']["distribution_category"]
        return distribution_category

    def choose_categories(self, cookies):
        distribution_category = self.get_all_categories(cookies)
        for first_index, first_category_temp in enumerate(distribution_category):
            logger.info(f'{first_index}: {first_category_temp["first_category"]}')
            for second_index, second_category_temp in enumerate(first_category_temp["second_category"]):
                logger.info(f'---- {second_index}: {second_category_temp}')
        choice = input(
            "请选择您的类目：如果输入-1则为全部类目，输入1-2-4代表整个美妆/个护，服饰鞋包，母婴用品类目，输入1(1,3,4)-2代表美妆/个护类目下的1,3,4子类目和服饰鞋的全部\n")
        return choice, distribution_category

    def get_user_by_page(self, choice, distribution_category, page, cookies):
        headers = get_qianfan_headers_template()
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributors"
        data = generate_qianfan_data(choice, distribution_category, page)
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        res_json = response.json()
        total = res_json["data"]["total"]
        user_list = res_json["data"]["list"]
        return user_list, total

    def get_some_user(self, choice, distribution_category, num, cookies):
        user_list = []
        page = 1
        while len(user_list) < num:
            user_list_temp, total = self.get_user_by_page(choice, distribution_category, page, cookies)
            user_list.extend(user_list_temp)
            page += 1
            if page > total / 20 + 1:
                break
        if len(user_list) > num:
            user_list = user_list[:num]
        return user_list

    def get_user_detail(self, user_id, cookies):
        headers = get_qianfan_userDetail_headers_template(user_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributor/detail/overview/v2"
        data = {
            "buyer_id": user_id,
            "date_type": 2
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_cooperation(self, user_id, cookies):
        headers = get_qianfan_userDetail_headers_template(user_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributor/cooperative/category/v2"
        data = {
            "buyer_id": user_id,
            "first_live_category": "",
            "second_live_category": "",
            "date_type": 2,
            "page": 1,
            "size": 10
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_shop(self, user_id, cookies, date_type=2, page=1, size=20):
        headers = get_qianfan_userDetail_headers_template(user_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributor/cooperative/shop/v2"
        data = {
            "buyer_id": user_id,
            "first_live_category": "",
            "second_live_category": "",
            "date_type": date_type,
            "page": page,
            "size": size
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_item(self, user_id, cookies, date_type=2, page=1, size=20):
        headers = get_qianfan_userDetail_headers_template(user_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distributor/cooperative/item/v2"
        data = {
            "buyer_id": user_id,
            "first_live_category": "",
            "second_live_category": "",
            "date_type": date_type,
            "page": page,
            "size": size
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_fans(self, user_id, cookies):
        headers = get_qianfan_userDetail_headers_template(user_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distributor-square/distribuitor/detail/fans"
        params = {
            "distributor_id": user_id,
            "date_type": "2"
        }
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    # ============================================================
    # 网页端达人详情端点（从浏览器抓包发现，kol_detail 系列）
    # ============================================================

    def get_kol_commerce_transformation(self, kol_id, cookies, date_type=1):
        """电商转化力总览 GET /api/draco/distribution/kol_detail/commerce_transformation"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/commerce_transformation"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_cooperation_shop(self, kol_id, cookies, date_type=1, first_category_name=''):
        """合作店铺（网页端口径） GET .../commerce_transformation/cooperation_shop"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/commerce_transformation/cooperation_shop"
        params = {"buyer_id": kol_id, "date_type": date_type, "first_category_name": first_category_name}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_cooperation_goods(self, kol_id, cookies, date_type=1, first_category_name=''):
        """合作商品（网页端口径） GET .../commerce_transformation/cooperation_goods"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/commerce_transformation/cooperation_goods"
        params = {"buyer_id": kol_id, "date_type": date_type, "first_category_name": first_category_name}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_cooperation_category(self, kol_id, cookies, date_type=1):
        """合作类目（网页端口径） GET .../commerce_transformation/cooperation_category"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/commerce_transformation/cooperation_category"
        params = {"buyer_id": kol_id, "date_type": date_type, "first_category_name": ''}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_detail_overview(self, kol_id, cookies, date_type=1):
        """达人详情总览 GET /api/draco/distribution/kol_detail/overview"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/overview"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_live_input(self, kol_id, cookies, date_type=1):
        """直播投入度 GET /api/draco/distribution/kol_detail/live_input"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/live_input"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_live_perception(self, kol_id, cookies, date_type=1):
        """直播表现力 GET /api/draco/distribution/kol_detail/live_perception"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/live_perception"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_fans_buy(self, kol_id, cookies, date_type=1):
        """粉丝购买力 GET /api/draco/distribution/kol_detail/fans_buy"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/fans_buy"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_live_forecast(self, kol_id, cookies, date_type=1):
        """直播预告笔记 GET /api/draco/distribution/kol_detail/live_forecast/overview"""
        headers = get_qianfan_userDetail_headers_template(kol_id)
        url = "https://pgy.xiaohongshu.com/api/draco/distribution/kol_detail/live_forecast/overview"
        params = {"buyer_id": kol_id, "date_type": date_type}
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    # ============================================================
    # 看同行（商家详情）：seller-merchants 系列（从 HAR 抓包发现）
    # referer: /microapp/distribution/seller-det
    # ============================================================

    def get_seller_item_list(self, seller_id, cookies, page=1, size=20,
                             sort_type='', sort_field=''):
        """商家商品列表（看同行）POST /api/draco/seller-merchants/v2/same_seller/seller_item_list

        返回 data.seller_products[]: {prodcut_name, product_id, new_sku_id, price,
        sales, commission, coo_buyer_num, product_cover}
        - coo_buyer_num: 该商品合作的达人数量
        - commission: 佣金率（0.20 = 20%）
        """
        api = "/api/draco/seller-merchants/v2/same_seller/seller_item_list"
        url = "https://pgy.xiaohongshu.com" + api
        data = {
            "seller_id": seller_id,
            "sort_type": sort_type,
            "sort_field": sort_field,
            "page": page,
            "size": size
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        headers['referer'] = 'https://pgy.xiaohongshu.com/microapp/distribution/seller-det'
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_seller_coo_buyer_list(self, seller_id, cookies, page=1, size=20,
                                  is_new_coo_buyer=False, sort_type='', sort_field=''):
        """商家合作达人列表（看同行）POST /api/draco/seller-merchants/v2/same_seller/seller_coo_buyer_list

        返回 data.pgy_seller_coo_buyer_infos[]（可能 base64 编码）:
        {distributor_data_info, distributor_extra_info, distributor_seller_data_info, invitation_info}
        - distributor_data_info: 达人画像（fans_num, avg_sale_amount, city, sex, distribution_category）
        - distributor_seller_data_info: 与该商家的合作数据（seller_sales_value, coo_product_num）
        - distributor_extra_info: telephone（加密）, willing_commsion
        """
        api = "/api/draco/seller-merchants/v2/same_seller/seller_coo_buyer_list"
        url = "https://pgy.xiaohongshu.com" + api
        data = {
            "seller_id": seller_id,
            "is_new_coo_buyer": is_new_coo_buyer,
            "page": page,
            "size": size,
            "sort_field": sort_field,
            "sort_type": sort_type
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        headers['referer'] = 'https://pgy.xiaohongshu.com/microapp/distribution/seller-det'
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        j = response.json()
        # 响应可能 base64 编码
        d = j.get('data')
        if isinstance(d, str):
            try:
                import base64
                j = json.loads(base64.b64decode(d).decode('utf-8'))
            except Exception:
                pass
        return j

    def search_sellers(self, keyword, cookies, page=1, size=20, category=None):
        """
        Search sellers/shops by keyword (看同行功能).
        GET /api/draco/sellers/search

        Args:
            keyword: search keyword (required, e.g. '箱包', '女包', '女装')
            cookies: dict with at least 'a1' key
            page: page number (1-based)
            size: results per page (default 20)
            category: optional category filter (e.g. '箱包皮具/热销女包/男包')

        Returns:
            dict with keys: total, sellers
            Each seller has: sellerId, sellerName, sellerAvatar
        """
        headers = get_qianfan_headers_template()
        url = "https://pgy.xiaohongshu.com/api/draco/sellers/search"
        params = {
            "keyword": keyword,
            "page": page,
            "size": size
        }
        if category:
            params["category"] = category
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    # ============================================================
    # Live Invite Methods (Draco distribution side)
    # Based on HAR capture from /solar/pre-trade/live/kol page
    # ============================================================

    def get_seller_info(self, cookies):
        """
        Get seller/brand info from Draco distribution side.
        Returns seller_id (different from solar brandUserId), contact info, etc.
        POST /api/draco/sellers/info
        """
        api = "/api/draco/sellers/info"
        url = "https://pgy.xiaohongshu.com" + api

        # Build body with basic info structure (empty — server returns stored data)
        data = {
            "basic_info": {
                "contact_info": {
                    "contact_person_list": []
                }
            },
            "brand_info": {
                "uploader_info": {
                    "product_manual": {}
                }
            }
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_invite_permission(self, kol_id, cookies):
        """
        Check if a KOL can be invited for live cooperation.
        GET /api/draco/invite/kols/{kol_id}/permissions
        Returns permission_type: 0 = can invite
        """
        api = f"/api/draco/invite/kols/{kol_id}/permissions"
        url = "https://pgy.xiaohongshu.com" + api
        headers = get_live_invite_headers_template()
        headers['x-b3-traceid'] = generate_x_b3_traceid() if hasattr(__import__('xhs_utils.xhs_util'), 'generate_x_b3_traceid') else headers.get('x-b3-traceid', '')
        response = requests.get(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT)
        return response.json()

    def send_live_invite_batch(self, kol_ids, target_ids, message, seller_id,
                               commission_lower, commission_higher, cookies):
        """
        Send live streaming cooperation invitation to one or more KOLs.
        POST /api/draco/distribution/invite/kols/batch

        Args:
            kol_ids: list of KOL user IDs (supports batch)
            target_ids: list of product/item IDs to recommend
            message: invite message text
            seller_id: seller/brand ID from get_seller_info()
            commission_lower: minimum commission rate (%)
            commission_higher: maximum commission rate (%)
            cookies: dict with at least 'a1' key

        Returns:
            Response with invitation_kol_results per KOL
        """
        api = "/api/draco/distribution/invite/kols/batch"
        url = "https://pgy.xiaohongshu.com" + api

        data = {
            "kol_ids": kol_ids,
            "target_ids": target_ids,
            "message": message,
            "seller_id": seller_id,
            "alliance_new_invitation": True,
            "intend_distributor_rate": {
                "lower": commission_lower,
                "higher": commission_higher
            }
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_last_invite_info(self, kol_id, cookies):
        """
        Get last invite info for pre-filling the invite form.
        GET /api/draco/distribution/seller_last_invite_info
        """
        api = f"/api/draco/distribution/seller_last_invite_info"
        url = "https://pgy.xiaohongshu.com" + api
        params = {
            "current_buyer_id": kol_id,
            "alliance_new_invitation": "true"
        }
        headers = get_live_invite_headers_template()
        response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_contact_info(self, seller_id, cookies):
        """
        Get stored contact info for the seller (brand side).
        POST /api/draco/selection-center/contact/info/query
        """
        api = "/api/draco/selection-center/contact/info/query"
        url = "https://pgy.xiaohongshu.com" + api
        data = {
            "source": "SELLER_CONTACT_INFO",
            "seller_id": seller_id,
            "source_page": "/solar/pre-trade/live/kol"
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_kol_contact_info(self, kol_id, cookies):
        """
        Get unmasked contact info for a KOL (buyer/distributor side).
        POST /api/draco/selection-center/contact/info/query
        Uses source='BUYER_CONTACT_INFO' with buyer_id=kol_id.

        Args:
            kol_id: KOL's userId
            cookies: dict with at least 'a1' key

        Returns:
            dict with contact_info containing available fields:
            {wechat: 'xxx', phone: 'xxx'} (phone may be absent)
            Returns empty dict if KOL hasn't shared contact info.
        """
        api = "/api/draco/selection-center/contact/info/query"
        url = "https://pgy.xiaohongshu.com" + api
        data = {
            "source": "BUYER_CONTACT_INFO",
            "buyer_id": kol_id,
            "source_page": "/solar/pre-trade/live/kol"
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data)
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def search_live_kols(self, cookies, page=1, page_size=20,
                         has_live_plan=True, live_plan_start=None, live_plan_end=None,
                         live_first_category=None, live_second_category=None,
                         seed=None):
        """
        Search KOLs on the live/distribution side with optional live plan date filter
        and server-side category filter.
        POST /api/draco/distributor-square/live/buyers

        Args:
            cookies: dict with at least 'a1' key
            page: page number (1-based)
            page_size: results per page (default 20)
            has_live_plan: if True, filter to KOLs with live plans (0=unlimited, 1=all, 2=custom)
            live_plan_start: start date string 'YYYYMMDD' (e.g. '20260701')
            live_plan_end: end date string 'YYYYMMDD' (e.g. '20260731')
            live_first_category: list of first-level category names (e.g. ['女装/女士精品'])
            live_second_category: list of second-level category names (e.g. ['连衣裙','T恤'])
            seed: random seed for pagination

        Returns:
            dict with keys: total, page_total, distributors
            Each distributor has: distributor_id, name, fans_num,
            avg_live_viewer_num, live_day_cnt, distribution_category, etc.
        """
        import random as _random
        if seed is None:
            seed = _random.randint(1000, 9999)

        api = "/api/draco/distributor-square/live/buyers"
        url = "https://pgy.xiaohongshu.com" + api

        data = {
            "query_param": {
                "page": page,
                "limit": page_size,
                "seed": seed
            }
        }

        # Server-side category filter (matches web page behavior)
        if live_first_category:
            data["live_first_category"] = live_first_category
        if live_second_category:
            data["live_second_category"] = live_second_category

        if has_live_plan:
            data["has_live_plan"] = 1
            if live_plan_start and live_plan_end:
                data["live_plan_range"] = [live_plan_start, live_plan_end]
            else:
                data["live_plan_range"] = []

        data_json = json.dumps(data, separators=(',', ':'))
        headers = generate_qianfan_signed_headers(cookies['a1'], api, data_json)
        response = requests.post(url, headers=headers, cookies=cookies, data=data_json, timeout=REQUEST_TIMEOUT)
        res = response.json()

        # Normalize response
        result = {
            'total': res.get('data', {}).get('total', 0),
            'page_total': res.get('data', {}).get('page_total', 0),
            'distributors': []
        }

        for item in res.get('data', {}).get('distributor_info_list', []):
            info = item.get('distributor_data_info', {})
            inv = item.get('invitation_info', {})
            result['distributors'].append({
                'distributor_id': info.get('distributor_id', ''),
                'name': info.get('distributor_name', ''),
                'fans_num': info.get('fans_num', 0),
                'avg_live_viewer_num': info.get('avg_live_viewer_num', '0'),
                'live_day_cnt': info.get('live_day_cnt', 0),
                'distribution_live_num': info.get('distribution_live_num', 0),
                'max_online_people_num': info.get('max_online_people_num', 0),
                'avg_sale_amount': info.get('avg_sale_amount', ''),
                'distribution_category': info.get('distribution_category', []),
                'city': info.get('city', ''),
                'red_id': info.get('red_id', ''),
                'can_invite': inv.get('can_invite', False) if inv else None,
                'invitation_id': inv.get('invitation_id') if inv else None,
            })

        return result

if __name__ == '__main__':
    qianfan_api = QianFanAPI()
    # https://pgy.xiaohongshu.com 的cookie
    cookies_str = ''
    cookies = trans_cookies(cookies_str)
    choice, distribution_category = qianfan_api.choose_categories(cookies)
    user_list = qianfan_api.get_some_user(choice, distribution_category, 10, cookies)
    for user in user_list:
        user_id = user["distributor_id"]
        user_detail = qianfan_api.get_user_detail(user_id, cookies)
        user_cooperation = qianfan_api.get_user_cooperation(user_id, cookies)
        user_shop = qianfan_api.get_user_shop(user_id, cookies)
        user_item = qianfan_api.get_user_item(user_id, cookies)
        user_fans = qianfan_api.get_user_fans(user_id, cookies)
        logger.debug(user)
        logger.debug(user_detail)
        logger.debug(user_cooperation)
        logger.debug(user_shop)
        logger.debug(user_item)
        logger.debug(user_fans)
        logger.info(f'url: https://www.xiaohongshu.com/user/profile/{user_id}')
        logger.info(f'qianfan_url: https://pgy.xiaohongshu.com/microapp/distribution/live-blogger-info/{user_id}?source=square')
