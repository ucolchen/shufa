# coding=utf-8
from __future__ import print_function

import chardet
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from six.moves.urllib import request
import os
import time
import datetime
import re
from pyvirtualdisplay import Display
import socket

# 設置超時
socket.setdefaulttimeout(10)

isDebug = True

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
HEADERS = {'User-Agent': USER_AGENT}

STYLE_PER_PAGE = 24

FOLDER_NAME = os.getcwd() + "//caoshu//"
filaNameCSV = FOLDER_NAME + '!og.log'  # + fileNamePre + datetime.datetime.now().strftime("%Y%m%d_%H%M") + '.csv'

opt = webdriver.ChromeOptions()  # 创建浏览器
# opt.set_headless()                            #无窗口模式
caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
caps["pageLoadStrategy"] = "none"  # Do not wait for full page load


def download_char(link_ori, currentPage):
    link = link_ori
    linkori=link_ori
    newLinkSections = {'cs', '.htm'}
    if currentPage > 1:
        if 'cs.htm' in link:
            link = link.replace('cs.htm', ("%s" % (currentPage-1)).join(newLinkSections))
        elif ("%s" % (currentPage-2)).join(newLinkSections) in link:
            link = link.replace(("%s" % (currentPage-2)).join(newLinkSections),
                                ("%s" % (currentPage-1)).join(newLinkSections)
                                )
    print(link)
    rt = requests.get(link, headers=HEADERS)
    soupt = BeautifulSoup(rt.content, features="html.parser")

    h2S = soupt.find_all('h2')
    for h2 in h2S:
        if h2.text.find(u'草书书法') > 0:
            style_count = int(h2.text[h2.text.find(u'（') + 1:h2.text.find(u'种')])
            page_count = style_count / STYLE_PER_PAGE
            if (page_count >= 0) and ((style_count % STYLE_PER_PAGE) > 0):
                page_count += 1
            print (style_count,' styles, page ', currentPage, ' of ', page_count)
            if currentPage < page_count:
                currentPage = currentPage + 1
            elif currentPage >= page_count:
                currentPage = 1
    # http://www.cidianwang.com/shufa/piao4677_cs.htm
    # <li>
    #    <img
    #       height="168"
    #       onclick="box.Show();showsf(this.src);"
    #       alt="毛泽东写的瓢"
    #       title="毛泽东写的瓢"
    #       src="http://www.cidianwang.com/file/shufa/caoshu/57c21f71cbf9941f.gif">
    #    <a href="http://www.cidianwang.com/shufa/maozedong2872.htm">毛泽东</a>
    # </li>
    liSt = soupt.find_all('li')
    for lit in liSt:
        imgt = lit.find_all('img')
        if len(imgt) > 0:
            for img in imgt:
                img_char = img.get('title')[-1]
                img_people = img.get('title')[:img.get('title').index(u'写的')]
                img_link = img.get('src')
                img_fp = img_link[-10:-4]  # img_link.index('caoshu/')+len('caoshu/'):-4]
                img_ext = img_link[-4:]
                img_name = img_char + '_' + img_people + '_' + img_fp + img_ext
                save_name = FOLDER_NAME + img_name
                if 'gif' in save_name:
                    save_name = save_name.replace('.gif', '.gif.jpg')
                if os.path.exists(save_name):
                    print(img_name, 'existed.')
                else:
                    if 'http' in img_link:
                        try:
                            request.urlretrieve(img_link, save_name)  # '{}{}.jpg'.format(paths, x))
                            print (img_name)
                            time.sleep(0.5)
                        except socket.timeout:
                            pass

                    # return True
    if currentPage == 1:
        return True
    else:
        download_char(linkori, currentPage)
        return True


def getCaoshu(zhi):
    # Open a new window
    driver.execute_script("window.open('');")
    # Switch to the new window and open URL B
    driver.switch_to.window(driver.window_handles[-1])

    driver.get('http://www.cidianwang.com/shufa/')  # 打开网页
    # driver.maximize_window()                      #最大化窗口

    time.sleep(3)

    radios = driver.find_elements_by_xpath("//input[@type='radio']")
    for i in radios:
        id = i.get_attribute("id")
        if id == 's2':
            i.click()
            # print id

    texts = driver.find_elements_by_xpath("//input[@type='text']")
    for i in texts:
        id = i.get_attribute("id")
        classtmp = i.get_attribute("class")
        if id == 'q' and classtmp == 'k3 k6':
            i.clear()
            # i.send_keys(unicode(zhi, 'utf-8'))
            i.send_keys(zhi)
            # print id

    submits = driver.find_elements_by_xpath("//input[@type='submit']")
    for i in submits:
        id = i.get_attribute("id")
        classtmp = i.get_attribute("class")
        if id == 'sk4' and classtmp == 'k4':
            i.click()
            # print id

    time.sleep(1)
    url = driver.current_url.encode('utf-8')
    download_char(url, 1)


if __name__ == "__main__":
    from Tkinter import Tk
    from tkinter.filedialog import askopenfilename
    print('ask to open file...')
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    print(filename)

    FOLDER_NAME = filename+'_//'
    if not os.path.exists(FOLDER_NAME):
        os.makedirs(FOLDER_NAME)
        print ('made folder: ', FOLDER_NAME)

    f = open(filename,'r')
    str=f.read().decode('utf8')
    print (str)

    display = Display(visible=0, size=(800, 600))
    display.start()

    driver = webdriver.Chrome(desired_capabilities=caps, options=opt)  # 创建浏览器对象

    # print chardet.detect(str)
    # print type(str)
    for z in str:
        ordz=ord(z)
        # if not (0xFF01 <= ordz <= 0xFF5E):
        # not Punctuation， not 。period not rtn, not space
        if not (65281 <= ordz <= 65374)\
                and ordz <> 12290\
                and ordz <> 10\
                and ordz <> 32:
            print(z, type(z),ord(z))
            getCaoshu(z)
            pass
    # driver.quit()
    # display.stop()

#
# ChromeOptions options = new ChromeOptions();
# options.addArguments("--headless");
# ChromeDriver chromeDriver = new ChromeDriver(options);
