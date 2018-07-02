import requests
import re
import json
from requests.exceptions import RequestException
import pymongo

client = pymongo.MongoClient('localhost',27017)
movie_maoyan = client['maoyan']
movie_top100 = movie_maoyan['movie_top100']

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Referer':'http://maoyan.com'
}

# ================================================<<<<<<<<<单线程抓取>>>>>>>>>>==================================================
def get_one_page(url):
	response = requests.get(url,headers = headers)
	try:
		if response.status_code == 200:
			return response.text

		return None

	except RequestException:
		return None

def parse_one_page(html):
	pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>'
		+'.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
	items = re.findall(pattern,html)
	for item in items:
		yield {
			'index':item[0], # 排名
			'image':item[1], # 图片
			'title':item[2], # 电影名
			'star' :item[3], # 主演
			'time' :item[4], # 上映时间
			'score':item[5]+item[6] # 评分

		}


	# title = pattern.search(html)
	# if title:
	# 	print(title.group(1))

def write_to_file(item):
	movie_top100.insert_one(item) # 插入数据库
	print('Done')

	# 写入文本

	# with open('./maoyantop100.txt','a',encoding = 'utf-8') as f: # open函数中写入 encoding = 'UTF-8'参数，进行中文的识别
	# 	f.write(json.dumps(item,ensure_ascii = False)+'\n')  #  item 为字典结构，不能写入文件，需调用json中的dumps方法进行转换为字符串
	# 	f.close()
	# print('写入完成') # 此时写入文件中的是uniclod编码，不能显示中文，需要在json.dunps()中添加ensure_ascii = False

def main(offset):
	url = 'http://maoyan.com/board/4?offset='+str(offset)
	html = get_one_page(url)
	# print(html)
	for item in parse_one_page(html):
		write_to_file(item)


if __name__ == '__main__':
	for i in range(10):
		main(i*10)

# ================================================<<<<<<<<<多进程抓取>>>>>>>>>>==================================================
# 多进程需要进入multiprocessing模块中的Pool （进程池）
import requests
import re
import json
from requests.exceptions import RequestException # requests的异常处理机制
from multiprocessing import Pool
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
	'Referer':'http://maoyan.com'
}

def get_one_page(url):
	response = requests.get(url,headers = headers)
	try:
		if response.status_code == 200:
			return response.text

		return None

	except RequestException:
		return None

def parse_one_page(html):
	pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?src="(.*?)".*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>'
		+'.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
	items = re.findall(pattern,html)
	for item in items:
		yield {
			'index':item[0],
			'image':item[1],
			'title':item[2],
			'star' :item[3],
			'time' :item[4],
			'score':item[5]+item[6]

		}

def write_to_file(item):
	with open('./maoyantop100_1.txt','a',encoding = 'utf-8') as f: # open函数中写入 encoding = 'UTF-8'参数，进行中文的识别
		f.write(json.dumps(item,ensure_ascii = False)+'\n')  #  item 为字典结构，不能写入文件，需调用json中的dumps方法进行转换为字符串
		f.close()
	print('写入完成') # 此时写入文件中的是uniclod编码，不能显示中文，需要在json.dunps()中添加ensure_ascii = False

def main(offset):
	url = 'http://maoyan.com/board/4?offset='+str(offset)
	html = get_one_page(url)
	# print(html)
	for item in parse_one_page(html):
		write_to_file(item)


if __name__ == '__main__':
	pool = Pool()
	pool.map(main,[i*10 for i in range(10)])
