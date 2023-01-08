import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import date, datetime, timedelta
import sys
import os
import shutil
from PIL import Image
import pytesseract

timeframe = ""

def main():
    global timeframe

    #Selenium Webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    chrome_options.add_argument("--ignore-certification-errors")
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options ,service=Service(ChromeDriverManager().install()))


    #Enter start/end
    try:
        print("""
 _____                 _              _              ______      _        
/  ___|               | |            (_)             |  _  \    | |       
\ `--. _ __ ___   ___ | | _____ _ __  _ _ __   __ _  | | | |__ _| |_ __ _ 
 `--. \ '_ ` _ \ / _ \| |/ / _ \ '_ \| | '_ \ / _` | | | | / _` | __/ _` |
/\__/ / | | | | | (_) |   <  __/ |_) | | | | | (_| | | |/ / (_| | || (_| |
\____/|_| |_| |_|\___/|_|\_\___| .__/|_|_| |_|\__, | |___/ \__,_|\__\__,_|
                               | |             __/ |                      
                               |_|            |___/                                                                                                      
          """)
        choice = int(input("\nChoose the timeframe:\n 1 - Today:\n 2 - Yesterday:\n 3 - Last week:\n 4 - Last Month: \n 5 - Custom: \n 6 - Exit \n\n "))
        if choice == 1:
            print("\n")
            today = date.today()
            print("Getting data for: ", today)
            smoke_start = today
            smoke_end = ""
            data_date = timeframe = smoke_start


        elif choice == 2:
            print("\n")
            today = date.today()
            yesterday = today - timedelta(days = 1)
            print("Getting data for: ", yesterday)
            smoke_start = yesterday
            smoke_end = ""
            data_date = timeframe = smoke_start

        elif choice == 3:
            print("\n")
            today = date.today()
            lastweek = today - timedelta(days = 7)
            print("Getting data for: ", lastweek)
            smoke_start = lastweek
            smoke_end = ""
            data_date = timeframe = smoke_start

        elif choice == 4:
            print("\n")
            today = date.today()
            lastmonth = today - timedelta(days = 30)
            print("Getting data for: ", lastmonth)
            smoke_start = lastmonth
            smoke_end = ""
            data_date = timeframe = smoke_start

        elif choice == 5:
            print("\n")
            format = ("%Y-%m-%d")
            smoke_start = (input("Start Time (yyyy-mm-dd format): "))
            smoke_end = (input("End Time (yyyy-mm-dd format): "))

            try:
                datetime.strptime(smoke_start, format)
                datetime.strptime(smoke_end, format)
                print("This is the correct date string format.")
            except ValueError:
                print("This is an incorrect date string format. It should be YYYY-MM-DD")
                sys.exit()

            print("Getting data from: " + str(smoke_start) + " to: " + str(smoke_end))
            data_date = timeframe = smoke_start

        elif choice == 6:
            sys.exit(0)
        else:
            print("Invalid input.")
            sys.exit()
    except ValueError:
        print("Invalid input.")
        sys.exit()

    # providing smokeping url
    url = ("https://smokeping.as20565.net/")

    # Creating request object
    req = requests.get(url)
    
    # Creating soup object
    data = BeautifulSoup(req.text, 'lxml')
    data1 = data.find('ul')
    for a in data1.find_all('a', href=True):
        newurl = (url + a['href'])

        req2 = requests.get(newurl)
        data2 = BeautifulSoup(req2.text, 'lxml')

        productDivs = data2.findAll('div', attrs={'class' : 'panel-body'})
        for div in productDivs:
            data_names = (div.a['href'])

            smoke_link = (url + "?displaymode=n;start=" + str(smoke_start) + ";" + str(smoke_end) + ";" + data_names[1:])
            file_names = data_names[8:]
            print(smoke_link)

            driver.get(smoke_link)
            with open(file_names + ".png", "wb") as file:
                try:
                    file.write(driver.find_element(By.XPATH, '//*[@id="zoom"]').screenshot_as_png)
                except NoSuchElementException:
                    print("Exception Handled")


    driver.close
    return data_date


path = (r"D:\Files\smokeping project")
newpath = (r"D:\Files\smokeping project\cropped")

#Crop Images
def cropstuff():
    if os.path.exists(newpath):
        pass
    else:
        os.mkdir(newpath)

    dirs = os.listdir(path)
    def crop():
        for item in dirs:
            fullpath = os.path.join(path,item)         
            if os.path.isfile(fullpath) and item.endswith(".png"):
                im = Image.open(fullpath)
                f,e = os.path.splitext(fullpath)
                imCrop = im.crop((-65, 230, 195, 695)) 
                imCrop.save(f + '2.png', "png", quality=100)
    crop()

    def move():
        for item in os.listdir(path):
            if item.lower().endswith('2.png'):
                shutil.move(os.path.join(path, item), newpath)
    move()



#########################################################################################################################

#Output Data
def outputstuff():
    pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\tesseract\tesseract.exe")

    #Directories
    dirs = os.listdir(newpath)

    #Latency Data
    print()
    print("Latency:")

    with open(path + '\\' + str(timeframe) + '.txt', 'w') as f:
        f.write("Latency:" + ("\n"))

        for item in dirs:
            fullpath = os.path.join(newpath,item) 
            
            im = Image.open(fullpath)
            text = pytesseract.image_to_string(im, lang = 'eng')

            latency = text[11:20]
            latency_rep = latency.replace(' a', '').replace('v', '')
            print(latency_rep.lstrip() + " " + item[:-5])
            content = (latency_rep.lstrip() + " " + item[:-5])
            f.write("%s\n" % content)

       
    print()
    print("_________________________")


    #Packet Loss Data 
    print(" Packet Loss:")

    with open(path + '\\' + str(timeframe) + '.txt', 'a+') as f:
        f.write("\nPacket Loss:" + ("\n"))

        for item in dirs:
            fullpath = os.path.join(newpath,item) 

            im = Image.open(fullpath)
            text = pytesseract.image_to_string(im, lang = 'eng')

            pktloss = text[35:42]
            pktloss_rep = pktloss.replace(':', '').replace('%', '').replace('s ', '').replace(' ','')

            print(pktloss_rep.lstrip() + " " + item[:-5].lstrip())
            content2 = (pktloss_rep.lstrip() + " " + item[:-5])
            f.write("%s\n" % content2)


if __name__ == "__main__":
    #Start Timer
    start_time = time.time()
    curr_date = date.today()
    now = datetime.now()

    main()
    cropstuff()
    outputstuff()

    #End Timer
    end_time = time.time()
    tot_time = (f"Total time: {end_time - start_time}")
    tot_time = round(end_time - start_time, 2)
    print("Elapsed time: " + str(tot_time))



