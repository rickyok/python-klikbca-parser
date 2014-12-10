#!/usr/bin/env python

import pycurl
import cStringIO
import json
import os
import sys
import urllib
import re
from datetime import date , timedelta

class BCA_parser(object):
	"""Parse klikbca untuk balance dan transaction"""

	def __init__(self, username , password):
		self.username = username
		self.password = password
		self.c = pycurl.Curl()
		# Init curl option
		self.c.setopt(self.c.USERAGENT , 'Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
		self.c.setopt(self.c.COOKIEFILE , self.file_location('cookie'))
		self.c.setopt(self.c.COOKIEJAR , self.file_location('cookiejar'))
		self.c.setopt(self.c.SSL_VERIFYHOST , 0)
		self.c.setopt(self.c.SSL_VERIFYPEER , 0)
		self.c.setopt(self.c.FOLLOWLOCATION , True)

		self.ip = self.curl_exec('http://ip.42.pl/raw')

		print "My IP : {}".format(self.ip)

	def file_location(self , filename):
		__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		return os.path.join(__location__, filename)

	def curl_exec(self , url , referer = '', params = {}, post = False):
		buff = cStringIO.StringIO()

		self.c.setopt(self.c.URL , url)
		self.c.setopt(self.c.REFERER , referer)
		self.c.setopt(self.c.WRITEFUNCTION , buff.write)

		if post:
			self.c.setopt(self.c.POSTFIELDS, urllib.urlencode(params))
			self.c.setopt(self.c.POST, 1 )

		self.c.perform()

		retval = buff.getvalue()
		buff.close()

		return retval

	def login(self):
		print "   --- Get login page ---"
		self.curl_exec('https://m.klikbca.com/login.jsp')

		params = {}
		params['value(user_id)'] = self.username
		params['value(pswd)'] = self.password
		params['value(Submit)'] = 'LOGIN'
		params['value(actions)'] = 'login'
		params['value(user_ip)'] = self.ip
		params['user_ip'] = self.ip
		params['value(mobile)'] = 'true'
		params['mobile'] = 'true'
		print "   --- Auth ---"
		retval = self.curl_exec('https://m.klikbca.com/authentication.do' , 'https://m.klikbca.com/login.jsp' , params , True)

		if "Informasi Rekening" in retval:
			return True
		else:
			print "Gagal login, mungkin sedang digunakan"
			return False
	def logout(self):
		print "   --- Logout ---"
		self.curl_exec('https://m.klikbca.com/authentication.do?value(actions)=logout' , 'https://m.klikbca.com/authentication.do?value(actions)=menu')

	def get_transactions(self):
		print "   --- Get Transaction ---"
		self.curl_exec('https://m.klikbca.com/accountstmt.do?value(actions)=menu' , 'https://m.klikbca.com/authentication.do')
		self.curl_exec('https://m.klikbca.com/accountstmt.do?value(actions)=acct_stmt' , 'https://m.klikbca.com/accountstmt.do?value(actions)=menu')

		today = date.today()
		fromdate = date.today() - timedelta(days=7)

		params = {}
		params['r1'] = 0
		params['value(D1)'] = 0
		params['value(startDt)'] = fromdate.day
		params['value(startMt)'] = fromdate.month
		params['value(startYr)'] = fromdate.year
		params['value(endDt)'] = today.day
		params['value(endMt)'] = today.month
		params['value(endYr)'] = today.year
		retval = self.curl_exec('https://m.klikbca.com/accountstmt.do?value(actions)=acctstmtview' , 'https://m.klikbca.com/accountstmt.do?value(actions)=acct_stmt' , params , True)

		# print retval

		pattern_balance = re.compile(r"<tr bgcolor='#(?:e0e0e0|f0f0f0)'><td valign='top'>([0-9/]+|PEND)<\/td><td>(.+)<td valign='top'>(DB|CR)<\/td>")
		match = pattern_balance.findall(retval)
		return match

	def get_balance(self):
		print "   --- Get Balance ---"
		self.curl_exec('https://m.klikbca.com/accountstmt.do?value(actions)=menu' , 'https://m.klikbca.com/authentication.do')
		retval = self.curl_exec('https://m.klikbca.com/balanceinquiry.do' , 'https://m.klikbca.com/accountstmt.do?value(actions)=menu')

		pattern_balance = re.compile(r"<td align='right'><font size='1' color='#0000a7'><b>([0-9,.]+)</td>")
		match = pattern_balance.search(retval)
		balance = 0
		if match:
			# print match.group(1)
			balance = float(match.group(1).replace(',' , ''))

		return balance

def main():
	bcaparser = BCA_parser('username' , 'password')

	if bcaparser.login():
		print bcaparser.get_balance()
		print bcaparser.get_transactions()
		bcaparser.logout()

if __name__ == '__main__':
	main()
