from knifes import times, randoms, jsons
import requests
import hashlib
token_safety_times = 1000 * 60 * 10  # 10min


def get_msg_common_params():
    return {
        'request_id': randoms.make_unique_str(),
        'settings': {
            'ttl': 43200000,  # 12 hours
        }
    }


class GeTui:
    def __init__(self, app_id, app_key, app_secret, master_secret):
        self.app_id = app_id
        self.app_key = app_key
        self.app_secret = app_secret
        self.master_secret = master_secret
        self.getui_api_base_url = f'https://restapi.getui.com/v2/{app_id}'
        self.token_expire_time = 0
        self.token = None

    # 透传消息(常用于用户在线时推送的事件)
    def push_transmission_msg(self, cid_list, payload):
        msg = {
            'push_message': {
                'transmission': payload
            }
        }
        msg_body = {**get_msg_common_params(), **msg}
        return self._push_msg(cid_list, msg_body)

    # 通知消息
    def push_notification_msg(self, cid_list, title, body, payload='{}', image_url=None):
        msg = {
            'push_message': {
                'notification': {
                    'title': title,
                    'body': body,
                    'click_type': 'payload',
                    'payload': payload,
                }
            },
            'push_channel': {
                'ios': {
                    'type': 'notify',
                    'aps': {
                        'alert': {
                            'title': title,
                            'body': body,
                        },
                        'content-available': 0,
                    },
                    'payload': payload
                }
            }
        }
        if image_url:
            msg['push_message']['notification']['big_image'] = image_url
            msg['push_channel']['ios']['multimedia'] = [{
                'url': image_url,
                'type': 1,
            }]
        msg_body = {**get_msg_common_params(), **msg}
        return self._push_msg(cid_list, msg_body)

    def _push_msg(self, cid_list, msg_body):
        if not cid_list:
            raise ValueError('missing cid param')
        if len(cid_list) == 1:
            return self._push_single(cid_list[0], msg_body)
        return self._push_batch(cid_list, msg_body)

    def _push_single(self, cid, msg_body):
        headers = {'token': self._get_token()}
        data = {
            'audience': {
                'cid': [cid]
            },
        }
        data = {**data, **msg_body}
        resp = requests.post(self.getui_api_base_url + '/push/single/cid', headers=headers, json=data, verify=False, timeout=10)
        j = resp.json()
        if j.get('code') != 0:
            raise Exception(f'个推推送消息失败,cid:{cid},params:{jsons.to_json(data)},resp:{resp.text}')

    def _push_batch(self, cid_list, msg_body):
        headers = {'token': self._get_token()}
        # 创建消息
        resp = requests.post(self.getui_api_base_url + '/push/list/message', headers=headers, json=msg_body, verify=False, timeout=10)
        j = resp.json()
        if j.get('code') != 0:
            raise Exception(f'个推创建消息失败,params:{jsons.to_json(msg_body)},resp:{resp.text}')
        task_id = j['data']['taskid']

        # 批量推送
        while len(cid_list) > 0:
            cid_slice_list = cid_list[:1000]
            cid_list = cid_list[1000:]
            data = {
                'audience': {
                    'cid': cid_slice_list  # cid数组，数组长度不大于1000
                },
                'taskid': task_id,
                'is_async': True
            }
            # 发送消息
            resp = requests.post(self.getui_api_base_url + '/push/list/cid', headers=headers, json=data, verify=False, timeout=10)
            j = resp.json()
            if j.get('code') != 0:
                raise Exception(f'个推批量推送消息失败,params:{jsons.to_json(data)},resp:{resp.text}')

    def _get_token(self):
        if self.token and self.token_expire_time > (times.current_milli_time() + token_safety_times):
            return self.token

        data = {
            'timestamp': str(times.current_milli_time()),
            'appkey': self.app_key
        }
        data['sign'] = hashlib.sha256((self.app_key + data['timestamp'] + self.master_secret).encode()).hexdigest()
        resp = requests.post(self.getui_api_base_url + '/auth', json=data, verify=False, timeout=10)
        j = resp.json()
        if j.get('code') != 0 or not j.get('data'):
            raise Exception(f'获取个推接口token失败: {resp.text}')
        data = j['data']
        self.token_expire_time = int(data['expire_time'])
        self.token = data['token']
        return self.token
