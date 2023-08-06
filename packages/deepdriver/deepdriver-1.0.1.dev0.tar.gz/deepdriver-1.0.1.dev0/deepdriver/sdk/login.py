from assertpy import assert_that
import requests
from deepdriver.sdk.interface import interface
from deepdriver import logger
from deepdriver.sdk import util
# deepdriver 실험환경을 사용하기위한 로그인 과정
# 서버의 login api를 호출하여 key를 서버로 전송하고 결과로서 jwt key를 받는다


def login_with():
    if util.is_notebook():
        import ipywidgets as widgets
        selected_login_method = widgets.Combobox(
            # value='John',
            placeholder='--select login method--',
            options=['google', 'email'],
            description='Choose : ',
            ensure_option=True,
            disabled=False
        )
        def on_change(change):
            if change['type'] == 'change' and change['name'] == 'value':
                if change['new']=='google':
                    method ='g'
                else:
                    method = 'e'
                interface.set_login_method(method)
        selected_login_method.observe(on_change)
        display(selected_login_method)


    else:
        login_with_google = input(
            'login with Google: \n( Enter "g" to sign in with Google.If other characters are entered, email login proceeds.)')
        interface.set_login_method(login_with_google)
def login(key: str=None, id: str =None, pw: str=None, method: str=None) -> (bool, str):
    #assert_that(key).is_not_none()
    gtoken = None
    if method is None:
        login_method = interface.get_login_method()
    else:
        login_method = method
    if key is None and id is None:
        if login_method == "e":
            import getpass

            id = input('Enter your email:')
            pw = getpass.getpass('Enter your password:')
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow

            client_secrets_file = None
            import os
            import site

            for path in site.getsitepackages():
                if os.path.isfile(path + "/deepdriver/" + "client_secrets.json"):
                    client_secrets_file = path + "/deepdriver/" + "client_secrets.json"
            assert_that(client_secrets_file).is_not_none()

            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file,
                scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile',
                        'https://www.googleapis.com/auth/userinfo.email'], redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            auth_url, _ = flow.authorization_url(prompt='consent')

            print('Please go to this URL: {}'.format(auth_url))
            code = input('Enter the authorization code: ')
            a = flow.fetch_token(code=code)
            gtoken = a['id_token']

            # You can use flow.credentials, or you can just get a requests session
            # using flow.authorized_session.
            session = flow.authorized_session()
            user_info = session.get('https://www.googleapis.com/userinfo/v2/me').json()
            id = user_info["email"]

        try:
            return interface.login(key, id, pw, gtoken)[0]
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            logger.error(f"Could Login to Server[{interface.get_http_host()}]. Set Server IP/PORT using deepdriver.setting()")
            return False
    else:
        try:
            return interface.login(key, id, pw)[0]
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            logger.error(
                f"Could Login to Server[{interface.get_http_host()}]. Set Server IP/PORT using deepdriver.setting()")
            return False







