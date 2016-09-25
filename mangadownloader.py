#-*- coding: utf-8 -*-

# (c) 2016 Zack1409 Labs LLC.
# This code is licensed under the GNU General Public License, version 3 or later.

# (c) 2016 Илья Коваленко.
# Данный код распространяется на условиях лицензии GNU GPL версии 3 или более поздней

import lxml.html
import urllib.request
import os

# Количество страниц равно 0
pages = 0
# Прогресс равен 0
progress = 0

class Chapter:
    # Класс, который обозначает главу манги
    def __init__(self, link, vol_number, ch_number):
        self.link = link
        self.vol_number = vol_number
        self.ch_number = ch_number


class MangaDownloader:

    def get_chapters_list(link):
        # Данная процедура скачивает список глав манги, ссылка на которую передаётся в качестве единственного параметра
        my_request = urllib.request.Request(link)
        # Данные заголовки необходимы, чтобы сайт считал нас браузером
        my_request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0)\
                                            Gecko/20100101 Firefox/24.0')
        try:
            page = urllib.request.urlopen(my_request)
        except:
            # Ошибка сети
            return 1
        text = page.read().decode(encoding='UTF-8')
        doc = lxml.html.document_fromstring(str(text))
        links = []
        # Ищем главы манги
        for element in doc.cssselect("html body div#mangaBox.pageBlock div.leftContent div.expandable"):
            for chapter in element.cssselect("tr td a"):
                if (chapter.get('href')):
                     if chapter.attrib['href'].startswith('/'):
                        lnk = chapter.attrib['href']
                        lnk += "?mature=1"
                        links.append(lnk)
        if len(links) == 0:
            return 2
        return reversed(links)

    def download_chapters(link, path):
        global pages
        global progress
        # Данная процедура скачивает в данную папку главу манги
        my_request = urllib.request.Request(link)
        # Данные заголовки необходимы, чтобы сайт считал нас браузером
        my_request.add_header('User-Agent', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0)\
                                            Gecko/20100101 Firefox/24.0")
        try:
            page = urllib.request.urlopen(my_request)
        except:
            return 1
        text = page.read().decode(encoding="UTF-8")
        doc = lxml.html.document_fromstring(str(text))
        # Ищем ссылки на данное изображение
        for element in doc.xpath("/html/body/div[6]/script[1]"):
            if element.text.find("rm_h.init") != -1:
                script_text = element.text
            else:
                print("Not Found")
        script_line = script_text.split("rm_h.init")[1]
        script_line = script_line[3:-17]
        script_line = script_line[:-1].replace('[', '').split('],')
        links = []
        for line in script_line:
            el = line.replace('"', r"'").replace("'", '')
            el = el.split(',')
            lnk = el[1] + el[0] + el[2]
            links.append(lnk)
            pages += 1
        if len(links) < 1:
            return 4
        imgNum = 0
        for download_link in links:
            imgNum += 1
            errCount = 0
            fileType = download_link.split(".")[-1]
            #Скачиваем изображение в нужную папку
            while True:
                if errCount > 100: #тк лочится только один поток то от сотни проверок хуже не станет
                    print('Ошибка при загрузке файлов' + download_link)
                    break
                try:
                    image_file = urllib.request.urlretrieve(download_link, os.path.join(path, str(imgNum).zfill(4) + "." + fileType))
                except:
                    errCount += 1
                    continue
                break
            progress += 1

        return 0
