#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   eleven.i386
#   E-mail  :   eleven.i386@gmail.com
#   WebSite :   eleveni386.7axu.com
#   Date    :   13/08/17 01:54:41
#   Desc    :   简易密码管理
#   FileName:   CLIPM

# 根据用户密钥加密密码;用sqlite保存密码

import os
import gnupg
from getpass import getuser
import time
import sqlite3
import sys
import getopt
import base64

class gpg():

	def __init__(self,GNUPGHOME='/home/%s/%s'%(getuser(),'.mypwd')):
		self.GNUPGHOME = GNUPGHOME
		self.g = gnupg.GPG(gnupghome = self.GNUPGHOME)

	def CreateCer(self, NAME_EMAIL, PASSPHRASE):
		input_data = self.g.gen_key_input(
               name_email = NAME_EMAIL,
               passphrase = PASSPHRASE)

		print "正在建立密钥.请稍等一会..."
		key = self.g.gen_key(input_data)
		print "建立完毕,密钥目录:%s"%self.GNUPGHOME

	def ImportKey(self, fp):
		key_data = open(fp,'rb').read()
		import_resut = self.g.import_keys(key_data)
		print "导入完毕"

	def Listkey(self):
		public_key = self.g.list_keys()
		private_key = self.g.list_keys(True)
		pub = public_key[0]
		private = private_key[0]

		print '%s\n%s'%(os.path.join(self.GNUPGHOME,'pubring.gpg'),\
				len(os.path.join(self.GNUPGHOME,'pubring.gpg'))*'-')

		print '%s\t%s\t%s'%(pub['type'],pub['keyid'],\
				time.strftime("%Y-%m-%d",time.localtime(float(pub['date']))))

		print '%s\t\t\t%s'%('uid',pub['uids'][0].split()[-1])

		print '%s\t%s\t%s'%(private['type'],private['keyid'],\
				time.strftime("%Y-%m-%d",time.localtime(float(private['date'])\
				)))

	def EncryptStr(self,unencrypt_str, uid):
		unencrypt_string = unencrypt_str
		encrypt_data = self.g.encrypt(unencrypt_string,uid)
		encrypt_string = str(encrypt_data.data)
		if encrypt_data.ok:return encrypt_string
		else:return encrypt_data.stderr
	
	def decryptStr(self,encrypt_str, pwd):
		encrypt_string = encrypt_str
		decrypt_data = self.g.decrypt(encrypt_string,passphrase=pwd)
		decrypt_string = str(decrypt_data.data)
		if decrypt_data.ok:return decrypt_string
		else:return decrypt_data.stderr

