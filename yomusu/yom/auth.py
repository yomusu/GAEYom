#!/usr/bin/env python
# coding: utf-8

#import logging, os, sys

# dbサービス
from google.appengine.ext import db
from google.appengine.ext.db import Key
from google.appengine.api import users

# memcacheサービス
from google.appengine.api import memcache


import time,random
import hashlib



# MemcacheのNameSpace名
SESSION_NAMESPACE = "Session."

# キャシュする時間(秒)
MEMCACHE_TIME = 3600

# Cookieに使用するキー
COOKIE_KEY = "sessionkey"

# COOKIEのmax_age(秒)
MAX_AGE = 120 * 365 * 24 * 60 * 60


#-----------------------------------------------------------------
# memcacheを使用したセッション
class MemcacheSession:
	
	"""memcacheを使用したセッション"""
	
	def __init__( self, skey ):
		# セッションKey
		self.skey = skey
		# データ
		self._sp = {}
		
	
	def __getitem__( self, key ):
		return self._sp[key]
	
	def __setitem__( self, key, value ):
		self._sp[key] = value
	
	
	def dispose(self):
		"""セッションを終了する"""
		
		memcache.delete( self.skey, namespace=SESSION_NAMESPACE )
		
		self.skey = None
		self._sp = None
	
	
	def store(self):
		
		"""データストア更新"""
		
		# memcacheに登録
		memcache.replace( self.skey, self._sp, time=MEMCACHE_TIME, namespace=SESSION_NAMESPACE )
	
	
	def create(self):
		
		"""データストアに新規に作成"""
		
		def _create(self):
		
			# キーが存在して無ければ
			if memcache.get( self.skey, namespace=SESSION_NAMESPACE ) is None:
				# memcacheに登録
				memcache.add( self.skey, self._sp, time=MEMCACHE_TIME, namespace=SESSION_NAMESPACE )
				return True
			# すでに存在していれば失敗
			return False
		
		# トランザクション内で実行
		return db.run_in_transaction_custom_retries( 1, _create, self )

	
	
	def load(self):
		
		"""読み込み"""
		
		# memcacheから読み込み
		d = memcache.get( self.skey, namespace=SESSION_NAMESPACE )
		# 見つかった
		if d is not None:
			self._sp = d
			return True
		
		return False


#-----------------------------------------------------------------
# DataStoreを使用したセッション
class DataStoreSession:
	
	def __init__( self, skey ):
		# セッションKey
		self.skey = skey
		# データ
		self._sp = {}
	
	def __getitem__( self, key ):
		return self._sp[key]
	
	def __setitem__( self, key, value ):
		self._sp[key] = value
	
	
	
	def dispose(self):
		
		"""セッションを破棄する"""
		
		m = DataStoreSessionModel.get_by_key_name( self.skey )
		if m is not None:
			
			m.delete()
			
			# これ以降悪さをしないようメンバを無効にする
			self.skey = None
			self._sp = None
			
			return True
		
		return False
	
	
	# storeに失敗したらFalseを返します
	def store(self):
		
		"""データストア更新"""
		
		m = DataStoreSessionModel( key_name=self.skey )
		m.data = str(self._sp)
		m.put()
	
	
	def create(self):
		
		"""データストアに新規に作成"""
		
		def _create(self):
			
			# すでに存在の判定
			model = DataStoreSessionModel.get_by_key_name( self.skey )
			if model is None:
				
				# 新規作成
				m = DataStoreSessionModel( key_name=self.skey )
				m.data = str(self._sp)
				m.put()
				
				return True
			
			return False
		
		# トランザクション内で実行
		return db.run_in_transaction_custom_retries( 1, _create, self )
	
	
	def load(self):
		
		"""読み込み"""
		
		model = DataStoreSessionModel.get_by_key_name( self.skey )
		# 見つかった
		if model is not None:
			self._sp = eval(model.data)
			return True
		
		return False


class DataStoreSessionModel(db.Model):
	
	# 作成日時
	data = db.TextProperty()
	
	# 作成日時
	date = db.DateTimeProperty(auto_now_add=True)




#-----------------------------------------------------------------
# API


# セッションインスタンスを作成する
def session( skey ):
	"""セッションのコンストラクタ"""
	return DataStoreSession(skey)
#	return MemcacheSession(skey)



# セッションを新規に作成します
def create_new_session():
	
	s = session( create_session_key() )
	
	while s.create() == False:
		s = session( create_session_key() )
	
	return s


