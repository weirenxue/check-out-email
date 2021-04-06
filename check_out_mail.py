import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
import json
from datetime import datetime

def send_email(subject, content):
        sender = json.load(open("./mailFrom.json", "r", encoding="utf-8"))
        gmailUser = sender["account"]
        gmailPass = sender["password"]
        to = json.load(open("./mailTo.json", "r", encoding="utf-8"))

        # create message
        message = MIMEText(content, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = gmailUser
        message["To"] = ','.join(to)

        # set smtp
        smtp = smtplib.SMTP("smtp.gmail.com:587")
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmailUser, gmailPass)  # 登入寄件者gmail

        # send mail
        smtp.sendmail(message["From"], to, message.as_string())

try:
    #get session at 9/18/2020 8:47PM
    s_account = json.load(open("./sAccount.json", "r", encoding="utf-8"))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",}
    payload = {"userid":s_account["account"], "password":s_account["password"], "submit":"登入", "refer":"https://pv.ncnu.edu.tw/EIP/Login/LoginGetNCNU.resource.aspx"}

    #response = requests.post( url, headers = headers, data = payload)

    sess = requests.Session()
    sess.headers.update(headers)

    #login
    url = "https://ccweb.ncnu.edu.tw/pv/actionlogin.aspx"
    response = sess.post(url, data=payload)

    #get iframe content
    while 1:
        url = "https://pv.ncnu.edu.tw/EIP/Resource/Dashboard_ncnu.resource.aspx"
        response = sess.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        today_last_td = None
        for this_tr in soup.find(id = "PersonalDuty_DataGrid").find_all("tr"):
            if(this_tr.find_all("td")[0].text == datetime.now().strftime("%Y-%m-%d")):
                today_last_td = this_tr.find_all("td")[-1]
                break
            
        if today_last_td is None:
            break
        #get check-in record of the day
        url = "https://pv.ncnu.edu.tw/EIP/Resource/" + today_last_td.a["href"]
        response = sess.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        maybe_offwork = soup.find_all("tr")[-2].find_all("td")
        maybe_onwork = soup.find_all("tr")[4].find_all("td")
        
        if maybe_onwork[1].text == "上班簽到":
            if maybe_offwork[1].text == "下班簽退":
                content = "!狂賀!!恭喜下班!!!" + "\n時間:" + maybe_offwork[2].text +"\n地點:" + maybe_offwork[-3].text
                send_email("通知:" + maybe_offwork[0].text + "下班簽退@" + maybe_offwork[2].text, content)
                #print(content)
                break
        else:
            break

        time.sleep(10)  
        
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "已打卡!")
except Exception as e:
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), e, e.with_traceback)