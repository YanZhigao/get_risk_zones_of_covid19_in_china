# -*- coding: utf-8 -*-
'''
@author: capsbot,
@time: 2022/01/19 15:05:07
@describe:从卫健委疫情风险等级查询网站（http://bmfw.www.gov.cn/yqfxdjcx/risk.html）中获得所有中高风险区并得到自己需要的文本格式并定时推送到企业微信机器人。
'''
import time
import json
import hashlib
import requests
# import schedule

# 设置企业微信机器人的webhook
webhook = os.environ['WEBHOOK']


def get_timestamp():
    timestamp = str(int(time.time()))
    return timestamp


def crypo_sha256(timestamp):
    e = timestamp
    a = '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA'
    i = '123456789abcdefg'
    s = 'zdww'
    str = (e + a + i + e).encode('utf-8')
    r = hashlib.sha256(str).hexdigest().upper()
    return r


def get_x_wif_signature(timestamp):
    str = (timestamp + 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA' +timestamp).encode('utf-8')
    r = hashlib.sha256(str).hexdigest().upper()
    return r

timestamp = get_timestamp()


def get_risk_zones():
    headers = {
    'x-wif-nonce': 'QkjjtiLM2dCratiA',
    'x-wif-signature': get_x_wif_signature(timestamp),
    'x-wif-timestamp': timestamp,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62',
    'x-wif-paasid': 'smt-application',
    'Content-Type': 'application/json; charset=UTF-8'}
    
    data = {
        'appId': 'NcApplication', 
        'paasHeader': 'zdww', 
        'timestampHeader': timestamp,
        'nonceHeader': '123456789abcdefg',
        'signatureHeader': crypo_sha256(timestamp),
        'key': '3C502C97ABDA40D0A60FBEE50FAAD1DA'}
    
    district_dict = {}
    
    try:
        res = requests.post('http://103.66.32.242:8005/zwfwMovePortal/interface/interfaceJson', headers = headers, data = json.dumps(data), verify = False)
        if res.status_code==200:
            res_json = res.json()
            msg = '目前有高风险地区{}个，中风险地区{}个，以下所列地区为中高风险地区。\n'.format(res_json['data']['hcount'],res_json['data']['mcount'])
            for i in range(2):
                if i == 0:
                    dict_to_do = res_json['data']['highlist']
                else:
                    dict_to_do = res_json['data']['middlelist']
                for district in dict_to_do:
                    province = district['province']
                    city = district['city']
                    county = district['county']
                    if province not in district_dict.keys():
                        district_dict[province] = {city:[county]}
                    else:
                        city_dict = district_dict[province]
                        if city not in city_dict.keys():
                            district_dict[province][city]=[county]
                        else:
                            if county not in city_dict[city]:
                                district_dict[province][city]=district_dict[province][city]+[county]
            for province in district_dict.keys():
                msg=msg+'\n\n《{}》\n\n'.format(province)
                province_dict = district_dict[province]
                for city in province_dict.keys():
                    msg = msg +'【{}】'.format(city)
                    county_list_str=''
                    county_list = province_dict[city]
                    for county in county_list:
                        county_list_str = county_list_str + county+'、'
                    if county_list_str[-1]=='、':
                        county_list_str = county_list_str[:len(county_list_str)-1]
                    msg=msg+county_list_str+'\n'
                msg = msg+'\n'
            return msg
        else:
            return res.status_code
    except Exception as e:
        return '{}'.format(e)


def push_report(msg):
    header = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    message_body = {
        "msgtype": "markdown",
        "markdown": {
            "content": msg
        },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    }
    send_data = json.dumps(message_body) 
    ChatBot = requests.post(url=webhook, data=send_data, headers=header)
    opener = ChatBot.json()
    if opener["errmsg"] == "ok":
        print(u"%s 通知消息发送成功！" % opener)
    else:
        print(u"通知消息发送失败，原因：{}".format(opener))


def job():
    risk_zones = get_risk_zones()
    print(risk_zones)
    if '高风险地区' in risk_zones:
        push_report(risk_zones)


if __name__ == '__main__':
    # schedule.every().day.at('09:09').do(job)
    # while True:
    #     schedule.run_pending()
    job()
    
