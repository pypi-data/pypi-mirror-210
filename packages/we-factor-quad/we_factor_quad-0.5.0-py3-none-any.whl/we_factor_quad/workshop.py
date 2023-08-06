# import numpy as np
# import pandas as pd
# from we_report.data_type import report_data
# import matplotlib.pyplot as plt
# from copy import deepcopy
# from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
# from typing import Union, List, Dict
# from we_factor_quad.test_settings import StocksOutputReport
# from we_factor_quad.test_settings import settings
#
# import pymysql
#
# # 连接数据库
# conn = pymysql.connect(host='172.16.127.213', port=3306, user='root', password='dev-project@mysql.', db='supersetdb')
#
# # 创建游标对象
# cursor = conn.cursor()
#
# # 执行SQL语句
# sql = 'SELECT * FROM supersetdb.StockRisk'
# cursor.execute(sql)
#
# # 获取查询结果
# result = cursor.fetchall()
# result = pd.DataFrame(result)
# result.columns = ['code', 'trade_date', 'msg_iVol', 'msg_Vol', 'close', 'forward_3m', 'msg_iVol_pct']
#
# from we_factor_quad.data_api import wiser_data_query_split
# # 获取股票名称
# param = {
#     'domain': 'sheet',
#     'phylum': 'ths',
#     'class': 'sec_basic_info',
#     'fields': ['SEC_ID', 'SEC_CODE', 'SEC_SHORT_NAME_CN'],
#     'start_date': '20230101',
#     'end_date': '20230102',
#     'codes': [],
#     'form': 'normal',
#     'filters': {
#         'SEC_TYPE': [f"= 'A股'"]
#     }
# }
# code_map_dict = wiser_data_query_split(param)[['SEC_CODE', 'SEC_SHORT_NAME_CN']].set_index('SEC_CODE')[
#     'SEC_SHORT_NAME_CN'].to_dict()
# result['name'] = [code_map_dict[i] for i in result['code'].str[:-3]]
# # 写入数据库
# from sqlalchemy import create_engine
# from urllib.parse import quote_plus as urlquote
#
# from sqlalchemy.orm import sessionmaker
#
# engine = create_engine(f"mysql+pymysql://root:{urlquote('dev-project@mysql.')}@172.16.127.213:3306/supersetdb")
#
# result.to_sql('StockRiskCopy', engine, if_exists='append', chunksize=100000, index=None)
# print('存入成功！')
#
# # 关闭游标和连接
# cursor.close()
# conn.close()
