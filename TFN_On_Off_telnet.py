# coding=utf-8
import httplib,urllib,re, time, ssl , sys
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def help():
	print 'TFN_On_Off_telnet <Destination IP> <port> <username> <password> <http,https>'
	print 'example:'
	print 'TFN_On_Off_telnet 1.1.1.1 443 root password https'
	print 'TFN_On_Off_telnet 1.1.1.1 80 root password http'
	sys.exit()

if len(sys.argv) < 6:
	help()
host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
Pass = sys.argv[4]
prot = sys.argv[5]

#連線前準備，GW位置
# host = '10.10.1.223'
# user = 'l'
# Pass = '1'
#排除網站阻擋
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
headers = { 'User-Agent' : user_agent}
#連線控制與URL

counter = 0

def http_get(data,prot):
	#列出來源頁面
	if prot == 'http':
		http_connect = httplib.HTTPConnection(host, port, timeout=10)	
	elif prot == 'https':
		http_connect = httplib.HTTPSConnection(host, port, timeout=10, context=ctx)	 	
	else:
		help()
	#print "<br>"
	#request(method, url, headers)
	#print (sub,headers)
	http_connect.request('GET', sub, '', headers)	
	#準備收取內容
	http_data = http_connect.getresponse()
	#Read page source html
	data = http_data.read()
	http_connect.close()
	#print data
	return data
	
	
def http_post(data,prot):
	#列出來源頁面
	if prot == 'http':
		http_connect = httplib.HTTPConnection(host, port, timeout=10)	
	elif prot == 'https':
		http_connect = httplib.HTTPSConnection(host, port, timeout=10, context=ctx)	 	
	else:
		help()
	#print "<br>"
	#request(method, url, body, headers)
	#print (host,sub,params,headers)	
	# http_data = urllib.urlopen(sub, params)
	http_connect.request('POST', sub, params, headers)	
	# 準備收取內容
	http_data = http_connect.getresponse()
	# Read page source html
	data = http_data.read()
	http_connect.close()
	#print data	
	return data
	
	
# sub = '/goform/LoginForm'
login_url = '/goform/LoginForm'
login_pass = 'username='+user+'&password='+Pass
status_url = '/CurrentStatusForm.asp'
telnet_url = '/goform/LoginAccountForm'
telnet_on = 'FORM_INDEX=0&HK627_0=0&K627_0=1'
telnet_off = 'FORM_INDEX=0&HK627_0=0'
get_telnet_url = '/LoginAccountForm.asp'
save_restart_url = '/goform/ConfigBackupLoadForm'
save_restart = 'FORM_INDEX=0&K48_0=1&K20_0=1&Config=ID_Reboot'
data = '123'

for i in range(1, 100, 1):


	#login page
	sub = "/LoginForm.asp"
	useless1 = http_get(data,prot)

	#login
	sub = login_url
	params = login_pass
	login_page = http_post(data,prot)
	print '登入中...'
	time.sleep(1)
	sub = "/LoginFirstPageForm.asp"
	useless2 = http_get(data,prot)
	# print login_page


	#getStatus
	sub = status_url
	getStatus = http_get(data,prot)
	# print "-----------------------------------"
	# print getStatus
	# print "-----------------------------------"
	getStatus_soup = BeautifulSoup(getStatus, "html.parser")
	getStatus_ex = getStatus_soup.find_all("script")
	# print getStatus_ex[2]
	getStatus_ex = str(getStatus_ex[2])
	getStatus_time_url = getStatus_ex.split('"')[3]
	# test = getStatus_time2.find('src')
	# print getStatus_time_url
	sub = getStatus_time_url
	poke_time_page = http_get(data,prot)
	# print "-----------------------------------"
	
	#system Information
	sub = '/goform/StatusLoad'
	params = 'FORM=SystemInformationForm'
	getinformation = http_post(data,prot)
	# print "-----------------------------------"
	# print getinformation
	# print "-----------------------------------"
	date_time = getinformation.split('"')[7]
	print date_time
	# firmware = getinformation.split('"')[87]
	# str.find(str, beg=0, end=len(string))
	firmware_head = getinformation.find('Ver(')
	firmware_tail = getinformation.find(' ',firmware_head+4)
	firmware = getinformation[firmware_head+4:firmware_tail]	
	# print firmware
	# set_firmware = '== Ver(1.2.38.97.12966 2016/03/02 16:03:39) PId(063.tfn.Huawei.NoPrefix.TR069.jumper25.drtp) Drv(1.4.2.252) Hw(SP9440OP) == '
	set_firmware = '1.2.38.97.12966'
	# set_firmware = '1.2.38.99.189'
	if firmware != set_firmware:
		continue
	else:
		# print 'OK'


		#check_telnet
		sub = get_telnet_url
		telnet_page = http_get(data,prot)
		#print telnet_page
		SRC_soup = BeautifulSoup(telnet_page, "html.parser")
		soup_out = SRC_soup.find(id='telnet_service')
		#<input checked="" class="INPUT_rightPlus8" name="K627_0" type="checkbox" value="1"> Enable Telnet Service </input></input></td> </tr> </tbody>
		#<input class="INPUT_rightPlus8" name="K627_0" type="checkbox" value="1"> Enable Telnet Service </input></input></td> </tr> </tbody>
		print '目前設定:' +str(soup_out)
		# checked = re.compile(u'checked')
		# checked = 'checked'
		# ref https://www.tutorialspoint.com/python/string_find.htm
		# Return -1 on failure
		check_tick = str(soup_out)
		tag_check = check_tick.find('checked')
		if tag_check > 0:
			# print 'tag position: '+str(tag_check)
			# print "Telnet 目前 ON "
			params = telnet_off
		else:
			# print tag_check
			# print "Telnet 目前 OFF "
			params = telnet_on

			
		# ON變OFF OFF變ON
		print '改變 Telnet... '
		time.sleep(3)
		sub = telnet_url
		telnet_page = http_post(data,prot)


		# double check telnet status
		print '確認設定中...'
		time.sleep(2)
		sub = get_telnet_url
		telnet_page2 = http_get(data,prot)
		# print "telnet_page2: "+str(telnet_page2)
		SRC_soup2 = BeautifulSoup(telnet_page2, "html.parser")
		soup_out2 = SRC_soup2.find(id='telnet_service')
		print "現在設定: "+str(soup_out2)
		check_tick2 = str(soup_out2)
		tag_check_confirm = check_tick2.find('checked')
		if tag_check != tag_check_confirm:
			counter = counter + 1
			print "設定成功並重開: "+str(counter) +" 次<br>"
		else:
			# goback and set again.	
			print "Fail! set again."
			

		#save and restart
		sub = save_restart_url
		params = save_restart
		save_restart_page = http_post(data,prot)
		sub = '/goform/ConfigBackupLoadForm'
		params = "Config=ID_CallReboot"
		restart_page = http_post(data,prot)
		print "<br>"
		time.sleep(45)