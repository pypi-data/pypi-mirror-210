import pandas as pd
import requests
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import email
import imaplib
import numpy as np
import re
from email.header import decode_header
import execjs
import json
import mimetypes
import smtplib   # 发送邮件模块
from email import encoders
from email.mime.multipart import MIMEMultipart    # 使用MIMEMultipart来标示这个邮件是多个部分组成的
from email.mime.base import MIMEBase
from email.mime.text import MIMEText   # 定义邮件内容
import  datetime
from email.utils import formataddr
import os.path
import sys
from zipfile import ZipFile
import zipfile
import os
import tushare as ts
if not os.path.exists(
        r'C:\Windows\AgentPool.xlsx'):
    print('注意注意！\n请确保存在\'C:\Windows\AgentPool.xlsx\'的ip代理文件\n否则，ip池功能将无法使用\n继续使用请敲击回车键')
class info():
    def show():
        print('测试成功，可以使用')
    def HowToUse():
        print('调用YesOrNot使用说明\nYesOrNot(ip,\'yes\'):表示调用改代理ip并进行检测\nYesOrNot(ip,\'\'):表示没有使用代理ip\n')
class function():
    def GetCityNumFromLiepin(place):
        ip = function.GetIpPool()
        ip = ip[random.randint(0, len(ip))]
        print('猎聘网正在查询城市编码')
        case=1
        OutNum=1
        while case==1:
            try:
                sheng = place[:place.find('省')]
                shi = place[place.find('省') + 1:place.find('市')]
                url = "https://apidok.liepin.com/api/com.liepin.bd.p.v3.get-all-dq"
                data = "sceneCode=6&from=component"
                header = {
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Client-Type": "web",
                    "X-Fscp-Fe-Version": "",
                    "X-Fscp-Version": "1.1",
                    "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Fscp-Trace-Id": "8136730b-00b0-4daa-b975-59728e3c2a5a",
                    "X-XSRF-TOKEN": "1vL6nJjVRCu01PAwwQmdEg"
                }
                data = requests.post(url, data=data, headers=header).json()
                name = data['data']['data']['city']['list']
                num = data['data']['data']['city']['relations']
                name = str(name)
                citysNum = num[str(((name.split(sheng)[0]).split('\'code\': \'')[-1])[:3])]
                for son in citysNum:
                    qu = ((name.split(str(shi))[0]).split('\'code\': \'')[-1])[:6]
                    cityName = \
                    (((name.split('\'' + str(qu) + '\', \'seoUri\': \'')[1]).split('\', \'category\'')[0])).split('\'')[-1]
                    if son == qu:
                        result = num[qu]
                        print('已经为你找到' + sheng + '省' + cityName + '市的所有区县，即将为你查询')
                        break
                    else:
                        result = []
                return result
                case=2
            except:
                OutNum=OutNum+1
                if OutNum==10:
                    print('抱歉，城市编码查询失败')
                    case=2
                else:
                    continue
    def GetIpPool():
        IpPool = []
        data = pd.read_excel(r'C:\Windows\AgentPool.xlsx')
        data = data.values.T.tolist()
        ip = data[0]
        port = data[1]
        type=data[2]
        for i in range(0, len(ip)):
            list = {}
            list[str(type[i])] = str(type[i])+'://'+str(ip[i]).replace(' ', '')+':'+str(port[i]).replace(' ', '')
            IpPool.append(list)
        return IpPool
    def GetCityNumFromBossZhiPing(city):
        ip = function.GetIpPool()
        ip = ip[random.randint(0, len(ip))]
        city=(city.split('省')[1]).split('市')[0]
        print('boss直聘查询说明\n本功能只能通过城市名字查询一个，关键词例如(宁波)，返回结果不是区的字典，只是当前城市代码。\n正在查询Boss的城市代码')
        res = requests.get('https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json',proxies=ip).json()
        res = str(res['zpData']['cityGroup'])
        res = (res.split(str(city))[0]).split('code\': ')[-1].replace(', \'name\': \'', '')
        res=[str(res)]
        return res
    def GetCityNameFromLiepin(num):
        ip = function.GetIpPool()
        ip = ip[random.randint(0, len(ip))]
        case = 1
        while case == 1:
            try:
                sheng = num[:num.find('省')]
                shi = num[num.find('省') + 1:num.find('市')]
                url = "https://apidok.liepin.com/api/com.liepin.bd.p.v3.get-all-dq"
                data = "sceneCode=6&from=component"
                header = {
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Client-Type": "web",
                    "X-Fscp-Fe-Version": "",
                    "X-Fscp-Version": "1.1",
                    "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-Fscp-Trace-Id": "8136730b-00b0-4daa-b975-59728e3c2a5a",
                    "X-XSRF-TOKEN": "1vL6nJjVRCu01PAwwQmdEg"
                }
                data = requests.post(url, data=data, headers=header, proxies=ip).json()
                data = str(data)
                data = data.split('\'sort\': \'' + str(num) + '\'')[1]
                data = data.split('\', \'name\': \'')[1]
                data = data.split('\', \'category\'')[0]
                case = 2
                return data
            except:
                continue
    def YesOrNot(ip,case):
        def get():
            jsdata = '''
            function r() {
            var e = 1 > 0 && void 0 !== 32 ? 32 : 32;
            console.assert(e >= 32, "最少需生成32位");
            var t = (new Date).getTime()
              , n = e < 32 ? 32 : e
              , r = new Array(n).join("x")
              , a = "".concat(r, "y").replace(/[xy]/g, (function(e) {
                var n = (t + 36 * Math.random()) % 36 | 0;
                return t = Math.floor(t / 36),
                ("x" == e ? n : 3 & n | 32).toString(36)
            }
            ));
            return a
        }'''
            sign = execjs.compile(jsdata).call('r')
            return sign
        def get_data(city, town, work, page, ip,townName):
            ckId_value = get()
            data = '{"data":{"mainSearchPcConditionForm":{"city":"' + str(city) + '","dq":"' + str(town) + '","pubTime":"","currentPage":"' + str(page) + '","pageSize":500,"key":"' + str(
                work) + '","suggestTag":"","workYearCode":"0","compId":"","compName":"","compTag":"","industry":"","salary":"","jobKind":"","compScale":"","compKind":"","compStage":"","eduLevel":"","otherCity":""},"passThroughForm":{"ckId":"' + str(
                ckId_value) + '","scene":"input","skId":"kidyjuir3x7rmen14hlz2kq1y9z6n3i3lqy","fkId":"kidyjuir3x7rmen14hlz2kq1y9z6n3i3lqy","sfrom":"search_job_pc"}}}'
            data = data.encode('utf-8')
            # print(data)
            header = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=utf-8;",
                "X-Client-Type": "web",
                "X-Fscp-Fe-Version": "",
                "X-Fscp-Version": "1.1",
                "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
                "X-Fscp-Bi-Stat": "{\"location\": \"https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime=&currentPage=0&pageSize=40&key=gs&suggestTag=&workYearCode=0&compId=&compName=&compTag=&industry=&salary=&jobKind=&compScale=&compKind=&compStage=&eduLevel=&otherCity=&sfrom=search_job_pc&scene=input&skId=xne9msayrzxkrk4njg7zq0ym8bfgoueb&fkId=xne9msayrzxkrk4njg7zq0ym8bfgoueb&ckId=" + str(
                    ckId_value) + "&suggestId=\"}",
                "X-Requested-With": "XMLHttpRequest",
                "X-Fscp-Trace-Id": "7400ed8f-fa5d-46b3-ae30-c7b1189ded7c",
                "X-XSRF-TOKEN": "q4fNe47HRBup-djOx7S_0Q"
            }
            url = 'https://apic.liepin.com/api/com.liepin.searchfront4c.pc-search-job'
            if case=='yes':
                data = requests.post(url, data=data, headers=header,proxies=ip)
            else:
                data = requests.post(url, data=data, headers=header)
            res = data
            res.encoding = 'utf-8'
            res=res.json()
            print(ip,res)
        get_data('070030','070030010','数据',0,ip,'温州')
    def CheckIp(ip):
        try:
            if str(ip)[2:7] != 'https':
                res = requests.get('http://httpbin.org/ip', proxies=ip)
                result = '可以'
            else:
                res = requests.get('https://blog.sina.com.cn/', proxies=ip)
                result = '可以'
        except:
            result = '不行'
        return result
    def IntoZip(dir_):
        with ZipFile(str(dir_) + '.zip', 'w') as z:
            z.write(dir_, arcname=(dn := os.path.basename(dir_)))
            for root, dirs, files in os.walk(dir_):
                for fn in files:
                    z.write(
                        fp := os.path.join(root, fn),
                        arcname=dn + '/' + os.path.relpath(fp, dir_)
                    )
        print('压缩成功，已经压缩到了文件夹:' + str(dir_) + '.zip')
    def ZipOut(dir, out):
        zf = zipfile.ZipFile(dir)
        os.chdir(out)
        ret = zf.extractall(path=out)  # 解压到指定目录
        print('解压成功')
    def SendEmail(name,password, receivers, text, sub, filepath):
        smtp_server = "smtp.qq.com"  # 发送邮箱服务器
        username = "yongxingkwok@foxmail.com"  # 用于发送邮箱的用户账号
        sender = 'yongxingkwok@foxmail.com'  # 发送者的邮箱
        EMAIL_FROM_NAME = name  # 自定义发件人名称
        time = datetime.datetime.today().strftime("%m-%d %H：%M")
        msg = MIMEMultipart()
        # 邮件正文
        msg.attach(MIMEText(str(text), 'plain', 'utf-8'))  # 文本内容换行\r\n
        msg['From'] = formataddr(pair=(EMAIL_FROM_NAME, sender))  # 自定义发件人的名称
        msg['To'] = ";".join(receivers)  # 发送给多个好友
        subject = str(sub).format(time)
        msg['Subject'] = subject
        if filepath != '':
            data = open(filepath, 'rb')
            ctype, encoding = mimetypes.guess_type(filepath)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(data.read())
            data.close()
            encoders.encode_base64(file_msg)  # 把附件编码
            file_msg.add_header('Content-Disposition', 'attachment',
                                filename=str(filepath.split('\\')[-1].split('.')[0]))  # 修改邮件头
            msg.attach(file_msg)
        server = smtplib.SMTP(smtp_server)
        server.login(username, password)
        server.sendmail(sender, receivers, msg.as_string())
        server.quit()
    def GetEmail(mail, password, dir):
        def decode_str(s):  # 字符编码转换
            value, charset = decode_header(s)[0]
            if charset:
                value = value.decode(charset)
                return value

        def get_email_title(msg):
            subject = email.header.decode_header(msg.get('subject'))
            if type(subject[-1][0]) == bytes:
                title = subject[-1][0].decode(str(subject[-1][1]))
            elif type(subject[-1][0]) == str:
                title = subject[-1][0]
            print("title:", title)
            return title

        def get_att(msg, dir):
            for part in msg.walk():
                # file_name = part.get_param("name")
                file_name = part.get_filename()
                if file_name:
                    h = email.header.Header(file_name)
                    dh = email.header.decode_header(h)
                    filename = dh[0][0]
                    if dh[0][1]:
                        filename = decode_str(str(filename, dh[0][1]))
                        data = part.get_payload(decode=True)
                        att_file = open(dir + file_name + '.zip', 'wb')
                        print('附件下载成功',file_name)
                        att_file.write(data)
                        att_file.close()

        """入口函数，登录imap服务"""
        server = imaplib.IMAP4_SSL('smtp.qq.com', 993)
        server.login(mail, password)
        server.select('INBOX')
        status, data = server.search(None, "ALL")
        if status != 'OK':
            raise Exception('read email error')
        emailids = data[0].split()
        mail_counts = len(emailids)
        # print("count:", mail_counts)
        # 邮件的遍历是按时间从后往前，这里我们选择最新的一封邮件
        for i in range(mail_counts - 1, mail_counts - 2, -2):
            status, edata = server.fetch(emailids[i], '(RFC822)')
            msg = email.message_from_bytes(edata[0][1])
            # 获取邮件主题title
            subject = email.header.decode_header(msg.get('subject'))
            if type(subject[-1][0]) == bytes:
                title = subject[-1][0].decode(str(subject[-1][1]))
            elif type(subject[-1][0]) == str:
                title = subject[-1][0]
            # print("title:", title)
            get_att(msg, dir)
    def ProgressBar(i, sum, printvalue):
        sys.stdout.write('\r')
        sys.stdout.write('{}%|{}{}|{}'.format(int(i / sum * 100), ((int(i / sum * 100))) * '■',
                                              (100 - int(i / sum * 100 + 1)) * '_', '当前打印：' + str(printvalue)))
        sys.stdout.flush()
    def GetPlateSon(num):
        if num == '':
            res = requests.get(r'https://hq.stock.sohu.com/pl/pl-1631.html?uid=1681655630543283qgz&548285357286').text
            res = json.loads(
                res.split('PEAK_ODIA(')[1].split(')</script>')[0].replace('\'pllist\',', '').replace('\'', '"'))
            info = ''
            for son in res:
                info = info + son[1] + ':' + son[0] + '、'
            print('请将所需板块的编号作为参数传入进来，具体信息如下：\n', info)
            input('')
        else:
            res = requests.get(r'https://q.stock.sohu.com/cn/bk_' + num + '.shtml').text
            res = res.split('</tbody>')[0].split('<tbody>')[1]
            res1 = res
            name = re.compile(r'>\d{6}<').findall(res1)
            res = re.compile(r'>[\u4e00-\u9fa5]+<').findall(res)
            '''>[\u4e00-\u9fa5]+<'''  # 匹配名称
            result1 = []
            for son in res:
                result1.append(son.replace('\'', '').replace('>', '').replace('<', ''))
            result2 = []
            for son1 in name:
                result2.append(son1.replace('\'', '').replace('>', '').replace('<', ''))
            result = {}
            result['代码'] = result2
            result['名称'] = result1
            return result
    def GetPlateInfo(PlateInfoName, url,code):
        def FindCode(codes):
            result = []
            pro = ts.pro_api(ApiCode)
            data = pro.daily(ts_code='')
            data = data.sort_values(by='ts_code')
            data = data['ts_code'].T.values.tolist()
            for i in range(0, len(data)):
                if data[i][:6] == codes:
                    result.append(data[i])
            return result

        a =function.GetPlateSon(PlateInfoName)
        ApiCode=code
        pro = ts.pro_api(ApiCode)
        print('正在下载' + str(PlateInfoName) + '板块的股票信息')
        for i in range(0, len(a['代码'])):
            code = FindCode(a['代码'][i])
            for son in code:
                data = pro.daily(ts_code=son)
                data.to_csv(r'{}\{}-{}.csv'.format(url, a['名称'][i], a['代码'][i]))
                function.ProgressBar(i, len(a['代码']), a['名称'][i])
    def MergeTable(data1, data2, on, data1name, data2name):
        data1 = pd.merge(data1, data2, on=on, how='outer')
        for i in range(0, len(list(data1))):
            data1 = data1.rename(
                columns={list(data1)[i]: list(data1)[i].replace('_x', data1name).replace('_y', data2name)})
        return data1
    def ChoiceColumn(date,name):
        date1=date.copy()
        if len(name)==0:
            print(list(date))
        else:
            for i in range(0,len(list(date))):
                if list(date)[i] in name:
                    pass
                else:
                    del(date1[list(date)[i]])
        return date1
class Model():
    def GetProbMatrix(df):
        name = []
        for son in df:
            if son not in name:
                name.append(son)
        result = []
        name = np.sort(name)
        for i in range(0, len(name)):  # 遍历行
            result.append([])
            for ii in range(0, len(name)):  # 遍历列
                result[i].append(0)
                # input(result)
                for iii in range(1, len(df)):
                    if df[iii - 1] == name[i] and df[iii] == name[ii]:
                        result[i][ii] = result[i][ii] + 1
            sum = np.sum(result[i])
            for iiii in range(len(result[i])):
                result[i][iiii] = result[i][iiii] / sum
            # print('sum is ',np.sum(result[i]),'序列',result[i],'\n')
        result = np.array(result)
        return result
    def ToMat(df):
        wide = df.shape[1]
        high = df.shape[0]
        df = df.values
        result = []
        size = []
        for i in range(0, high):
            for ii in range(0, wide):
                result.append([[df[i][ii]]])
            size.append(wide)
        back = [np.concatenate(result), size]
        return back
class spider():
    def Browser(url, show=False):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if show is False:
            options.add_argument('--headless')
        driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
          Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
          })
        """
        })
        driver.maximize_window()
        driver.get(url)
        return driver