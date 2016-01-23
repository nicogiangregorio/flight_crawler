import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer:
	def __init__(self, smtp, port, user, pwd, authenticated):
		self.smtp = smtp
		self.port = port
		self.user = user
		self.pwd = pwd
		self.authenticated = authenticated

	def sendMail(self, from_addr, to, subject, body):
		msg = MIMEMultipart('alternative')
		msg['Subject'] = subject
		msg['From'] = from_addr
		msg['To'] = to
		
		part1 = MIMEText(body, 'plain')
		part2 = MIMEText(body, 'html')

		msg.attach(part1)
		msg.attach(part2)
		smtpserver = smtplib.SMTP(self.smtp,self.port)
		
		try:
			
			smtpserver.ehlo()
			smtpserver.starttls()
			smtpserver.ehlo
			
			if self.authenticated:
				smtpserver.login(self.user, self.pwd)
			smtpserver.sendmail(self.user, to, msg.as_string())
		except Exception, e:
			print e
		finally:
			smtpserver.quit()