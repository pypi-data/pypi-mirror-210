##function to get free edge points and run it every day at 2:00 am using selenium and cron job

import time

from selenium import webdriver
from selenium.webdriver import EdgeOptions

search_list= ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']

options = EdgeOptions()
options.add_argument('--user-data-dir=/home/malav/.config/microsoft-edge-dev')
driver = webdriver.Edge(options=options)

def bot():
    for i in search_list:
        url = 'https://www.google.com/search?q='+i
        driver.get(url)
        time.sleep(2)


