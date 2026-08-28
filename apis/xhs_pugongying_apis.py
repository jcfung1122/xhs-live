import json
import requests
from loguru import logger
from xhs_utils.cookie_util import trans_cookies
from xhs_utils.http_util import REQUEST_TIMEOUT
from xhs_utils.xhs_pugongying_util import generate_pugongying_headers, get_pugongying_bozhu_data, generate_pugongying_data
from xhs_utils.xhs_util import get_request_headers_template


class PuGongYingAPI:
    def __init__(self):
        self.base_url = "https://pgy.xiaohongshu.com"

    def get_all_categories(self, cookies):
        api = '/api/solar/cooperator/content/tag_tree'
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(self.base_url + api, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT)
        distribution_category = response.json()["data"]
        return distribution_category

    def choose_categories(self, cookies):
        distribution_category = self.get_all_categories(cookies)
        for first_index, first_category_temp in enumerate(distribution_category):
            logger.info(f'{first_index}: {first_category_temp["taxonomy1Tag"]}')
            for second_index, second_category_temp in enumerate(first_category_temp["taxonomy2Tags"]):
                logger.info(f'---- {second_index}: {second_category_temp}')
        choice = input("请选择您的类目：如果输入-1则为全部类目，输入1-2-4代表整个美妆/个护，服饰鞋包，母婴用品类目，输入1(1,3,4)-2代表美妆/个护类目下的1,3,4子类目和服饰鞋的全部\n")
        contentTag = generate_pugongying_data(choice, distribution_category)
        return contentTag, distribution_category

    def get_track(self, data, cookies):
        api = "/api/solar/cooperator/blogger/track"
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_pugongying_headers(cookies['a1'], api, data)
        response = requests.post(self.base_url + api, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_by_page(self, page, cookies, contentTag=None):
        api = "/api/solar/cooperator/blogger/v2"
        self_info = self.get_self_info(cookies)
        brandUserId = self_info["data"]["userId"]
        # brandUserId = cookies['x-user-id-ark.xiaohongshu.com']
        data = get_pugongying_bozhu_data(page, brandUserId, contentTag)
        trackId = self.get_track(data, cookies)["data"]["trackId"]
        data['trackId'] = trackId
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_pugongying_headers(cookies['a1'], api, data)
        response = requests.post(self.base_url + api, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        res_json = response.json()
        total = res_json["data"]["total"]
        user_list = res_json["data"]["kols"]
        return user_list, total

    def get_some_user(self, num, cookies, contentTag=None):
        user_list = []
        page = 1
        while len(user_list) < num:
            user_list_temp, total = self.get_user_by_page(page, cookies, contentTag)
            user_list.extend(user_list_temp)
            page += 1
            if page > total / 20 + 1:
                break
        if len(user_list) > num:
            user_list = user_list[:num]
        return user_list

    def get_user_detail(self, user_id, cookies):
        api = "/api/solar/kol/dataV3/dataSummary"
        params = {
            "userId": user_id,
            "business": "0"
        }
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(self.base_url + api, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_fans_detail(self, user_id, cookies):
        api = "/api/solar/kol/dataV3/fansSummary"
        params = {
            "userId": user_id
        }
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(self.base_url + api, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_fans_history(self, user_id, cookies):
        api = f"/api/solar/kol/data/{user_id}/fans_overall_new_history"
        params = {
            "dateType": "1",
            "increaseType": "1"
        }
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(self.base_url + api, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_user_notes_detail(self, user_id, cookies):
        api = "/api/solar/kol/dataV3/notesRate"
        params = {
            "userId": user_id,
            "business": "0",
            "noteType": "3",
            "dateType": "1",
            "advertiseSwitch": "1"
        }
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(self.base_url + api, headers=headers, cookies=cookies, params=params, timeout=REQUEST_TIMEOUT)
        return response.json()

    def get_self_info(self, cookies):
        url = "https://pgy.xiaohongshu.com/api/solar/user/info"
        api = "/api/solar/user/info"
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.get(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT)
        return response.json()

    def send_invite(self, user_id, cookies, productName, time, inviteContent, contactInfo):
        api = "/api/solar/invite/initiate_invite"
        self_info = self.get_self_info(cookies)
        cooperateBrandId = self_info["data"]["userId"]
        cooperateBrandName = self_info["data"]["nickName"]
        data = {
            "kolId": user_id,
            "cooperateBrandId": cooperateBrandId,
            "cooperateBrandName": cooperateBrandName,
            "inviteType": 1,
            "productName": productName,
            "expectedPublishTimeStart": time[0],
            "expectedPublishTimeEnd": time[1],
            "inviteContent": inviteContent,
            "contactInfo": contactInfo,
            "contactType": 1,
            "brandUserId": cooperateBrandId
        }
        data = json.dumps(data, separators=(',', ':'))
        headers = generate_pugongying_headers(cookies['a1'], api)
        response = requests.post(self.base_url + api, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT)
        return response.json()

    # Known activity codes
    ACTIVITY_LIVE_PLAN = '6a05d7f2e4b078c8db9e1ab8'  # 有直播计划

    def search_kols(self, cookies, content_tags=None, name_filter=None, max_pages=50,
                    sort_column="comprehensiverank", sort_order="desc",
                    brand_user_id=None, activity_codes=None,
                    live_plan_date_start=None, live_plan_date_end=None):
        """
        Search KOLs by content tags with optional name filter.
        Uses Solar API /api/solar/cooperator/blogger/v2

        Args:
            cookies: dict with at least 'a1' key
            content_tags: list of content tag strings, e.g. ['箱包', '女装']
            name_filter: optional substring to filter KOL names (client-side)
            max_pages: max pages to scan (20 KOLs per page)
            sort_column: 'comprehensiverank', 'fansCount', etc.
            sort_order: 'desc' or 'asc'
            brand_user_id: optional, auto-detected from cookies if not provided
            activity_codes: list of activity codes, e.g. [ACTIVITY_LIVE_PLAN]
            live_plan_date_start: timestamp (ms) - client-side filter start
            live_plan_date_end: timestamp (ms) - client-side filter end

        Returns:
            list of matching KOL dicts with keys: userId, name, fansNum,
            kliveCnt30d, tradeType, location, avgLiveViewerNum, avgAgmv90d
        """
        if not brand_user_id:
            # Try from solar user info; fall back to cookie-based detection
            try:
                self_info = self.get_self_info(cookies)
                brand_user_id = self_info.get('data', {}).get('userId', '')
            except Exception:
                brand_user_id = ''
        if not brand_user_id:
            brand_user_id = cookies.get('x-user-id-pgy.xiaohongshu.com', '')

        results = []
        for page in range(1, max_pages + 1):
            data = get_pugongying_bozhu_data(
                page=page, brandUserId=brand_user_id,
                contentTag=content_tags
            )
            data['column'] = sort_column
            data['sort'] = sort_order
            if activity_codes:
                data['activityCodes'] = activity_codes

            # Get trackId
            track_api = "/api/solar/cooperator/blogger/track"
            track_data = json.dumps(data, separators=(',', ':'))
            track_headers = generate_pugongying_headers(cookies['a1'], track_api, track_data)
            track_resp = requests.post(
                self.base_url + track_api,
                headers=track_headers, cookies=cookies, data=track_data,
                timeout=REQUEST_TIMEOUT
            )
            data['trackId'] = track_resp.json().get('data', {}).get('trackId', '')

            # Search KOLs
            api = "/api/solar/cooperator/blogger/v2"
            data_json = json.dumps(data, separators=(',', ':'))
            headers = generate_pugongying_headers(cookies['a1'], api, data_json)
            resp = requests.post(
                self.base_url + api,
                headers=headers, cookies=cookies, data=data_json,
                timeout=REQUEST_TIMEOUT
            )
            res = resp.json()
            kols = res.get('data', {}).get('kols', [])

            if not kols:
                break

            for k in kols:
                name = k.get('nickName', k.get('name', ''))

                # Client-side name filter
                if name_filter and name_filter not in name:
                    continue

                results.append({
                    'userId': k.get('userId', ''),
                    'name': name,
                    'fansNum': k.get('fansNum', k.get('fansCount', 0)),
                    'kliveCnt30d': k.get('kliveCnt30d', 0),
                    'tradeType': k.get('tradeType') or '',
                    'location': k.get('location') or '',
                    'avgLiveViewerNum': k.get('avgLiveViewerNum', 0),
                    'avgAgmv90d': k.get('avgAgmv90d', 0),
                })

                # If we found a name match, we can stop early
                if name_filter and name_filter in name:
                    # Found! Return just this one
                    pass

            if name_filter and results:
                break  # Found match, stop scanning

        return results


if __name__ == '__main__':
    pugongying_api = PuGongYingAPI()
    # "https://pgy.xiaohongshu.com"的cookie
    cookies_str = ''
    cookies = trans_cookies(cookies_str)
    contentTag, distribution_category = pugongying_api.choose_categories(cookies)
    user_list = pugongying_api.get_some_user(1, cookies, contentTag)
    for user in user_list:
        user_id = user["userId"]
        user_detail = pugongying_api.get_user_detail(user_id, cookies)
        fans_detail = pugongying_api.get_user_fans_detail(user_id, cookies)
        fans_history = pugongying_api.get_user_fans_history(user_id, cookies)
        notes_detail = pugongying_api.get_user_notes_detail(user_id, cookies)
        # 期望发布时间 产品名称，【开始时间，结束时间】，合作内容介绍，联系方式
        invite_res = pugongying_api.send_invite(user_id, cookies, "测试", ["2021-10-01", "2021-10-01"], "测试", "")
        logger.debug(user_detail)
        logger.debug(fans_detail)
        logger.debug(fans_history)
        logger.debug(notes_detail)
        logger.debug(invite_res)
        logger.info(f'url: https://www.xiaohongshu.com/user/profile/{user_id}')
        logger.info('===========================')
