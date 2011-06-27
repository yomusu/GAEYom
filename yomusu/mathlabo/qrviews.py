#!/usr/bin/env python
# coding: utf-8


from django import http
from django import shortcuts

# for JSON
import django.utils.simplejson as json

from google.appengine.api import users


from yom import auth


# OK文字列
RESULT_OK = json.dumps( {"result":True} )

# パラメーターエラー文字列
PARAM_ERROR = json.dumps( {"result":False, "message":"param error"} )

# セッションエラー文字列
SESSION_ERROR = json.dumps( {"result":False, "message":"session error"} )

# インデックスエラー文字列
INDEX_ERROR = json.dumps( {"result":False, "message":"index error"} )

# 登録個数が最大エラー文字列
MAXIMUM_ERROR = json.dumps( {"result":False, "message":"no space"} )


# 最大登録数
MAX_FORMULA = 9


#--------------------------------------------------
# 非会員インデックス
def index( request ):
	return shortcuts.render_to_response('mathlabo/qrcode.html', {} )


#--------------------------------------------------
#
# 数式配列の最後に追加します
# 失敗することはありません
# 
# f = 数式
#
@auth.session_page
def add_qrcode( request, session=None ):
	
	"""数式を追加"""
	
	# サイズ制限
	
	# パラメーターの取得
	try:
		f = request.REQUEST['qrcode']
	except:
		return http.HttpResponse( PARAM_ERROR )
	
	# 追加処理
	try:
		a = session['qrcode']
		if len(a) >= MAX_FORMULA:
			return http.HttpResponse( MAXIMUM_ERROR )
		
		a.append( f )
		
	except KeyError:
		session['qrcode'] = [f,]
	
	return http.HttpResponse( RESULT_OK )


#--------------------------------------------------
# 数式の取得
@auth.session_page
def get_qrcode( request, session=None ):
	
	try:
		data = json.dumps({"result":True, "data":session['qrcode']})
		return http.HttpResponse( data, mimetype="application/json" )
	
	except KeyError:
		return http.HttpResponse( SESSION_ERROR )


#--------------------------------------------------
#
# 数式配列の指定したindexの数式を削除します
# 
# index = 配列のIndex
#
@auth.session_page
def delete_qrcode( request, session=None ):
	
	# パラメーターの取得
	try:
		i = int(request.GET['index'])
	except:
		return http.HttpResponse( PARAM_ERROR )
	
	# 削除処理
	try:
		a = session['qrcode']
		del a[i]
		return http.HttpResponse( RESULT_OK )
	
	except KeyError:
		return http.HttpResponse( SESSION_ERROR )
	except IndexError:
		return http.HttpResponse( INDEX_ERROR )


