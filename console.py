#-*- coding: utf-8 -*-

# (c) 2016 Zack1409 Labs LLC.
# This code is licensed under the GNU General Public License, version 3 or later.

# (c) 2016 Илья Коваленко.
# Данный код распространяется на условиях лицензии GNU GPL версии 3 или более поздней

import mangadownloader as md
import urllib
import os
from multiprocessing.dummy import Pool as WorkerPool

while True:

    # Вводим ссылку на сайт
    print("\nВведите ссылку на мангу с сайта readmanga.me или mintmanga.com")

    # Создаем переменную которая получает нашу ссылку
    link = input()

    # Создаем переменную которая парсит строку и приводит ее к виду
    # ParseResult(scheme='', netloc='mintmanga.com', path='/evil_blade/',
    # params='', query='', fragment='')
    link_components = urllib.parse.urlparse(link)

    # Проверяет содержит ли адрес сайта "readmanga.me" "adultmanga.ru" "mintmanga.com"
    if (link_components.netloc == 'readmanga.me' or
            link_components.netloc == 'adultmanga.ru' or
            link_components.netloc == 'mintmanga.com'):

        # Переменная проверяет есть ли после второго знака есть елешы то получаем номер этого слеша в строке начиная с 0 и обрезаем все что после что бы получить имя манги (http://mintmanga.com/tokyo_ghoul/vol14/143 получим tokyo_ghoul) если ссылка дана правильно сразу используем имя
        pathCount = link_components.path[1:].count('/')
        if pathCount != 0:
            first = link_components.path[1:].find('/')
            manga_name = link_components.path[1:first + 1]
        else:
            manga_name = link_components.path[1:]
        #  Получаем список глав манги с сайта
        chapters = md.MangaDownloader.get_chapters_list(
            'http://' + link_components.netloc + '/' + manga_name)
        # Обьявляем пустой и явно указанный массив
        chapters_list = []
        # Получаем список глав если проблемы с подключением к сайту (1) или в манге нет глав (2) пишем ошибку
        if chapters == 1 or chapters == 2:
            print('\nНевозможно скачать мангу в данный момент.')
        else:
            for chapter in chapters:
                # Делим ссылку полную (/mintmanga.com/evil_blade/vol1/5?mature=1) по / и кидаем в список
                words_from_name = chapter.split('/')
                try:
                    # Обрезаем vol1 до 1 и явно указываем тип число
                    vol = int(words_from_name[2][3:])
                    # Обрезаем 5?mature=1 до 5 и явно указываем тип число
                    ch = int(words_from_name[3].split('?')[0])
                except:
                    vol = 0
                    ch = -1
                # Создаем словарь с полной ссылкой (/evil_blade/vol1/5?mature=1) томом (1) и глава (5)
                chapters_list.append(dict(link=chapter, vol=vol, ch=ch))
            print("\nВведите номера глав, которые вы хотите скачать, через пробел, если хотите скачать все главы, нажмите ENTER")

            input_string = input()
            if input_string in chapters_list:
                if (input_string.find('-') != -1):
                    num = input_string.find('-')
                    l_num = int(input_string[:num])
                    r_num = int(input_string[num + 1:])
                    chapters_to_download_list = list()
                    for a in range(l_num, r_num + 1):
                        chapters_to_download_list.append(a)
                    download_all = False
                else:
                    chapters_to_download_list = list(
                        map(int, input_string.split()))
                download_all = False
                if len(chapters_to_download_list) == 0:
                    download_all = True
                # TODO сделать выбор папки куда качать
                work_directory = os.curdir
                if not os.path.exists(os.path.join(work_directory, manga_name)):
                    os.mkdir(os.path.join(work_directory, manga_name))
                pool = WorkerPool(len(chapters_list))  # лимита на закачку нет
                # Создать папки для томов и глав
                for chapter in chapters_list:
                    if (ch != -1):
                        if (download_all == True) or (chapter['ch'] in chapters_to_download_list):
                            vol_path = os.path.join(
                                work_directory, manga_name, str(chapter['vol']).zfill(4))
                            if not os.path.exists(vol_path):
                                os.mkdir(vol_path)
                            ch_path = os.path.join(work_directory, manga_name, str(
                                chapter['vol']).zfill(4), str(chapter['ch']).zfill(4))
                            if not os.path.exists(ch_path):
                                os.mkdir(ch_path)
                            # Скачивание манги в папку

                            pool.apply_async(md.MangaDownloader.download_chapters, (
                                'http://' + link_components.netloc + chapter['link'], ch_path))

                lastProgress = 0
                while md.progress < md.pages or md.pages == 0:
                    if lastProgress != md.progress:
                        print("\rloaded " + str(md.progress) +
                              "/" + str(md.pages), end="")
                        lastProgress = md.progress
                    print("\ndownload complete")
                pool.close()
                pool.join()
            else:
                print ("В этой манге нет такой главы")

    else:
         print("\nЭта ссылка не на readmanga или mintmanga")

