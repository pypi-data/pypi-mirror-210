import time

import requests, json, os
import base64

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

    def image_captcha(self,image_file_path,numeric=0,min_len=0,max_len=0):
        with open(image_file_path, "rb") as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            image_file.close()
        request_url = "https://app.metabypass.tech/CaptchaSolver/api/v1/services/captchaSolver"
        payload = json.dumps({
            "image": f"{base64_data}", # PUT CORRECT BASE64 OF IMAGE
            "numeric": f"{numeric}",
            "min_len": f"{min_len}",
            "max_len": f"{max_len}",
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

        if response.status_code == 200:

            response_dict = json.loads(response.text)

            if response_dict['status_code'] == 200:
                return response_dict['data']['result']
            else:
                print(response_dict['message'])
                return False
        else:
            return False


     ###########################################################################################################################

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

    #################################################################################################################################

    def reCAPTCHAV3(self,url, site_key):
        request_url = "https://app.metabypass.tech/CaptchaSolver/api/v1/services/bypassReCaptcha"
        payload = json.dumps({
            "url": f"{url}",
            "sitekey": f"{site_key}",
            "version": "3",
        })

        # handle access token
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
        if response.status_code == 200:
            response_dict = json.loads(response.text)

            if response_dict['status_code'] == 200:
                return response_dict['data']['RecaptchaResponse']
            else:
                return False

        return False

