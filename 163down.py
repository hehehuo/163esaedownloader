import urllib.request
import urllib.parse
import json
import os
import wget
import eyed3
#全局变量（没求用）
global html
global max
global now
#写歌曲tag函数
def tag(path,artist,album,title):
	audiofile = eyed3.load(path)
	audiofile.tag.artist = artist
	audiofile.tag.album = album
	audiofile.tag.title = title
	print('下载完成 %d / %d，歌曲信息为\n标题：%s\n作者：%s\n专辑：%s\n' % (now,max,title,artist,album))
	audiofile.tag.save()
#是否返回主菜单函数
def gotomain():
	set = input('是否返回主菜单？Y/N 不区分大小写\n')
	if set == 'y' or set == 'Y':
		mainmenu()
	elif set =='n' or set =='N':
		print('退出程序')
	else:
		gotomain()					
#下载函数
def download(url,b): 
	file = open(b,mode='wb+')
	os.remove(b)
	file.close()
	wget.download(url, b)
#getApi接口函数
def getapi(a,b):
	request = urllib.request.Request("输入你自己的api链接"+ a +urllib.parse.quote(b))
	response = urllib.request.urlopen(request)
	global html
	html = response.read().decode('utf-8')
#搜索函数
def search(a):
	global max
	global now
	getapi('/search?keywords=' , a)
	jlist = json.loads(html)
	if jlist['code']==200:
		print('数据载入完毕，解析中\n')
		if 'result' in jlist:
			jlist = jlist['result']
			jlist = jlist['songs']
			i = 0
			while i < len(jlist):
				jj = jlist[i]
				i += 1
				print('第%d首\n曲名：%s'%(i,jj['name']))				
				for ii in jj['artists']:
					print('作者:' + ii['name'])
				print('\n')
			set=input('请选择您要下载第几首')
			if set.isnumeric() and int(set) <= i and int(set) >= 0 :
				jj = jlist[int(set)-1]
				id = jj['id']
				art1 = jj['artists']
				if len(art1) > 1:	
					art = ''
					cishu = 0
					for times in art1:
						if cishu < len(art1) - 1:
							art = times['name'] + '/' + art
						elif cishu == len(art1) - 1:
							art = art + times['name']
						cishu += 1
				elif len(art1) == 1:
					art = art1[0]
					art = art['name']
				print('歌曲Id为：%d'%(id))
				getapi('/check/music?id=%d'%(id),'')
				j = json.loads(html)
				if j['success']:
					getapi('/song/url?id=' + str(id),'')
					j = json.loads(html)
					if j['code'] == 200:
						path = os.getcwd()
						j = j['data']
						j = j[0]
						path = path+ '/music/'+jj['name'].replace('/','_') + '.mp3'
						print('\n您下载的音乐在' + path)
						download(j['url'],path)
						print(path)
						album = jj['album']
						now = 1
						max = 1
						tag(path,art,album['name'],jj['name'])
						gotomain()
					else:
						print('错误，网络代码为' + str(j['code'])+'\n')
						mainmenu()
				else:
					print('此歌曲不可用\n')
					mainmenu()
		else:
			print('没有找到相关歌曲\n')
			mainmenu()
	else:
		print(j['code']+'错误\n')
		mainmenu()
#歌单批量下载函数
def dwgd(link):
	global max
	global now
	pz = link.find('playlist/')
	if pz == -1:
		print('链接异常，请确认是否为歌单链接\n')
		mainmenu()
	else:
		link = link[pz+9:]
		playlistid = link[:link.find('/')]
		getapi('/playlist/detail?id=' + str(playlistid),'')
		h_j = json.loads(html)
		track = h_j['playlist']
		track = track['trackIds']
		idlist = []
		for i in track:
			idlist.append(i['id'])
		max = len(idlist) +1
		print('将要下载%d首歌曲'%(max))
		now =0
		for i in idlist:
			now += 1
			getapi('/song/url?id=' + str(i)+'&br=320000','')
			h_j = json.loads(html)
			h_j = h_j['data']
			h_j = h_j[0]
			id = h_j['id']
			url = h_j['url']
			type = h_j['type']
			getapi('/song/detail?ids=' + str(id),'')
			h_j = json.loads(html)
			h = h_j['songs']
			h = h[0]
			name = h['name']
			art1 = h['ar']
			if len(art1) > 1:	
				art = ''
				cishu = 0
				for times in art1:
					if cishu < len(art1) - 1:
						art = times['name'] + '/' + art
					elif cishu == len(art1) - 1:
						art = art + times['name']
					cishu += 1
			elif len(art1) == 1:
				art = art1[0]
				art = art['name']
			album = h['al']
			album = album['name']
			path = os.getcwd() + '/music/'+name.replace('/','_') + '.'+type
			download(url,path)
			tag(path,art,album,name)
		print('歌单获取完毕')
		gotomain()
#主菜单函数
def mainmenu():
	print('欢迎使用Python版网易云下载器')
	print('\n请选择您需要要的功能\n\n')
	print('1.搜索单曲并下载\n')
	print('2.通过歌单链接下载全部歌曲\n')
	print('其他功能开发中\n\n')
	set = input('请输入您要使用的的功能\n')
	if set == '1':
		s_str = input('请输入您要搜索的歌曲\n')
		print('加载中……')
		search(s_str)
	elif set == '2':
		s_str = input('请输入您的歌单链接#直接粘贴复制的内容\n')
		print('加载中……')
		dwgd(s_str)
	else:
		print('未知指令\n')
		mainmenu()
#
mainmenu()
