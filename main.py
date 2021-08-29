import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


# 前回のIPを保存するDB
PREVIOUS_IP_FILE = "previous_ip.json"

# Gmailアカウントの設定ファイル
CONFIG_FILE = "config.json"


# Gmailの設定
with open(CONFIG_FILE) as f:
    config = json.load(f)
SENDER_ADDRESS = config["from_address"]
PASSWORD = config["password"]
RECEIVER_ADDRESS = config["to_address"]
BCC = config["bcc"]
SUBJECT = config["subject"]


def create_message(sender_address, receiver_address, bcc_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = sender_address
    message["To"] = receiver_address
    message["Bcc"] = bcc_address
    message["Date"] = formatdate()

    return message


def send(sender_address, receiver_address, message):
    smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(SENDER_ADDRESS, PASSWORD)
    smtpobj.sendmail(sender_address, receiver_address, message.as_string())
    smtpobj.close()


def send_ip_info(ip_info):
    body = json.dumps(ip_info)
    message = create_message(SENDER_ADDRESS, RECEIVER_ADDRESS, BCC, SUBJECT, body)

    send(SENDER_ADDRESS, RECEIVER_ADDRESS, message)


def get_global_ip():
    url = "http://inet-ip.info/json"
    headers = {"content-type": "application/json"}
    result = requests.get(url, headers)
    data = result.json()

    return data["IP"]


def get_previous_ip_info(file_path):
    try:
        with open(file_path) as f:
            ip_info = json.load(f)
    except FileNotFoundError:
        print("file not found")
        ip_info = {}

    return ip_info


def write_current_ip(file_path, ip_info):
    with open(file_path, "w") as f:
        json.dump(ip_info, f, indent=4)


if __name__ == '__main__':
    previous_ip_info = get_previous_ip_info(PREVIOUS_IP_FILE)
    current_global_ip = get_global_ip()

    # グローバルIPが前回と変わっていたとき
    if previous_ip_info["global_ip"] != current_global_ip:

        # メール送信 
        send_ip_info({"global_ip": current_global_ip})

        # DB更新
        write_current_ip(PREVIOUS_IP_FILE, {"global_ip": current_global_ip})
