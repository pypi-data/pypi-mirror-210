
import requests, json, os
import base64,time

TOKEN_FILE_PATH=os.path.dirname(__file__) + "/metabypass.token"
class MetaBypass():

    def __init__(self,CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD):
        self.CLIENT_ID=CLIENT_ID
        self.CLIENT_SECRET=CLIENT_SECRET
        self.EMAIL=EMAIL
        self.PASSWORD=PASSWORD

    def getCredentials(self):
        cred=[self.CLIENT_ID,self.CLIENT_SECRET,self.EMAIL,self.PASSWORD]
        return  cred
    # -----------------------GET ACCESS TOKEN------------------------
    def getNewAccessToken(self):
        cred=self.getCredentials()
        CLIENT_ID, CLIENT_SECRET, EMAIL, PASSWORD = cred
        request_url = "https://app.metabypass.tech/CaptchaSolver/oauth/token"
        payload = json.dumps({
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": EMAIL,
            "password": PASSWORD
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST", request_url, headers=headers, data=payload)

        if response.status_code == 200:

            response_dict = json.loads(response.text)

            # store access token at cache file
            try:
                with open(TOKEN_FILE_PATH, 'w') as f:
                    f.write(response_dict['access_token'])
                    f.close()
                    return response_dict['access_token']
            except Exception as e:
                print(f"Error writing token to file: {e}")
                exit()

        else:
            print('unauth!')
            exit()

    def reCAPTCHAV2(self, url, site_key):
        request_url = "https://app.metabypass.tech/CaptchaSolver/api/v1/services/bypassReCaptcha"
        payload = json.dumps({
            "sitekey": f"{site_key}",
            "version": "2",
            "url": f"{url}",
        })
        # generate access token
        if os.path.exists(TOKEN_FILE_PATH):
            try:
                with open(TOKEN_FILE_PATH, 'r') as f:
                    access_token = f.read()
                    f.close()
            except Exception as e:
                print(f"Error writing token to file: {e}")
                exit()
        else:
            access_token = self.getNewAccessToken()

        # prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.request("POST", request_url, headers=headers, data=payload)

        if response.status_code == 401:
            access_token = self.getNewAccessToken()
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.request("POST", request_url, headers=headers, data=payload)
        try:
            recaptcha_id = json.loads(response.text)['data']['RecaptchaId']
        except:
            print('error!')
            print(response)
            exit()
        result=self.getResult(recaptcha_id)
        return result

    def getResult(self, recaptcha_id, step=0):
        if step == 0:
            time.sleep(10)

        request_url = "https://app.metabypass.tech/CaptchaSolver/api/v1/services/getCaptchaResult"

        payload = json.dumps({
            'recaptcha_id': recaptcha_id,
        })

        # generate access token
        if os.path.exists(TOKEN_FILE_PATH):
            try:
                with open(TOKEN_FILE_PATH, 'r') as f:
                    access_token = f.read()
                    f.close()
            except Exception as e:
                print(f"Error writing token to file: {e}")
                exit()
        else:
            access_token = self.getNewAccessToken()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.request("GET", request_url, headers=headers, data=payload)

        if response.status_code == 401:
            access_token = self.getNewAccessToken()
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.request("GET", request_url, headers=headers, data=payload)

        if response.status_code == 200:
            response_dict = json.loads(response.text)
            if response_dict['status_code'] == 200:
                return response_dict['data']['RecaptchaResponse']
            elif response_dict['status_code'] == 201:
                if step < 6:
                    print("result not ready")
                    time.sleep(10)
                    return self.getResult(recaptcha_id, step + 1)
                # print(response_dict['message']+'. wait 10 seconds again ...')
                else:
                    return False
            else:
                print(response_dict['message'])

        return False
