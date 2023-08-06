from future.utils import raise_
from .SecurityLayer import SecurityLayer
from .AuthAnswer import AuthAnswer
from cryptography.fernet import Fernet
from .Error import *
import os
import json
from .default import crypt as D20_SL_CRYPTOKEY

def api_back_auth(request=None, **kwargs):
    jr={}
    try:
        jr.update(kwargs.get('jr', {}))
    except:
        pass
    try:
        jr.update(request.form)
    except:
        pass
    if request != None and request.method != 'GET' and request.get_json() != None:
        jr.update(request.get_json())
    if request.headers.get('Authorization', '').split(" ")[0].upper() == 'BEARER':
        token_id = request.headers.get('Authorization').split(" ")[1]
        token = SecurityLayer.AccessToken(data= {'_key':token_id, 'origin' : request.headers.get('origin',request.headers.get('referer',''))})
        try:
            token.find()
        except HTTPError as e:
            AuthAnswer(False, error= e())
    elif request.headers.get('Authorization', '').split(" ")[0].upper() == 'BASIC':
        jr['apiuser'] = request.authorization.get('username')
        jr['apisecret'] = request.authorization.get('password')
        jr['origin'] = request.headers.get('origin',request.headers.get('referer',''))
        jr['permalink'] = kwargs.get('permalink', False)
        if jr.get('permalink', False) == True:
            jr['permalink'] = jr.get('permalink', False)
            jr['origin'] = jr.get('permalink_origin', jr['origin'])
        jr['oauth'] = kwargs.get('oauth', False)
        token = SecurityLayer.AccessToken(data=jr)
        try:
            token.auth()
        except HTTPError as e:
            AuthAnswer(False, error= e())
    elif (kwargs.get('oauth', False) == True or kwargs.get('file_req', False) == True) and request.args.get('client_id', '') != '':
        token_id = request.args.get('client_id', '')
        token = SecurityLayer.AccessToken(data= {'_key':token_id, 'origin' : request.headers.get('origin',request.headers.get('referer',''))})
        try:
            token.find()
        except HTTPError as e:
            AuthAnswer(False, error= e())
    else:
        return AuthAnswer(False, error= SSONoCredentialsError())
    if token.get('_key') == None:
        return AuthAnswer(False, error= SSOInvalidCredentialsError())
    if jr.get('permalink', False) == True and 'pl' not in token.get('actions') and 'sso' not in token.get('actions'):
        return AuthAnswer(False, error= SSONoPermalinksAllowedError())
    if 'action' in kwargs:
        if action_clearance(token, kwargs.get('action'),  jr=jr) != True:
            return AuthAnswer(False, error=  SSOAccessDeniedError(kwargs.get('action')))
    if 'clearance' in kwargs:
        if access_clearance(token, kwargs.get('clearance'), request.method, jr=jr) != True:
            return AuthAnswer(False, error=   SSOAccessDeniedError(kwargs.get('clearance'), request.method))
    if 'object_action' in kwargs:
        if object_action_clearance(token, kwargs.get('object_action'), request.method, jr=jr) != True:
            return AuthAnswer(False, error=   SSOAccessDeniedError(kwargs.get('clearance'), request.method))
    return AuthAnswer(True, token=token)

