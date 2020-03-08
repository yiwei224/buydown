import requests
from  lxml import etree

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/80.0.3987.132 Safari/537.36',
    'Referer':'http://13.231.90.159:8001/admin/login/?next=/admin/',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

url = 'http://13.231.90.159:8001/admin/login/?next=/admin/'
rs = requests.Session()
response = rs.get(url, headers=headers)

page = etree.HTML(response.text)
page = page.xpath('//input[1]/@value')
token = page[0]
data ={
    'csrfmiddlewaretoken': token,
    'username': 'admin', 'password': 'Raiser123'}
res = rs.post(url,headers=headers,data=data)
res2 = rs.get('http://13.231.90.159:8001/admin/api/order/',headers=headers)
print(res2.text)
