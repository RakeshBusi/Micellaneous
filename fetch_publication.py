import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
from bs4 import BeautifulSoup
import os
from datetime import date
ddd=date.today().strftime("%d/%m/%Y").replace('/','_')
try:
    os.mkdir(ddd)
except FileExistsError:
    print(f'Error {ddd} folder already exist')
    print(f'Possible solution: Delete the {ddd} folder')
    
# Website from the iitb online

url='https://iitb.irins.org/faculty/index/Department+of+Biosciences+and+Bioengineering'

response=requests.get(url,timeout=30)
soup=BeautifulSoup(response.text,'html.parser')
x=soup.find_all('div',{'class':'flat-testimonials-in md-margin-bottom-50 profileBox-heihgt'})

prof={}

for xi in x:
    y=xi.find('a',{'class':'btn-u btn-u-xs btn-u-sea mt10'})['href']
    z=xi.find('h3').get_text()
    w=xi.find('a',{'href':"#"}).get_text()
    wi=int(w.split(' ')[0])
    prof[z]=[y,wi]

driver=webdriver.Chrome('E:\Softies\chromedriver_win32\chromedriver')
driver.maximize_window()

for ek,ev in prof.items():
    driver.get(ev[0])
    print('Entered the Profile of ...',ek)
    c=0.5
    while True:
        try:
            publication=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT,'Publications')))
            publication.click()
            art=WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div#publication_div')))
            scroll_pause = c
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            pub=art.text
            no_pub=len(re.split('\n\s*\n',pub))
    #         no_pub=len(pub.split('\n\n'))
    #         print(no_pub,'......',ev[1])
            if no_pub != ev[1]:
                print('Number of publications not retrieved: ',ev[1]-no_pub)
                c+=0.5
            else:
                print('Number of publications retrieved: ',ev[1])
                break
        finally:
            time.sleep(0.5)
    #         break
    #         driver.quit()
    out=open(f'{ddd}/{ek}.txt','w',encoding='utf-8')
    out.write(ek+'\n')
    out.write('....................................................\n')
    out.write(pub+'\n')
    out.close()
    
driver.quit()   