import requests, json, os

TOKEN_FILE_PATH = os.path.dirname(__file__) + "/metabypass.token"

def getCredentials(CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD):
    cred=[CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD]
    return cred
# -----------------------GET ACCESS TOKEN------------------------
def getNewAccessToken(cred):
    CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD=cred
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

        responseDict = json.loads(response.text)

        # store access token at cache file
        try:
            with open(TOKEN_FILE_PATH, 'w') as f:
                f.write(responseDict['access_token'])
                f.close()
                return responseDict['access_token']
        except Exception as e:
            print(f"Error writing token to file: {e}")
            exit()

    else:
        print('unauth!')
        exit()


# ----------------------------CALL reCAPTCHA v2-------------------------------
def reCAPTCHAV3(url, site_key,cred):
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
        access_token = getNewAccessToken(cred)

    # prepare headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("POST", request_url, headers=headers, data=payload)

    if response.status_code == 401:
        access_token = getNewAccessToken(cred)
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

