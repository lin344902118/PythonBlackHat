#coding:utf-8
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
	"""
	格式化邮件地址
	"""
	name, addr = parseaddr(s)
	return formataddr((Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, unicode) else addr))


from_email = 'lgh344902118@sina.com'
from_password = '344902118Lgh'
smtp_server = 'smtp.sina.com'
to_email = '344902118@qq.com'
log_name = 'test.log'

def send_email():
	"""
	定时查看日志,发现有错误及时发送邮件
	"""
	msg = MIMEText('你好,你的程序出了问题,请及时处理', 'plain', 'utf-8')
	msg['From'] = _format_addr(u'%s' %from_email)
	msg['To'] = _format_addr(u'%s' %to_email)
	msg['Subject'] = Header(u'来自服务器xxx', 'utf-8').encode()


	server = smtplib.SMTP(smtp_server, 25)
	server.starttls()
	server.set_debuglevel(1)
	server.login(from_email, from_password)
	server.sendmail(from_email, [to_email], msg.as_string())
	server.quit()

def check_log():
	with open(log_name, 'r') as f:
		contents = f.readlines()
	print contents
	check_contents = contents[-100:]
	print check_contents
	for content in check_contents:
		if 'Traceback' in content:
			send_email()
			break

if __name__ == '__main__':
	check_log()