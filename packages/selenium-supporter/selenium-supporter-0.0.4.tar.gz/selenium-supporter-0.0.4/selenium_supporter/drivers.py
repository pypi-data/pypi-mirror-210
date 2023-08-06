import platform
from PIL import Image
from io import StringIO
from PIL import Image
from io import BytesIO
from io import BytesIO
from pathlib import Path
import sys
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
try:
    import pyautogui
except:
    pass
import time
import sys
from python_supporter import logging
import getpass
import traceback

class ChromeDriver():
    #def __init__(self, user_data_dir="C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\".format(getpass.getuser()), profile_directory="Default"):
    #def __init__(self, user_data_dir, profile_directory):
    def __init__(self, user_data_dir=None):
    #def __init__(self):
        super().__init__()

        #executable_path = "chromedriver_98.0.4758.102/chromedriver.exe"
        executable_path = ChromeDriverManager().install()
        service = Service(executable_path=executable_path)
        if platform.system() == 'Windows': #윈도우
            from subprocess import CREATE_NO_WINDOW #윈도우에만
            service.creationflags = CREATE_NO_WINDOW #콘솔창 숨기기 https://stackoverflow.com/questions/66953190/selenium-hide-chromdriver-console-window

        options = webdriver.ChromeOptions() 
        #https://forum.katalon.com/t/open-browser-with-custom-profile/19268
        #'''
        #options.add_argument(f"user-data-dir={user_data_dir}")
        #options.add_argument(f"profile-directory=\"{profile_directory}\"")
        #print(f"profile-directory=\"{profile_directory}\"")
        #'''
        #user_data_dir="C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\Default".format(getpass.getuser())
        #options.add_argument(f"user-data-dir={user_data_dir}")



        '''
        #options.add_argument("user-data-dir=C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\".format(getpass.getuser()))
        options.add_argument("user-data-dir=C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data".format(getpass.getuser()))
        #options.add_argument("user-data-dir=\"C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 17\"".format(getpass.getuser())) #
        #options.add_argument("user-data-dir=\"C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\"".format(getpass.getuser())) #
        options.add_argument("profile-directory=\"Default\"")
        '''

        #!!
        #options.add_argument("user-data-dir=C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\".format(getpass.getuser()))

        if user_data_dir:
            options.add_argument(f"--user-data-dir=\"{user_data_dir}\"")

        #x
        #options.add_argument("user-data-dir=C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\User Data\\Default".format(getpass.getuser()))
        
        #x
        #options.add_argument("profile-directory=\"Default\"")

        #options.add_argument("--user-data-dir=\"D:\\크랜베리_제작\\작업 봇\\input\\chrome\"") #
        #options.add_argument("--profile-directory=\"Profile test\"")


        #options.add_argument("user-data-dir=\"D:\\크랜베리_제작\\작업 봇\\input\\chrome\\Profile test\"") #
        #options.add_argument("--disable-extensions") #



        #options.add_argument(f"user-data-dir={user_data_dir}\\{profile_directory}")
        


        #https://stackoverflow.com/questions/70534875/typeerror-init-got-an-unexpected-keyword-argument-service-error-using-p
        #https://www.pythonanywhere.com/forums/topic/29068/
        try: 
            self.driver = webdriver.Chrome(service=service, options=options) 
        except:
            logging.debug(traceback.format_exc())
            try: 
                self.driver = webdriver.Chrome(options=options)
            except:
                logging.debug(traceback.format_exc())
                self.driver = webdriver.Chrome(executable_path=executable_path, options=options)

    def get_driver(self):
        return self.driver

    def get(self, url):
        self.driver.get(url)

    def get_with_proxy_username_and_password(self, url, proxy_username, proxy_password):
        self.driver.get(url)
        if proxy_username and proxy_password:
            time.sleep(1)
            pyautogui.typewrite(proxy_username)
            pyautogui.press('tab')
            pyautogui.typewrite(proxy_password)
            pyautogui.press('enter')

class ChromeDebuggingDriver():
    def __init__(self, chrome_debugger_address=None):
        super().__init__()

        #executable_path = "chromedriver_98.0.4758.102/chromedriver.exe"
        executable_path = ChromeDriverManager().install()
        service = Service(executable_path=executable_path)
        if platform.system() == 'Windows': #윈도우
            from subprocess import CREATE_NO_WINDOW #윈도우에만
            service.creationflags = CREATE_NO_WINDOW #콘솔창 숨기기 https://stackoverflow.com/questions/66953190/selenium-hide-chromdriver-console-window

        options = webdriver.ChromeOptions() 
        if not chrome_debugger_address:
            chrome_debugger_address = "127.0.0.1:9222"
        options.add_experimental_option("debuggerAddress", chrome_debugger_address)

        #https://stackoverflow.com/questions/70534875/typeerror-init-got-an-unexpected-keyword-argument-service-error-using-p
        #https://www.pythonanywhere.com/forums/topic/29068/
        try: 
            self.driver = webdriver.Chrome(service=service, options=options) 
        except:
            try: 
                self.driver = webdriver.Chrome(options=options)
            except:
                self.driver = webdriver.Chrome(executable_path=executable_path, options=options)

    '''
    def __init__(self, proxy_server=None, proxy_username=None, proxy_password=None):
        super().__init__()
   
        self.proxy_server = proxy_server
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        #executable_path = "chromedriver_98.0.4758.102/chromedriver.exe"
        executable_path = ChromeDriverManager().install()
        service = Service(executable_path=executable_path)
        if platform.system() == 'Windows': #윈도우
            from subprocess import CREATE_NO_WINDOW #윈도우에만
            service.creationflags = CREATE_NO_WINDOW #콘솔창 숨기기 https://stackoverflow.com/questions/66953190/selenium-hide-chromdriver-console-window

        options = webdriver.ChromeOptions() 
        #https://botproxy.net/docs/how-to/setting-chromedriver-proxy-auth-with-selenium-using-python/
        if proxy_server:
            manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
            """

            background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
            """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

            options.add_argument(f"--proxy-server={self.proxy_server}")

        if self.proxy_username and self.proxy_password:
            pluginfile = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(pluginfile)
        
        #https://stackoverflow.com/questions/70534875/typeerror-init-got-an-unexpected-keyword-argument-service-error-using-p
        #https://www.pythonanywhere.com/forums/topic/29068/
        try: 
            self.driver = webdriver.Chrome(service=service, options=options) 
        except:
            try: 
                self.driver = webdriver.Chrome(options=options)
            except:
                self.driver = webdriver.Chrome(executable_path=executable_path, options=options)
    '''

    def get_driver(self):
        return self.driver

    def get(self, url):
        self.driver.get(url)

    def get_with_proxy_username_and_password(self, url, proxy_username, proxy_password):
        self.driver.get(url)
        if proxy_username and proxy_password:
            time.sleep(1)
            pyautogui.typewrite(proxy_username)
            pyautogui.press('tab')
            pyautogui.typewrite(proxy_password)
            pyautogui.press('enter')
