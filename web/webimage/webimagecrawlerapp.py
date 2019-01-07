#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on: 2019-01-02

@author: Byng Zeng
"""
import os
import re
import time

from tkinter import *
from tkinter.filedialog import askopenfilename #askdirectory

import threading
from queue import Queue

from web.webcontent import WebContent
from web.webimage.girlsky import Girlsky
from web.webimage.pstatp import Pstatp
from web.webimage.meizitu import Meizitu
from web.webimage.mzitu import Mzitu
from web.webimage.webimage import WebImage

class FileListInfo(object):
    def __init__(self):
        self._url = None
        self._state = 'Waitting'
        self._output = '/home/yingbin/Dowloads/'

class WebImageCrawler(WebContent):

    URL_BASE = {
        # xval : { url_base : class}
        'xgmn' : {'http://m.girlsky.cn/mntp/xgmn/URLID.html' : 'girlsky'},  # 性感美女
        'swmn' : {'http://m.girlsky.cn/mntp/swmn/URLID.html' : 'girlsky'},  # 丝袜美女
        'wgmn' : {'http://m.girlsky.cn/mntp/wgmn/URLID.html' : 'girlsky'},  # 外国美女
        'zpmn' : {'http://m.girlsky.cn/mntp/zpmn/URLID.html' : 'girlsky'},  # 自拍美女
        'mnxz' : {'http://m.girlsky.cn/mntp/mnxz/URLID.html' : 'girlsky'},  # 美女写真
        'rtys' : {'http://m.girlsky.cn/mntp/rtys/URLID.html' : 'girlsky'},  # 人体艺术
        'jpmn' : {'http://m.girlsky.cn/mntp/jpmn/URLID.html' : 'girlsky'},  # 街拍美女
        'gzmn' : {'http://m.girlsky.cn/mntp/gzmn/URLID.html' : 'girlsky'},  # 古装美女
        'nrtys' : {'http://m.girlsky.cn/mntpn/rtys/URLID.html' : 'girlsky'},  # 人体艺术
        # pstatp
        'pstatp'   : {'https://www.toutiao.com/aURLID' : 'pstatp'},
        'pstatp_i' : {'https://www.toutiao.com/iURLID' : 'pstatp'},
        # meizitu
        'meizitu' : {'http://www.meizitu.com/a/URLID.html' : 'meizitu'},
        # mzitu
        'mzitu'   : {'https://m.mzitu.com/URLID' : 'mzitu'},
    }


    def __init__(self, name=None):
        self._name = name
        self._wm = dict()
        self._fs_list = list()
        self._fs_list_cnt = 0
        self._update_thread = None
        self._update_thread_run = 0
        self._update_thread_queue = None
        self._crawler_thread = None
        self._crawler_thread_run = 0

        self._class = None
        self._download_thread_max = 5
        self._download_thread_queue = None
        self._download_threads = list()

    def menu_file_open(self):
        self._path_var.set(askopenfilename())

    def menu_about_about(self):
        print('Version: 1.0')

    def create_menu(self, root):
        menubar = Menu(root)

        file_menu = Menu(menubar, tearoff = 0)
        file_menu.add_command(label = 'Open', command=self.menu_file_open)

        about_menu = Menu(menubar, tearoff = 0)
        about_menu.add_command(label = 'About', command=self.menu_about_about)

        menubar.add_cascade(label = 'File', menu = file_menu)
        menubar.add_cascade(label = 'About', menu = about_menu)
        root['menu'] = menubar

    def on_run_click(self):
        fp = self._wm['enPath'].get()
        if fp:
            self.create_update_file_list_thread()

            # clear file list
            self._fs_list = list()
            # update file list
            self.update_file_list()
            self.update_list_info()
            self._wm['bnPath']['state'] = DISABLED
            self._wm['enPath']['state'] = DISABLED

            self.create_crawler_thread()

    def create_main_window_frames(self, root):
        Path = Frame(root)
        Path.pack(side = TOP, fill=X)

        Hdr = Frame(root)
        Hdr.pack(side = TOP, fill=X)

        Fs = Frame(root)
        Fs.pack(side = TOP, fill=X)

        FsList = Frame(Fs)
        FsList.pack(side = LEFT, expand = 1, fill=X)
        SbY = Frame(Fs)
        SbY.pack(side = RIGHT, fill=Y)

        SbX = Frame(root)
        SbX.pack(side = TOP, fill = X)

        self._wm['frmPath'] = Path
        self._wm['frmHdr'] = Hdr
        self._wm['frmFs'] = Fs
        self._wm['frmFsList'] = FsList
        self._wm['frmSbX'] = SbX
        self._wm['frmSbY'] = SbY

    def create_path_widgets(self):
        frm = self._wm['frmPath']
        lbPath = Label(frm, text = 'Path:')
        lbPath.pack(side = LEFT, expand=1, fill=X)
        self._path_var = StringVar()
        enPath = Entry(frm, textvariable = self._path_var, width = 78)
        enPath.pack(side = LEFT, expand=1, fill=X)
        bnPath = Button(frm, text = 'Run', command = self.on_run_click)
        bnPath.pack(side = LEFT, expand=1, fill=X)

        self._wm['lbPath'] = lbPath
        self._wm['enPath'] = enPath
        self._wm['bnPath'] = bnPath

    def create_header_widgets(self):
        frm = self._wm['frmHdr']
        #self.chkFsSelAll = Checkbutton(frm, justify=LEFT)
        self.lbFsURL = Label(frm, text = 'URL', width = 32)
        self.lbFsState = Label(frm, text = 'State', width = 8)
        self.lbFsOutput = Label(frm, text = 'Output', width = 32)
        #self.chkFsSelAll.pack(side = LEFT, expand =1, fill = X)
        self.lbFsURL.pack(side = LEFT, expand =1, fill=X)
        self.lbFsState.pack(side = LEFT, expand =1, fill=X)
        self.lbFsOutput.pack(side = LEFT, expand =1, fill=X)


    def create_file_list_widgets(self):
        frmFsList = self._wm['frmFsList']
        self._lbFs_var = StringVar()
        lbFs = Listbox(frmFsList, height = 38, listvariable = self._lbFs_var)
        lbFs.pack(side = LEFT, expand = 1, fill = X)
        frmSbY = self._wm['frmSbY']
        sbY = Scrollbar(frmSbY)
        sbY.pack(side = TOP, expand = 1, fill=Y)
        frmSbX = self._wm['frmSbX']
        sbX = Scrollbar(frmSbX, orient = HORIZONTAL)
        sbX.pack(side = TOP, expand = 1, fill=X)

        lbFs['yscrollcommand'] = sbY.set
        sbY['command'] = lbFs.yview
        lbFs['xscrollcommand'] = sbX.set
        sbX['command'] = lbFs.xview

        self._wm['lbFs'] = lbFs
        self._wm['sbY'] = sbY
        self._wm['sbX'] = sbX

    def create_main_window(self, root):
        # create frames for main window.
        self.create_main_window_frames(root)
        # create path widgets.
        self.create_path_widgets()
        # create header of file list.
        self.create_header_widgets()
        # create file list widghts
        self.create_file_list_widgets()

    def add_file_info(self, url, state = None, output = None):
        info = FileListInfo()
        info._url = url
        if state:
            info._state = state
        if output:
            info._output = output
        self._fs_list.append(info)

    def update_list_info(self, url = None, state = None, output = None):
        fs = list()
        for i, info in enumerate(self._fs_list):
            if url == info._url:
                if state:
                    info._state = state
                if output:
                    info._output = output
            fs.append('%s%s%s' % (info._url.ljust(64), info._state.ljust(16), info._output.ljust(64)))
        self._lbFs_var.set(tuple(fs))

    def update_file_list(self):
        f = self._wm['enPath'].get()
        if not os.path.isfile(f):
            lines = [f]
        else:
            with open(f, 'r') as fd:
                lines = fd.readlines()
        for line in lines:
            for key, value in {'/$' : '', '\n$' : ''}.items():
                line = re.sub(key, value, line)
            if line:
                self.add_file_info(line)
        self._fs_list_cnt = len(lines)

    def create_update_file_list_thread(self):
        if not self._update_thread:
            self._update_thread = threading.Thread(target = self.update_file_list_thread)
            self._update_thread_run = 1
            self._update_thread_queue = Queue()
            self._update_thread.start()

    def update_file_list_thread(self, url=None, state = None, output = None, delay = 0):
        if delay:
            time.sleep(delay)
        while self._update_thread_run:
            if self._update_thread_queue.empty():
                time.sleep(1)
                continue
            else:
                info = self._update_thread_queue.get()
                self.update_list_info(info._url, info._state, info._output)
                if self._fs_list_cnt:
                    self._fs_list_cnt -= 1
            if not self._fs_list_cnt:
                self._wm['bnPath']['state'] = NORMAL
                self._wm['enPath']['state'] = NORMAL

    def download_url(self, args=None):
        url = args['-u']
        if self._class:
            if self._class == 'girlsky':
                hdr = Girlsky('Girlsky')
            elif self._class == 'pstatp':
                hdr = Pstatp('Pstatp')
            elif self._class == 'meizitu':
                hdr = Meizitu('Meizitu')
            elif self._class == 'mzitu':
                hdr = Mzitu('Mzitu')
        else:
            hdr = WebImage('WebImage')
        if hdr:
            for info in self._fs_list:
                if info._url == url:
                    info._state = 'Downloading'
                    self._update_thread_queue.put(info)
                    break
            output = hdr.main(args)
        else:
            self._pr.pr_err('[WebImageCrawler] Error, no found handler!')
        # release queue
        if self._download_thread_queue:
            self._download_thread_queue.get()

        for info in self._fs_list:
            if info._url == url:
                info._state = 'Done'
                info._output = output
                self._update_thread_queue.put(info)
                break


    def create_crawler_thread(self):
        if not self._crawler_thread:
            self._download_thread_queue = Queue(self._download_thread_max)
            self._crawler_thread = threading.Thread(target = self.crawler_thread)
            self._crawler_thread_run = 1
            self._crawler_thread.start()

    def crawler_thread(self):
        while self._crawler_thread_run:
            cnt = len(self._fs_list)
            if not self._fs_list_cnt: # no files.
                time.sleep(1)
                continue
            index = 0
            self._download_threads = list()
            while cnt:
                info = self._fs_list[index]
                self._class = None
                for key, value in {'/$' : '', '\n$' : ''}.items():
                    url = re.sub(key, value, info._url)
                base, num = self.get_url_base_and_num(url)
                if base:
                    for dict_url_base in self.URL_BASE.values():
                        if base == list(dict_url_base)[0]:
                            self._class =  dict_url_base[base]
                            break
                if self._class:
                    url = {'-u' : url}
                    # create thread and put to queue.
                    t = threading.Thread(target=self.download_url, args=(url,))
                    self._download_thread_queue.put(url)
                    t.start()
                    self._download_threads.append(t)
                index += 1
                cnt -= 1
            for t in self._download_threads:
                t.join()

    def main(self):
        top = Tk()
        self._wm['top'] = top
        top.title('WebImageCrawler')
        top.geometry('800x640')

        top.resizable(0, 0)
        self.create_menu(top)

        self.create_main_window(top)

        top.mainloop()
        self._update_thread_run = 0
        self._crawler_thread_run = 0
        if self._update_thread:
            self._update_thread.join()
        if self._crawler_thread:
            self._crawler_thread.join()

        print('WebImageCrawler done!')

if __name__ == '__main__':
    wic = WebImageCrawler()
    wic.main()