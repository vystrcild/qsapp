import requests
from qsapp.helpers import config

oauth_token = config()["oura"]["TOKEN_OURA"]
result = requests.get('https://api.ouraring.com/v1/userinfo?access_token=' + oauth_token)
result2 = requests.get('https://api.ouraring.com/v1/sleep?start=2020-11-12&end=2020-11-13&access_token=' + oauth_token)

print(result.content)
print(result2.content)
