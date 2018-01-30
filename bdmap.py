# -*- coding:utf-8 -*-
import json

from flask import current_app
from requests import request


class BDMap(object):
    def __init__(self):
        self.ak = 'jEWGp1H7LcHPmq1pPnpKXZMoNyOd0E7D' # current_app.config['AK']

    def get_dot(self, place):
        """
        获取地点纬度，经度
        :param place:
        :return: 纬度，经度
        """

        res = request('GET',
                      'http://api.map.baidu.com/geocoder/v2/?address='+place+'&output=json&ak='+self.ak+'&callback=showLocation')
        try:
            con = eval(res.content[26:])
        except SyntaxError:
            return (None, None)
        if con['status'] != 0:
            return (None,None)

        return con['result']['location']['lat'], con['result']['location']['lng'] if con['status'] == 0 else (
        None, None)

    def get_distance(self, fr, to='衡阳'):
        """
        计算两地距离
        :param fr: 出发地
        :param to: 目的地 默认衡阳
        :return: 距离 or False if exception
        """
        fr_lat, fr_lng = self.get_dot(fr)
        to_lat, to_lng = self.get_dot(to)
        if not fr_lat or not to_lat:
            return False

        res = request('GET',
                      'https://api.map.baidu.com/routematrix/v2/driving?output=json&origins={},{}&destinations={},{}&ak={}'.format(
                          fr_lat, fr_lng, to_lat, to_lng, self.ak))
        con = json.loads(res.content)
        if con['status'] != 0:
            return False
        return con['result'][0]['distance']['value'] / 1000


if __name__ == '__main__':
    print BDMap().get_distance('南昌')
