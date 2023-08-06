import requests
import re
from pprint import pprint
from urllib.parse import urlparse
from tqdm import tqdm

# 去掉分享链接前后的汉字、符号等


def clean_url(text):
    match = re.search(r'(https?://\S+)', text)
    if match:
        url = match.group(1)
    return url

# 如果都是数字，就说明是分享后跳转的链接


def is_numeric_url(url):
    pattern = r'\d+$'
    match = re.search(pattern, url)
    return bool(match)


def request_1(url):
    if not is_numeric_url(url):
        response = requests.get(url=url, allow_redirects=False)
        url_1 = response.headers.get('location')
        result = "https://www.douyin.com/video/" + \
            urlparse(url_1, scheme='https').path.split('/')[-2]
        return result
    else:
        return url


def get_video(url):
    headers = {
        "cookie": 'douyin.com; ttwid=1|3qFt3uO7dNhnBx3Hm06PJo5vrcCE7XSFloUqbmqgaBA|1673328587|ae5bc41ee255b7fa34c66c2d89f9a06166a44b6a7b7e1a343d6ecfb8bff2e807; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; store-region=cn-ln; store-region-src=uid; douyin.com; strategyABtestKey="1679528646.757"; passport_csrf_token=5ffa4acc3d88d80e5a843c3a91c5595a; passport_csrf_token_default=5ffa4acc3d88d80e5a843c3a91c5595a; s_v_web_id=verify_lfkbzpz1_lUvAffP4_hLcZ_4HG8_Azly_ufsgFnoBriYH; csrf_session_id=079c4a9f1314f7bacca77269b8a9815f; _tea_utm_cache_1243=undefined; MONITOR_WEB_ID=41d167e3-84f5-40be-b90a-fdd2b9a55123; VIDEO_FILTER_MEMO_SELECT={"expireTime":1680133556197,"type":1}; download_guide="3/20230323"; pwa2="2|0"; sso_uid_tt=8ee67fe87e208bca9118e933b6c36a20; sso_uid_tt_ss=8ee67fe87e208bca9118e933b6c36a20; toutiao_sso_user=bdaef499ca245a8defef555a15fb8cac; toutiao_sso_user_ss=bdaef499ca245a8defef555a15fb8cac; passport_auth_status=58117164854cb2ce4164567698bbd18a,; passport_auth_status_ss=58117164854cb2ce4164567698bbd18a,; uid_tt=1ec8e8b9254a3f61813f4f7ec2a14929; uid_tt_ss=1ec8e8b9254a3f61813f4f7ec2a14929; sid_tt=31921c9a4bdd359f2f99f286cd5db7df; sessionid=31921c9a4bdd359f2f99f286cd5db7df; sessionid_ss=31921c9a4bdd359f2f99f286cd5db7df; odin_tt=044157b5f47d2151ba70b433accf5072d90b482fe1d22af0d4373732d0d3eda955f4b9c9fcd18f4280ea1beb69b3e4e6; passport_assist_user=CjygW18XurD0x_x7TBh5w2oHwG2a9KF2C0f0Pbp15z2Y_LggHoxiVKPvH5ZqzMB4dgJvuTQGo51LaLfdB14aSAo8Vdi9CKYu4KW9qmRnHUMF8XmD9LVdxioZloEKxB5jLgX6jx5kiXtlyJzfbChQADMzzqaNmnmcGyCN4WtsEL-_rA0Yia_WVCIBA2cEl7Q=; sid_ucp_sso_v1=1.0.0-KGQxMjhlMTQ0NjIwMGJkNzg4ZjZjOGQwZDg1YzMzOGYyOTI3ZTA3ZWYKHQjJ0fLu3wIQnsXuoAYY7zEgDDCP2OzUBTgGQPQHGgJsZiIgYmRhZWY0OTljYTI0NWE4ZGVmZWY1NTVhMTVmYjhjYWM; ssid_ucp_sso_v1=1.0.0-KGQxMjhlMTQ0NjIwMGJkNzg4ZjZjOGQwZDg1YzMzOGYyOTI3ZTA3ZWYKHQjJ0fLu3wIQnsXuoAYY7zEgDDCP2OzUBTgGQPQHGgJsZiIgYmRhZWY0OTljYTI0NWE4ZGVmZWY1NTVhMTVmYjhjYWM; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jZXJ0IjoiLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tXG5NSUlDRXpDQ0FicWdBd0lCQWdJVUtsV0VFWTZpVGdUUnVrUU1GMDdtR0M0VzMyZ3dDZ1lJS29aSXpqMEVBd0l3XG5NVEVMTUFrR0ExVUVCaE1DUTA0eElqQWdCZ05WQkFNTUdYUnBZMnRsZEY5bmRXRnlaRjlqWVY5bFkyUnpZVjh5XG5OVFl3SGhjTk1qTXdNekl6TURBMU1UUXlXaGNOTXpNd016SXpNRGcxTVRReVdqQW5NUXN3Q1FZRFZRUUdFd0pEXG5UakVZTUJZR0ExVUVBd3dQWW1SZmRHbGphMlYwWDJkMVlYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEXG5BUWNEUWdBRVNnYkljUVhQaEY4UmUxaXpPTW1JQnduekZLNm41MFBVeUFHNGQzUVNzNjFLQ0hKTWU5dDlwb3ExXG5wRmJPWDcwaGZTSmZLUWZ4a3pMZWZwamxrZVhOQ0tPQnVUQ0J0akFPQmdOVkhROEJBZjhFQkFNQ0JhQXdNUVlEXG5WUjBsQkNvd0tBWUlLd1lCQlFVSEF3RUdDQ3NHQVFVRkJ3TUNCZ2dyQmdFRkJRY0RBd1lJS3dZQkJRVUhBd1F3XG5LUVlEVlIwT0JDSUVJSmhIWExvYTZIaTRlNTM2MTMzMkx1S0RCVzlSd0FxMHFSTEZXeXNtNmFjYk1Dc0dBMVVkXG5Jd1FrTUNLQUlES2xaK3FPWkVnU2pjeE9UVUI3Y3hTYlIyMVRlcVRSZ05kNWxKZDdJa2VETUJrR0ExVWRFUVFTXG5NQkNDRG5kM2R5NWtiM1Y1YVc0dVkyOXRNQW9HQ0NxR1NNNDlCQU1DQTBjQU1FUUNJQ0ltcDc3aXFQMkVDQmh0XG54dEt1c2VOeVNyY3dOOWJ4c3FnRWZGejV2ajFYQWlBamlod2NpbnFtbjNsSmg0Z2NXQlNJOU1XMjJvN1l5TW1kXG5ERXZlU1BzSGdRPT1cbi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS1cbiJ9; bd_ticket_guard_server_data=; LOGIN_STATUS=1; publish_badge_show_info="0,0,0,1679532712477"; sid_guard=31921c9a4bdd359f2f99f286cd5db7df|1679532714|5183987|Mon,+22-May-2023+00:51:41+GMT; sid_ucp_v1=1.0.0-KDEwODBlNWYwOWUwMTQ4ZjRhMWFkOWM0YzhlZWFlNDI1M2Q3Njg3YTkKGQjJ0fLu3wIQqsXuoAYY7zEgDDgGQPQHSAQaAmxxIiAzMTkyMWM5YTRiZGQzNTlmMmY5OWYyODZjZDVkYjdkZg; ssid_ucp_v1=1.0.0-KDEwODBlNWYwOWUwMTQ4ZjRhMWFkOWM0YzhlZWFlNDI1M2Q3Njg3YTkKGQjJ0fLu3wIQqsXuoAYY7zEgDDgGQPQHSAQaAmxxIiAzMTkyMWM5YTRiZGQzNTlmMmY5OWYyODZjZDVkYjdkZg; msToken=GZkJ-5M1W-pb4JcHv28vQpb81UbDKafB6nFC02L7DRtCFSSjemzDA9zdXBakvqAiaaPlpEvCkfhcdxBGTLGdz3Ol_Q3QUMy1YnbFXC6_EJgKKJTD4rH_wAHZZ-VF-bTY; __ac_nonce=0641bb227004f23017431; __ac_signature=_02B4Z6wo00f01Vg2irwAAIDAc7zReUlt4MlYFo4AADIZZmJo..WT14jnzqgsYOglQp7MOvjuICGBKaNgUiQL0Qg6Dgv0fs8KXAQvlh1JcMvKAPJkn0KTwq-jhWelwCGJ-GaJqG7wOo1tiV9Bb9; FOLLOW_LIVE_POINT_INFO="MS4wLjABAAAAEGPvhhLlz_9EAsl2Q4DE1Im2fppPCG8QzhTHhiO_AZY/1679587200000/0/0/1679537280601"; FOLLOW_NUMBER_YELLOW_POINT_INFO="MS4wLjABAAAAEGPvhhLlz_9EAsl2Q4DE1Im2fppPCG8QzhTHhiO_AZY/1679587200000/0/0/1679537880601"; home_can_add_dy_2_desktop="1"; tt_scid=1qPSdPTvWsQXr4EaWVZGuwPrfaDEM04BLX5ki3wF05TWV4aLxfIrI0FWg7yzVRx.0755; passport_fe_beating_status=false; msToken=S1b0l-i4Osgq55puDs5LPQkBegPLFQhAW7E5fyrAULCq20O06XvCZBKsASw-hnGayKdegTM1vncpmV1k-iOicwCfPOPt7Fw1zsWyJJCbpJAeA5S6qqwwXQo02woWHBPXwg==',
        "referer": "https://www.iesdouyin.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    this_url = clean_url(url)
    this_url = request_1(this_url)
    response = requests.get(url=this_url, headers=headers)

    html_data = re.findall('%22src%22%3A%22(.*?)%22%7D', response.text)[0]
    print(html_data)
    video_url = "https:"+requests.utils.unquote(html_data)
    title = re.findall(
        '<title data-react-helmet="true">(.*?)</title>', response.text)[0]
    video_content = requests.get(
        url=video_url, headers=headers, stream=True)
    con_length = round(int(video_content.headers['Content-Length'])/1024**2, 2)
    process_bar = tqdm(colour='blue', total=con_length,
                       unit='MB', desc=title, initial=0)

    with open(f'{title}.mp4', mode='wb') as f:
        for i in video_content.iter_content(chunk_size=1024**2):
            if i:
                f.write(i)
                process_bar.update(1)