class manager():

	def __init__(self):
		try:
			self.sql = sqlite3.connect("/home/%s/.mypwd/mypwd.db"%\
									(getuser()))
			self.cur = self.sql.cursor()
			self.g = gpg()
		except sqlite3.Error, e:
			print "Error: %s"%e.args[0]
			print Help()
			sys.exit()

	def Init(self, email=None, pwd=None):
		"""建立数据库"""
		if email == None or pwd == None:Help();sys.exit()
		self.email = email.strip()
		self.passwd = pwd.strip()
		self.g.CreateCer(self.email, self.passwd)
		try:
			self.cur.execute(
							"create table myinfo(id integer primary key,\
							title varchar, \
							username varchar,\
							password varchar,\
							date varchar, \
							remark varchar);"
							)
			self.sql.commit()
			print "标识: %s\nkey: %s"%(
					self.email, base64.b64encode(self.passwd))
			print "请保管好,标识和key"
		except sqlite3.Error, e:
			if self.sql:self.sql.rollback()
			print "Error: %s"%e.args[0]
			sys.exit(1)
		finally:
			if self.sql:self.sql.close()

	def Insert(self, args):
		"""插入新记录"""
		keys = dict([(k,v) for k,v in [ i.split('=') for i in args ]])
		email = keys.get("email")
		if email:
			pwd = self.g.EncryptStr(keys.get("password"),email)
			try:
				self.cur.execute(
						"insert into myinfo values\
						(%s,'%s','%s','%s','%s','%s');"%\
						("null",\
						str(keys.get("title")),\
						str(keys.get("username")),\
						str(pwd),\
						str(time.strftime("%Y-%m-%d",time.localtime())),\
						str(keys.get("remark"))))
				self.sql.commit()
			except sqlite3.Error, e :
				if self.sql:self.sql.rollback()
				print "Error: %s"%e.args[0]
				sys.exit(1)
			finally:
				if self.sql:self.sql.close()
		else:Help();sys.exit(1)

	def Update(self, args):
		"""更新记录"""
		if len(args) < 2:Help();sys.exit(1)
		cmd = ""
		keys = dict([(k,v) for k,v in [ i.split('=') for i in args ]])
		if keys.get("password"):
			if keys.get("email"):
				keys["password"] = self.g.EncryptStr(keys.get("password"),\
													keys.get("email"))
				del keys["email"]
				cmd = "update myinfo set password='%s' where %s"%(
												keys.get("password"),\
												''.join([ i+"='"+keys[i]+"'" \
												for i in keys.keys() \
												if i != "password" ]))
			else:Help();sys.exit(1)
		else:
			cmd = "update myinfo set %s where %s"%(
				''.join(args[0].split("=")[0]+"='"+args[0].split("=")[1]+"'"),\
				''.join(args[1].split("=")[0]+"='"+args[1].split("=")[1]+"'"))
		try:
			self.cur.execute(cmd)
			self.sql.commit()
		except sqlite3.Error, e:
			if self.sql:self.sql.rollback()
			print "Error: %s"%e.args[0]
			sys.exit(1)
		finally:
			if self.sql:self.sql.close()

	def List(self):
		"""列出当前存储的记录"""
		count = 0
		try:
			data = self.cur.execute("select * from myinfo;").fetchall()
			if len(data) == 0:
				print "\n\tNo records ;-(\n\tplease insert new record\n"
				sys.exit(0)
			print "="*80
			print "ID\tTITLE\tUSERNAME\tPASSWORD\tDATE\tREMARK"
			print "-"*80
			for i in data:
				print "%s\t%s\t%s\t%s\t%s\t%s"%(
					str(i[0]),unicode(i[1]),"******","******",i[4],unicode(i[5]))
				count += 1
			print "-"*80
			print "Total: %s records"%(count)
			print "="*80
		except sqlite3.Error, e:
			if self.sql:self.sql.rollback()
			print "Error: %s"%e.args[0]
			Help()
			sys.exit(1)
		finally:
			if self.sql:self.sql.close()

	def Search(self,content=None, userkey=None):
		if content == None or userkey == None:Help;sys.exit(1)
		try:
			self.cur.execute(
					"select title,username,password from myinfo where title='%s' \
							limit 1;"%content)
			data = self.cur.fetchone()
			return self.g.decryptStr(data[2],base64.b64decode(userkey))
		except sqlite3.Error, e:
			if self.sql:self.sql.rollback()
			print "Error: %s"%e.args[0]
			sys.exit(1)
		finally:
			if self.sql: self.sql.close()

def Help():
	print """
	init   初始化数据库;
			usage: init email password
			请保留好 标识(email) 用于加密
			         key(password) 用于解密

	insert 插入新记录 ;
			insert title='',username='',password='',remark='',email=''
			email 必须使用 用于加密
			title,username,password,remark 可以为空

 	list   列出当前存储的记录

	update 修改记录 ;
			update title='',user='',password='',remark='',email=''
			当修改password时,email 不能为空,用于加密
			title,username,password,remark 必须且仅能使用两个

	%s title yourkey
	eleveni386
	"""%(sys.argv[0])

def main():
	clipm = manager()
	member = [ i.lower() for i in dir(clipm) if not i.startswith('__') ]
	if len(sys.argv) == 1:Help();sys.exit()
	try:
		if sys.argv[1] == "init":
			clipm.Init(sys.argv[2], sys.argv[3])
		if sys.argv[1] == "insert":
			clipm.Insert(sys.argv[2:])
		if sys.argv[1] == "update":
			clipm.Update(sys.argv[2:])
		if sys.argv[1] == "list":
			clipm.List()
		if sys.argv[1] not in member:
			print clipm.Search(sys.argv[1], sys.argv[2])
	except IndexError:
		Help()
		sys.exit(1)

if __name__ == "__main__":main()
