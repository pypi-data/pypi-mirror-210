# -*- coding: utf-8 -*-
"""
@desc: a股指数
@author: yinchao
@time: 2023/5/23
@log: change log
"""
import copy

import pandas as pd
from bs4 import BeautifulSoup

from adata.common.headers import ths_headers
from adata.common.utils import cookie, requests


class StockIndex(object):
    """
    A股指数
    """

    def __init__(self) -> None:
        super().__init__()

    def all_index_code(self):
        """
        获取所有指数的代码
        :return: 指数信息[name,index_code，concept_code]
        """
        return self.__all_index_code_ths()

    def __all_index_code_ths(self):
        """
        获取同花顺所有行情中心的指数代码
        http://q.10jqka.com.cn/zs/
        :return: 指数信息[name,index_code，concept_code]
        """
        # 1. url拼接页码等参数
        data = []
        total_pages = 1
        curr_page = 1
        while curr_page <= total_pages:
            api_url = f"http://q.10jqka.com.cn/zs/index/field/zdf/order/desc/page/{curr_page}/ajax/1/"
            headers = copy.deepcopy(ths_headers.text_headers)
            headers['Cookie'] = cookie.ths_cookie()
            res = requests.request(method='get', url=api_url, headers=headers, proxies={})
            curr_page += 1
            # 2. 判断请求是否成功
            if res.status_code != 200:
                continue
            text = res.text
            soup = BeautifulSoup(text, 'html.parser')
            # 3 .获取总的页数
            if total_pages == 1:
                page_info = soup.find('span', {'class': 'page_info'})
                if page_info:
                    total_pages = int(page_info.text.split("/")[1])
            # 4. 解析数据
            page_data = []
            for idx, tr in enumerate(soup.find_all('tr')):
                if idx != 0:
                    tds = tr.find_all('td')
                    page_data.append({'index_code': tds[1].contents[0].text, 'short_name': tds[2].contents[0].text})
            data.extend(page_data)
        # 5. 封装数据
        if not data:
            return pd.DataFrame(data=data, columns=['index_code', 'short_name'])
        result_df = pd.DataFrame(data=data)
        data.clear()
        return result_df[['index_code', 'short_name']]


if __name__ == '__main__':
    print(StockIndex().all_index_code())