def user_back_auth(request=None, **kwargs):
    jr={}
    try:
        jr.update(kwargs.get('jr', {}))
    except:
        pass
    try:
        jr.update(request.form)
    except:
        pass
    if request != None and request.method != 'GET' and request.get_json() != None:
        jr.update(request.get_json())
    access_code = request.headers.get('Oauth-Token', request.headers.get('Access-Token', jr.get('Oauth-Token', jr.get('access_token', request.args.get('user_token', '')))))
    token_id = request.headers.get('UserToken', jr.get('UserToken', ''))
    user_id = request.headers.get('UserId', kwargs.get('UserId', jr.get('UserId', jr.get('_key', ''))))
    if token_id != '':
        token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': user_id})
        try:
            token.find()
        except HTTPError as e:
            AuthAnswer(False, error= e())
    elif jr.get('password', '') != '':
        token = SecurityLayer.UserToken(data=jr)
        try:
            token.auth()
        except HTTPError as e:
            AuthAnswer(False, error= e())
    elif jr.get('otp', '') != '':
        jr['password']=jr.get('otp', '')
        token = SecurityLayer.UserToken(data=jr)
        try:
            token.auth()
        except HTTPError:
            token_id = jr.get('otp')
            otp = SecurityLayer.OneTimeAccess(data= {'_key': token_id, 'username': jr['username']})
            try:
                otp.find()
                token = SecurityLayer.UserToken(data={'username': jr.get('username'), 'oauth': jr.get('oauth'), 'oauth_client': token.get('apiuser'), 'scopes': jr.get('scopes'), 'userid': otp.get('userid')})
                token.create()
            except HTTPError as e:
                AuthAnswer(False, error= e())           
    elif (kwargs.get('oauth', False) == True or kwargs.get('TPAMI', False) == True or kwargs.get('file_req', False) == True) and access_code != '':
        try:
            token = break_access_token(access_code)
        except:
            return AuthAnswer(False, error= SSOInvalidUserTokenError())
        # token = SecurityLayer.UserToken('find', {'_key': token_id, 'userid': userid})
        if token.get('status') != True:
            return AuthAnswer(False, error= SSOInvalidUserTokenError())
    else:
        return AuthAnswer(False, error= SSONoCredentialsError())
    if token.get("_key", None) == None:
        return AuthAnswer(False, error= SSOInvalidUserTokenError())
    if token.get('delegated', None) != None and delegated_clearance(token, request.method) != True:
        return AuthAnswer(False, error= SSOInvalidUserTokenError())
    return AuthAnswer(True, token=token)

def access_clearance(api_token: SecurityLayer.AccessToken, obj_type: str, action: str, **kwargs) -> bool:
    if not obj_type in api_token.get('allowed_types'):
        return False
    if action == 'PUT':
        permission = 'create'
    elif action == 'DELETE':
        permission = 'create'
    elif action == 'GET':
        permission = 'display'
    elif action == 'POST':
        permission = 'search'
    elif action == 'PATCH':
        permission = 'update'
    if not permission in api_token.get('allowed_types')[obj_type]:
        return False
    return True

def object_action_clearance(api_token: SecurityLayer.AccessToken, obj_type: str, action: str, **kwargs) -> bool:
    if not obj_type in api_token.get('allowed_types'):
        return False
    if action == 'PUT':
        permission = 'C'
    elif action == 'DELETE':
        permission = 'D'
    elif action == 'GET':
        permission = 'R'
    elif action == 'POST':
        permission = 'A'
    elif action == 'PATCH':
        permission = 'U'
    if api_token.get('allowed_types')[obj_type].find(permission) < 0:
        return False
    return True

def action_clearance(api_token: SecurityLayer.AccessToken, action: str, **kwargs) -> bool:
    return action in api_token.get('actions')

def scope_clearance(api_token: SecurityLayer.UserToken, scope: str, **kwargs) -> bool:
    return scope in api_token.get('scopes')

def delegated_clearance(user_token: SecurityLayer.UserToken, action: str, **kwargs) -> bool:
    if user_token.get('isadmin', False) == True:
        return True
    if action in ['GET', 'POST']:
        return True
    return user_token.get('can_write', False)

def action_user(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    return user_token.get('delegated', user_token.get('userid'))

def gen_access_token(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'{userid}.{tokenid}', 'utf-8')).decode()
    return access_token

def break_access_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    userid, token_id = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': userid})
    token.find()
    return token

def gen_refresh_token(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'{tokenid}.{userid}', 'utf-8')).decode()
    return access_token

def break_refresh_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    token_id, userid = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    token = SecurityLayer.UserToken(data={'_key': token_id, 'userid': userid})
    token.find()
    return token

def api_access_from_token(api_token: SecurityLayer.AccessToken) -> SecurityLayer.APIAccess:
    api_access = SecurityLayer.APIAccess(data={'username':api_token.get('apiuser')})
    api_access.load_multikey(['username'])
    return api_access

def gen_password_token(user_token: SecurityLayer.UserToken, **kwargs) -> str:
    userid = user_token.get('userid')
    tokenid = user_token.get('_key')
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    access_token = f.encrypt(bytes(f'passwordrec.{tokenid}.{userid}', 'utf-8')).decode()
    return access_token

def break_password_token(access_token:str) -> SecurityLayer.UserToken:
    crypt =  os.environ.get('CRYPTOKEY', D20_SL_CRYPTOKEY)

    f = Fernet(crypt)
    val, userid, token_id = f.decrypt(bytes(access_token, 'utf-8')).decode().split('.')
    if val != 'passwordrec':
        raise ObjectNotFoundException
    token = SecurityLayer.PasswordRecoveryToken(data={'_key': token_id, 'userid': userid})
    token.find()
    return token