# セッションIDを作成します
def create_session_key():
	m = hashlib.sha224()
	m.update( str(time.localtime()) )
	m.update( str(random.randint(0,9999999)) )
	return "m"+m.hexdigest()


# セッション情報を検索して取得します
def search_session( sessionkey ):
	
	s = session( sessionkey )
	
	if s.load():
		return s
	
	# 見つからなかった
	return None



#---------------------------------


# セッションが記録される取り扱うページ
def session_page( func ):
	
	def login_checker( *args, **kwargs ):
		
		# HttpRequest
		req = args[0]
		
		s = None
		
		#-----------------
		# セッションIDをCookieから取得
		skey = req.COOKIES.get(COOKIE_KEY,None)
		
		# cookie情報があった場合セッションを取得
		if skey is not None:
			s = search_session( skey )
			
		# セッションが無ければ作成
		if s is None:
			s = create_new_session()
			# 基本的なユーザー情報を記録
			s['HTTP_USER_AGENT'] = req.META['HTTP_USER_AGENT']
			s['REMOTE_ADDR'] = req.META['REMOTE_ADDR']
		
		#-----------------
		# 引数にセッションを追加し関数呼び出し
		kwargs['session'] = s
		response = func( *args, **kwargs )
		
		#-----------------
		# 関数によってセッションが破棄される場合がある
		if s.skey is not None:
			
			# 破棄されて無ければセッション内容更新する
			s.store()
			
			# HttpResponseにセッションのためのcookieをセットする
			if response is not None:
				response.set_cookie( COOKIE_KEY, value=s.skey, max_age=MAX_AGE )
		
		else:
			
			# 破棄されているのでcookieを削除
			if response is not None:
				response.delete_cookie( COOKIE_KEY )
		
		return response
	
	
	return login_checker




#----------------------------------------------------

class Account(db.Expando):
	
	"""アカウント情報のクラス"""
	
	# key_nameと同じ内容をidが持っているのがカッコ悪い
	# なぜ持っているかというと、Modelを外部に直接渡していて、
	# そこでidという記述にてidを取得したいから。key().name()とかしたくない
	# でも、これってどうよ的な
	
	
	# ID = メンバーID
	id = db.StringProperty(multiline=False)
	
	# PW = メンバーPW
	pw = db.StringProperty(multiline=False)
	
	# 作成日時
	date = db.DateTimeProperty(auto_now_add=True)



#----------------------------------------------------
# ログイン
def login( session, id, pw ):
	
	# 指定されたIDでAccountを取得
	account = Account.get_by_key_name( id )
	
	# アカウントが存在するかどうか
	if account is not None:
		
		if account.pw == pw:
			
			# セッションにAccountのKeyを保存
			session['account_key'] = str( account.key() )
			
			return account
	
	return None


#-----------------------------------------------------
# 新規アカウントの作成
def create_new_account( id, pw ):
	
	"""新規Accountの作成"""
	
	# 指定されたIDが存在するか調査して作成
	def check_and_create( id ):
		
		model = Account.get_by_key_name( id )
		
		# すでに存在していたらNoneを返す
		if model is None:
		
			# DataStoreにModel作成
			model = Account( key_name=id )
			model.id = id
			model.pw = pw
			model.put()
			
			return model
		
		return None
	
	# トランザクション内で実行
	return db.run_in_transaction_custom_retries( 1, check_and_create, id )


#-----------------------------------------------------
# 会員のみ参照可能ページ
def account_lock( noaccountfunc ):

	"""会員のみ実行されるページ

	urlsに登録したPage表示関数にdecoして使います

	@account_lock( noaccountfunc )
	def func( request, session=None, account=None ):
		pass

	session = SessionCacheインスタンス
	account = Accountインスタンス
	noaccountfunc = セッションがない場合に呼ばれる関数

	"""
	def wrapper( func ):
		
		def memberable( *args, **kw ):
			
			# セッションからAccount情報を取得
			try:
				account = db.get( Key( kw['session']['account_key'] ) )
				if account is None:
					raise KeyError
				
			except KeyError:
				
				# セッションが正しくなかったり、
				# Accountがなければメンバーなしページの呼び出し
				return noaccountfunc( args[0] )
			
			else:
				# Accountがあれば、メンバーデータセットし
				kw['account'] = account
				
				# 元々の関数を呼び出す
				result = func( *args, **kw)
				
				# Accountデータを更新
				account.put()
				
				return result
		
		return session_page( memberable )
	
	return wrapper



