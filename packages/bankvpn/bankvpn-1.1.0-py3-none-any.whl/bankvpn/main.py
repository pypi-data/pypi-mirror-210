import requests
import json
import re


# json=data query打印
# {'query': {'start_time': '1637656061249', 'end_time': '1640248061249', 'log_names': 'appbke.riskdecision-dev2-id3', 'sort': '@timestamp desc', 'basic': {'search': '\\"1640228649-33f02da3-ca17-4af4-8700-895896d59137-3481877\\"'}, 'filters': []}, 'relative_time_name': 'unit=Day&count=-30&referenceTime=now', 'with_highlights': True, 'page_size': 100, 'page_token': None}

def catch(url, authorization, cookie, query, tmp):
    # 查询url
    # url = 'https://log-nonlive.bke.shopee.io/v2/readapiserver_bke_id/logs/appbke.riskdecision-dev1-id3/query'
    # url = 'https://log.bke.shopee.io/v2/readapiserver_bke_id/logs/appbke.riskdecision-live-id3/query'
    header = {
        'authority': 'log-nonlive.bke.shopee.io',
        'method': 'POST',
        'path': '/v2/readapiserver_bke_id/logs/appbke.riskdecision-dev1-id3/query',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 认证信息
        # 'authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dfbmFtZXMiOlsiYXBwYmtlLnJpc2tkZWNpc2lvbi1kZXYxLWlkMyJdLCJwcm9qZWN0X25hbWVzIjpudWxsLCJleHAiOjE2NDEwOTA3NTUsImlhdCI6MTY0MDIyNjc1NX0.jzkGbgGcIbdz53Z8EKoD1YdwfrrR7hkcWNs-hSHGSIU',
        'authorization': authorization,
        'cache-control': 'no-cache',
        # 'content-length': '294',
        'content-type': 'application/json',
        # cookie
        # 'cookie': '_ga=GA1.2.320009075.1629283105; _fbp=fb.1.1629358768749.476342426; _rdt_uuid=1629358769030.8799da18-ee6b-4cee-aa85-d6a0aa0c6af4; G_ENABLED_IDPS=google; infra_platform_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImppYWd1aS5saW5Ac2hvcGVlLmNvbSIsIm5hbWUiOiJKaWFndWkgTGluIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBVFhBSnpxSE5YZjNJLVVBbFpwWmlaWGpfd0s1TjhUbkJtRXdGVjBRN1M2PXM5Ni1jIiwiUm9sZSI6MSwiZXhwIjoxNjQwMzI4NjI3LCJpYXQiOjE2Mzk0NjQ2Mjd9.wz9FqSn3Secktjw3qsaV7FZS5JX0FsoaCDnPaZ0mT3E; G_AUTHUSER_H=0; _gid=GA1.2.250339055.1640070164',
        'cookie': cookie,
        'origin': 'https://log-nonlive.bke.shopee.io',
        'pragma': 'no-cache',
        'referer': 'https://log-nonlive.bke.shopee.io/log-search?date-time=%7B%22type%22%3A%22rel%22%2C%22relativeTime%22%3A%22unit%3DDay%26count%3D-2%26referenceTime%3Dnow%22%2C%22start%22%3A1640160000000%2C%22end%22%3A1640163000999%7D&enable-long-history-search=0&log-chart-step=%221h%22&log-search-filters=%5B%5D&log-search-input=%22cost%22&search-condition=%7B%22logStores%22%3A%5B%22appbke.adminse-uat1-id3%22%5D%2C%22dateTime%22%3A%7B%22type%22%3A%22rel%22%2C%22relativeTime%22%3A%22unit%3DMin%26count%3D-30%26referenceTime%3Dnow%22%7D%2C%22timeZone%22%3A8%2C%22sqlOutputFormat%22%3A%22SQLOUTPUTFORMAT_TEXT%22%2C%22sqlSearchInput%22%3A%22%22%2C%22normalSearchInput%22%3A%22%22%2C%22filters%22%3A%5B%5D%2C%22longHistorySearch%22%3Afalse%7D&search-table-sort=%7B%22column%22%3A%22%40timestamp%22%7D&selected-logstores=appbke.riskdecision-dev2-id3&sql-output-format=SQLOUTPUTFORMAT_TEXT&sql-search-input=&time-zone=8',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    # 查询语句
    # data = '{"query":{"start_time":"1639620180000","end_time":"1639621964999","log_names":"appbke.riskdecision-dev1-id3","sort":"@timestamp desc","basic":{"search":""},"filters":[]},"with_highlights":true,"page_size":100,"page_token":null}'
    # data = '{"query":{"start_time":"1640145133000","end_time":"1640145556999","log_names":"appbke.riskdecision-live-id3","sort":"@timestamp desc","basic":{"search":"cost"},"filters":[]},"with_highlights":true,"page_size":100,"page_token":null}'
    query['query']['basic']['search'] = tmp
    # print(query)
    result = requests.post(url, json=query, headers=header)
    # print(result.content)
    result = result.json()
    return result


# print(result.content)
# print((result['instant_query_result']['entries'][0]))

set = {}
count = 0
totalRecord = 0


def dealData(result):
    # print(result)
    # print(result['instant_query_result'])
    print(result['instant_query_result']['entries'][0]['text_payload'])
    global count
    global totalRecord
    totalRecord += len(result['instant_query_result']['entries'])
    for i in range(len(result['instant_query_result']['entries'])):
        str = result['instant_query_result']['entries'][i]['text_payload']
        uid = str[str.index('"uid":') + 6: str.index(',')]
        if set.get(uid) == None:
            set[uid] = 1
        else:
            set[uid] = set[uid] + 1
        count += 1


def search(env, query, pageNum):
    if env == 'dev':
        url = dev1_url
        authorization = dev1_authorization
        cookie = dev1_cookie
    elif env == 'live':
        url = live_url
        authorization = live_authorization
        cookie = live_cookie

    tmp = re.findall(r'{"search":"(.*?)"}', query)[0]
    # print(tmp)
    query = query.replace(r'\"', '')
    query = json.loads(query)
    # print(query)
    for i in range(pageNum):
        result = catch(url, authorization, cookie, query, tmp)
        print(result)
        dealData(result)
        # 下一页
        query['page_token'] = result['instant_query_result'].get('next_page_token')
        if (query['page_token'] == None):
            print('page end,curr page:%s' % (i))
            break
    print(set)
    print(count)
    print(totalRecord)


# query中search不能含有正则相关字符

dev1_url = 'https://log-nonlive.bke.shopee.io/v2/readapiserver_bke_id/logs/appbke.riskdecision-dev1-id3/query'
dev1_authorization = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dfbmFtZXMiOlsiYXBwYmtlLnJpc2tkZWNpc2lvbi1kZXYxLWlkMyJdLCJwcm9qZWN0X25hbWVzIjpudWxsLCJleHAiOjE2NDEwOTA3NTUsImlhdCI6MTY0MDIyNjc1NX0.jzkGbgGcIbdz53Z8EKoD1YdwfrrR7hkcWNs-hSHGSIU'
dev1_cookie = '_ga=GA1.2.320009075.1629283105; _fbp=fb.1.1629358768749.476342426; _rdt_uuid=1629358769030.8799da18-ee6b-4cee-aa85-d6a0aa0c6af4; G_ENABLED_IDPS=google; infra_platform_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImppYWd1aS5saW5Ac2hvcGVlLmNvbSIsIm5hbWUiOiJKaWFndWkgTGluIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBVFhBSnpxSE5YZjNJLVVBbFpwWmlaWGpfd0s1TjhUbkJtRXdGVjBRN1M2PXM5Ni1jIiwiUm9sZSI6MSwiZXhwIjoxNjQwMzI4NjI3LCJpYXQiOjE2Mzk0NjQ2Mjd9.wz9FqSn3Secktjw3qsaV7FZS5JX0FsoaCDnPaZ0mT3E; G_AUTHUSER_H=0; _gid=GA1.2.250339055.1640070164'

live_url = 'https://log.id.seabank.io/v2/readapiserver_bke_id/logs/appbke.riskdecision-live-id3/query'
# live_authorization ='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dfbmFtZXMiOlsiYXBwYmtlLmF1dGhlbnRpY2F0aW9uY2VudGVyLWxpdmUtaWQzIl0sInByb2plY3RfbmFtZXMiOm51bGwsImV4cCI6MTY0MjI0NjM5MywiaWF0IjoxNjQxMzgyMzkzfQ.SRJl1E1kgemsHZfvctjPavD4NbUMoBDt2oGDHPaUIZg'
live_authorization = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dfbmFtZXMiOlsiYXBwYmtlLnJpc2tkZWNpc2lvbi1saXZlLWlkMyJdLCJwcm9qZWN0X25hbWVzIjpudWxsLCJleHAiOjE2NTgxNDI4NzcsImlhdCI6MTY1NzI3ODg3N30.x8Ur_abwan1cLRyq49gH47-9EkSGJH9qtjL1CuDuzmk'
# live_cookie ='_ga=GA1.2.320009075.1629283105; G_ENABLED_IDPS=google; G_AUTHUSER_H=0; _gid=GA1.2.652392368.1641363621; infra_platform_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImppYWd1aS5saW5Ac2hvcGVlLmNvbSIsIm5hbWUiOiJKaWFndWkgTGluIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBVFhBSnpxSE5YZjNJLVVBbFpwWmlaWGpfd0s1TjhUbkJtRXdGVjBRN1M2PXM5Ni1jIiwiUm9sZSI6MSwiZXhwIjoxNjQyMjQ0NDQ1LCJpYXQiOjE2NDEzODA0NDV9.OEjKXYy2Le5JhAD1C2l5fEtQ0U8IXITFY0F0zTnfjY0'
live_cookie = '_ga=GA1.2.320922174.1632381481; G_ENABLED_IDPS=google; G_AUTHUSER_H=0; infra_platform_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImppYWd1aS5saW5Ac2hvcGVlLmNvbSIsIm5hbWUiOiJKaWFndWkgTGluIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FJdGJ2bW5jZGFhTHFwTEFaMXFlYkNZUXZvZDk2enp3Qy1PLVlPVGlURGQ0PXM5Ni1jIiwiUm9sZSI6MSwiZXhwIjoxNjU4MTQyODc2LCJpYXQiOjE2NTcyNzg4NzZ9.DQM22Vpm3ix8se2ZchoXAoIBDJqh5JU9MGPflIRtYO8'

env = 'live'
# query = r'{"query":{"start_time":"1637656061249","end_time":"1640248061249","log_names":"appbke.riskdecision-dev2-id3","sort":"@timestamp desc","basic":{"search":"\"1640228649-33f02da3-ca17-4af4-8700-895896d59137-3481877\""},"filters":[]},"relative_time_name":"unit=Day&count=-30&referenceTime=now","with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"start_time":"1637656376107","end_time":"1640248376107","log_names":"appbke.riskdecision-dev2-id3","sort":"@timestamp desc","basic":{"search":"\"1640228649-33f02da3-ca17-4af4-8700-895896d59137-3481877\" AND \"cost\""},"filters":[]},"relative_time_name":"unit=Day&count=-30&referenceTime=now","with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"start_time":"1640067924000","end_time":"1640154328999","log_names":"appbke.riskdecision-live-id3","sort":"@timestamp desc","basic":{"search":"\"cost\" AND \"F94957E5-071A-4BE4-A5AF-C23F96E623BC\""},"filters":[]},"with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"start_time":"1640067924000","end_time":"1640154328999","log_names":"appbke.riskdecision-live-id3","sort":"@timestamp desc","basic":{"search":"\"cost\" AND \"F94957E5-071A-4BE4-A5AF-C23F96E623BC\" AND \"SUCCEED\""},"filters":[]},"with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"log_names":"appbke.authenticationcenter-live-id3","start_time":"1640534400000","end_time":"1641139199999","basic":{"search":"\"c.s.b.authentication.controller.OneTimePasswordController#verifyOneTimeLoginPassword \" AND \"error\""},"filters":[],"sort":"@timestamp desc"},"with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"log_names":"appbke.authenticationcenter-live-id3","start_time":"1640534400000","end_time":"1641139199999","basic":{"search":"\"OneTimePasswordController#verifyOneTimeLoginPassword\""},"filters":[],"sort":"@timestamp desc"},"with_highlights":true,"page_size":100,"page_token":null}'
# query = r'{"query":{"log_names":"appbke.authenticationcenter-live-id3","start_time":"1640534400000","end_time":"1641139199999","basic":{"search":" \"oneTimePasswordVerifyRequest\" AND \"verifyOneTimeLoginPassword\" AND \"success\""},"filters":[],"sort":"@timestamp desc"},"with_highlights":true,"page_size":100,"page_token":null}'
query = r'{"query":{"log_names":"appbke.riskdecision-live-id3","start_time":"1654012800000","end_time":"1655135999999","basic":{"search":"\"050b6537-afd0-4b53-b47d-7c5e9d50409f\""},"filters":[],"sort":"@timestamp desc"},"aggregations":[{"name":"1h","field":"@timestamp","field_type":"FIELD_TYPE_TIMESTAMP","type":"AGGREGATIONTYPE_GROUP","value":"{\"interval\":\"1h\",\"timezone\":\"+08:00\"}"}],"page_size":1}'
pageNum = 3
search(env, query, pageNum)


