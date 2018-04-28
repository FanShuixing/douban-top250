import csv,os
import lxml.html
import urllib.request
import re
import urllib.parse
import pickle
from urllib.parse import quote
from html.parser import HTMLParser


				
class Downloader:
	def	__init__(self,cache):
		self.cache=cache
		
	def __call__(self,url):
		result=None
		if self.cache:
			try:
				#print('2')
				result=self.cache[url]
			except:
				pass
		if result==None:
			print(url)
			result=self.download(url)
			if self.cache:
				self.cache[url]=result
		return result
		
	def download(self,url,num_retry=2):
		headers={'User-agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)'}
		url=quote(url, safe='/:?=')
		request=urllib.request.Request(url,headers=headers)
		print('正在下载: '+str(url))
	
		try:
		
			html=urllib.request.urlopen(request).read()
		except urllib.error.HTTPError as e:
			if num_retry>0:
				if hasattr(e,'code') and 500<=e.code<600:
					download(url,num_retry=num_retry-1)
				else:
					html=None     #当页面出现4xx Not found错误时应当返回None，不然会出错
		return(html)
				
		
	
class DiskCache:
	def __init__(self,cache_dir='Cache'):
		self.cache_dir=cache_dir
	def __getitem__(self,url):
		path=self.url_to_path(url)
		if os.path.exists(path):
			with open(path,'rb') as fp:
				return pickle.load(fp)
		
	def __setitem__(self,url,result):
		path=self.url_to_path(url)
		folder=os.path.dirname(path)
		if  not os.path.exists(folder):
			os.makedirs(folder)
		with open(path,'wb') as fp:
			fp.write(pickle.dumps(result))
			
	def url_to_path(self,url):
		components=urllib.parse.urlsplit(url)
		path=components.path
		if not path:   #即path为空
			path='nihao'
		elif path.endswith('/'):
			path+='index.html'
		filename=components.netloc+path+components.query
		filename=re.sub('[^/0-9a-zA-Z\-.,;_]','_',filename)
		filename='/'.join(segment[:255] for segment in filename.split('/'))
		return(os.path.join(self.cache_dir,filename))
		
class novel_b:
	def __init__(self):
			self.writer=csv.writer(open('Dou2.csv','w'))
			self.rows=('book_name','author','grade','people','ISBN','定价')
			self.writer.writerow(self.rows)
			
	def __call__(self,url,html):
			#print('nihao')
			if (re.match('https://book.douban.com/subject/[\d]{7,8}/$',url)) :      #!!!这里不能使用self.url?
				#print('nihao')
				print(url)
				list=[]
				tree=lxml.html.fromstring(html)       #这里不能使用self.html?
				fixed_url=lxml.html.tostring(tree,pretty_print=True)
				pattern=re.compile('・|•|‧|∙')#这些字符在写入磁盘时会报UnicodeError错
				pattern1=re.compile('ç|Å')
				#书名
				book_name=tree.cssselect('div#wrapper>h1>span')[0].text
				if(pattern.findall(book_name)):
						book_name=re.sub(pattern,'.',book_name)
				list.append(book_name)
				#作者
				try:
					author=tree.cssselect('div#info>span>a')[0].text
					
					if(pattern.findall(author)):
						author=re.sub(pattern,'.',author)
					if pattern1.findall(author):
						author=re.sub(pattern1,'(拉丁)',author)
							
					list.append(author)
				except:
					author='作者不详'
					list.append(author)
				#豆瓣分数
				grade=tree.cssselect('div.rating_self.clearfix>strong.ll.rating_num')[0].text
				list.append(grade)
				#豆瓣评分人数
				try:
					db_people=tree.cssselect('div.rating_sum>span>a>span')[0].text
				except:
					try:
						db_people=tree.cssselect('div.rating_sum>span')[0].text
					except:
						db_people=tree.cssselect('span.color_gray')[0].text
				list.append(db_people)
				#ISBN
				pa=re.compile('<span class="pl">ISBN:</span>(.*?)<br>')
				fixed_url=fixed_url.decode('utf-8')
				for e in pa.findall(fixed_url):
					list.append(e)
				#定价
				#通过把正则改为<span class="pl">.*?<br>查看对应的&#
				pa=re.compile('<span class="pl">&#23450;&#20215;:</span>(.*?)<br>')
				for e in pa.findall(fixed_url):
					
					e=HTMLParser().unescape(e)
					#list.append(e) 
					pattern=re.compile('£')
					if(pattern.findall(e)):
						e_a=re.sub(pattern,'英镑',e)
						list.append(e_a)
					else:
						list.append(e)
				self.writer.writerow(list)
if __name__=='__main__':
	a=Downloader(DiskCache())
	a.download('https://book.douban.com/subject/1059336/')
