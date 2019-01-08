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
from tkinter import ttk

import threading
from queue import Queue

from web.webcontent import WebContent
from web.webimage.girlsky import Girlsky
from web.webimage.pstatp import Pstatp
from web.webimage.meizitu import Meizitu
from web.webimage.mzitu import Mzitu
from web.webimage.webimage import WebImage

STAT_WAITTING = 'Waitting'
STAT_DOWNLOADING = 'Downloading'
STAT_DONE = 'Done'

class FileListInfo(object):
    def __init__(self):
        self._url = None
        self._state = STAT_WAITTING
        self._output = ''
        self._args = None

class WindowUI(object):

    def __init__(self):
        self._wm = dict()
        # create UI
        top = Tk()
        self._wm['top'] = top
        top.title('WebImageCrawler')
        top.geometry('800x646')

        top.resizable(0, 0)
        self.create_menu(top)

    def register_widget_handlers(self, widget_cmds, widgets_vars):
        # widget command
        self.menu_file_open = widget_cmds['menu_file_open']
        self.menu_about_about = widget_cmds['menu_about_about']
        self.on_run_click = widget_cmds['on_run_click']
        self.on_chk_type_click = widget_cmds['on_chk_type_click']
        self.on_bn_type_click = widget_cmds['on_bn_type_click']
        # widget vars
        self._lbfs_var = widgets_vars['lbfs_var']
        self._path_var = widgets_vars['path_var']
        self._type_var = widgets_vars['type_var']
        self._type_chk = widgets_vars['type_chk']
        self._type_start = widgets_vars['type_start']
        self._type_end = widgets_vars['type_end']

    def run(self):
        root = self._wm['top']
        # create frames for main window.
        self.create_main_window_frames(root)
        # create path widgets.
        self.create_path_widgets()

        self.create_type_widgets()
        # create header of file list.
        self.create_header_widgets()
        # create file list widghts
        self.create_file_list_widgets()

        root.mainloop()

    def create_menu(self, root):
        menubar = Menu(root)

        file_menu = Menu(menubar, tearoff = 0)
        #file_menu.add_command(label = 'Open', command=self.menu_file_open)

        about_menu = Menu(menubar, tearoff = 0)
        #about_menu.add_command(label = 'About', command=self.menu_about_about)

        menubar.add_cascade(label = 'File', menu = file_menu)
        menubar.add_cascade(label = 'About', menu = about_menu)
        root['menu'] = menubar


    def create_main_window_frames(self, root):
        Path = Frame(root)
        Path.pack(side = TOP, fill=X)

        Type = Frame(root)
        Type.pack(side = TOP, fill = X)

        Hdr = Frame(root)
        Hdr.pack(side = TOP, fill=X)

        Fs = Frame(root)
        Fs.pack(side = TOP, fill=X, padx =4, pady = 4)

        FsList = Frame(Fs)
        FsList.pack(side = LEFT, expand = 1, fill=X)
        SbY = Frame(Fs)
        SbY.pack(side = RIGHT, fill=Y)

        SbX = Frame(root)
        SbX.pack(side = TOP, fill = X)

        self._wm['frmPath'] = Path
        self._wm['frmType'] = Type
        self._wm['frmHdr'] = Hdr
        self._wm['frmFs'] = Fs
        self._wm['frmFsList'] = FsList
        self._wm['frmSbX'] = SbX
        self._wm['frmSbY'] = SbY

    def create_path_widgets(self):
        frm = self._wm['frmPath']
        lbPath = Label(frm, text = 'Path:')
        lbPath.pack(side = LEFT, expand=1, fill=X)
        enPath = Entry(frm, textvariable = self._path_var, width = 78)
        enPath.pack(side = LEFT, expand=1, fill=X)
        bnPath = Button(frm, text = 'Run', command = self.on_run_click)
        bnPath.pack(side = LEFT, expand=1, fill=X, padx = 4, pady = 2)

        self._wm['lbPath'] = lbPath
        self._wm['enPath'] = enPath
        self._wm['bnPath'] = bnPath

    def create_type_widgets(self):
        frm = self._wm['frmType']
        chkType = Checkbutton(frm, text = '', onvalue = 1, offvalue = 0, state = NORMAL,
                              variable = self._type_chk, command = self.on_chk_type_click)
        self._type_chk.set(0)
        chkType.pack(side = LEFT, padx = 8)
        cmbType = ttk.Combobox(frm, width = 8, textvariable = self._type_var)
        cmbType.pack(side = LEFT, padx = 18)
        cmbType['value'] = ('xgmn', 'swmn', 'wgmn', 'zpmn', 'mnxz', 'rtys', 'jpmn', 'gzmn', 'nrtys', 'meizitu', 'mzitu')
        lbStart = Label(frm, text = 'Start:')
        lbStart.pack(side = LEFT, padx = 8)
        enStart = Entry(frm, width = 8, textvariable = self._type_start)
        enStart.pack(side = LEFT)
        lbEnd = Label(frm, text = 'End:')
        lbEnd.pack(side = LEFT, padx = 8)
        enEnd = Entry(frm, width = 8, textvariable = self._type_end)
        enEnd.pack(side = LEFT)
        bnType = Button(frm, text = 'OK', width = 4, command = self.on_bn_type_click)
        bnType.pack(side = LEFT, padx = 36)

        cmbType['state'] = DISABLED
        enStart['state'] = DISABLED
        enEnd['state'] = DISABLED
        bnType['state'] = DISABLED

        self._wm['chkType'] = chkType
        self._wm['cmbType'] = cmbType
        self._wm['enStart'] = enStart
        self._wm['enEnd'] = enEnd
        self._wm['bnType'] = bnType

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
        lbFs = Listbox(frmFsList, height = 36, listvariable = self._lbfs_var)
        lbFs.pack(side = LEFT, expand = 1, fill = BOTH)
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



class WebImageCrawlerUI(WebContent, WindowUI):

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
        super().__init__()
        self._name = name

        self._fs_list = None
        self._fs_list_cnt = 0
        self._fs_list_state = STAT_DONE
        self._update_thread = None
        self._update_thread_run = 0
        self._update_thread_queue = None
        self._crawler_thread = None
        self._crawler_thread_run = 0

        self._class = None
        self._download_thread_max = 5
        self._download_thread_queue = None
        self._download_threads = list()


    def reclaim_url_address(self, url):
        for key, value in {'/$' : '', '\n$' : ''}.items():
            url = re.sub(key, value, url)
        return url

    def menu_file_open(self):
        f = askopenfilename()
        self._path_var.set(f)
        if f:
            self.update_file_list()
            self.update_list_info()

    def menu_about_about(self):
        print('Version: 1.0')

    def on_chk_type_click(self):
        cmbType = self._wm['cmbType']
        enStart = self._wm['enStart']
        enEnd = self._wm['enEnd']
        bnType = self._wm['bnType']
        # get state of cheType
        state = self._type_chk.get()
        if int(state):
            cmbType['state'] = NORMAL
            enStart['state'] = NORMAL
            enEnd['state'] = NORMAL
            bnType['state'] = NORMAL
        else:
            cmbType['state'] = DISABLED
            enStart['state'] = DISABLED
            enEnd['state'] = DISABLED
            bnType['state'] = DISABLED

    def on_bn_type_click(self):
        t_type  = self._type_var.get()
        t_start = self._type_start.get()
        t_end   = self._type_end.get()
        if all((t_type, t_start)):
            url_start = int(t_start)
            if t_end:
                url_end = int(t_end)
                if url_end > url_start:
                    n = url_end - url_start + 1
                else:
                    print('error: end(%d) < start(%d)!' % (url_end, url_start))
            else:
                n = 1
            # config args
            args = {'-x': t_type, '-u' : t_start, '-n' : n}
            self._path_var.set(args)

            # update file list and info.
            self.update_file_list()
            self.update_list_info()
        else:
            print('error, please input type and start.')

    def on_run_click(self):
        fp = self._wm['enPath'].get()
        if fp:
            self.create_update_file_list_thread()

            # # update file list and info
            self.update_file_list()
            self.update_list_info()
            self.set_widget_state(0)
            self._fs_list_state = STAT_DOWNLOADING

            self.create_crawler_thread()

    def set_widget_state(self, state):
        if state:
            self._wm['bnPath']['state'] = NORMAL
            self._wm['enPath']['state'] = NORMAL
            self._wm['chkType']['state'] = NORMAL
            self._wm['cmbType']['state'] = NORMAL
            self._wm['enStart']['state'] = NORMAL
            self._wm['enEnd']['state'] = NORMAL
            self._wm['bnType']['state'] = NORMAL
        else:
            self._wm['bnPath']['state'] = DISABLED
            self._wm['enPath']['state'] = DISABLED
            self._wm['chkType']['state'] = DISABLED
            self._wm['cmbType']['state'] = DISABLED
            self._wm['enStart']['state'] = DISABLED
            self._wm['enEnd']['state'] = DISABLED
            self._wm['bnType']['state'] = DISABLED


    def add_file_info(self, url, state = None, output = None):
        info = FileListInfo()
        info._url = url
        if state:
            info._state = state
        if output:
            info._output = output
        self._fs_list.append(info)
        self._fs_list_cnt += 1

    def update_list_info(self, url = None, state = None, output = None):
        fs = list()
        for i, info in enumerate(self._fs_list):
            if url == info._url:
                if state:
                    info._state = state
                if output:
                    info._output = output
            fs.append('%s%s%s' % (info._url.ljust(64), info._state.ljust(16), info._output.ljust(64)))
        self._lbfs_var.set(tuple(fs))

    def update_file_list(self):
        # clear file list
        self._fs_list_cnt = 0
        self._fs_list = list()
        # get file
        f = self._wm['enPath'].get()
        if os.path.isfile(f):
            with open(f, 'r') as fd:
                urls = fd.readlines()
        elif '-x' in f:
            args = eval(f)
            url_start = int(args['-u'])
            n = args['-n']
            url_type = args['-x']
            urls = list()
            for index in range(n):
                if url_type in self.URL_BASE:
                    url_base = list(self.URL_BASE[url_type])[0]
                    url = url_base.replace('URLID', str(url_start + index))
                    urls.append(url)
        else:
            urls = [f]
        # add file info to list.
        for url in set(urls):
            url = self.reclaim_url_address(url)
            if url:
                self.add_file_info(url)
        # sort of file list.
        self._fs_list.sort(key = lambda info: info._url, reverse=False)

    def create_update_file_list_thread(self):
        if not self._update_thread:
            self._update_thread = threading.Thread(target = self.update_file_list_thread)
            self._update_thread_run = 1
            self._update_thread_queue = Queue()
            self._update_thread.start()

    def update_file_list_thread(self):
        while self._update_thread_run:
            if self._update_thread_queue.empty():
                time.sleep(1)
                continue
            else:
                info = self._update_thread_queue.get()
                self.update_list_info(info._url, info._state, info._output)
                # Url done.
                if info._state == STAT_DONE:
                    self._fs_list_cnt -= 1
            if self._fs_list_cnt <= 0:
                self.set_widget_state(1)
                self._fs_list_state = STAT_DONE

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
                    info._state = STAT_DOWNLOADING
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
                info._state = STAT_DONE
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
            if self._fs_list_cnt:
                if self._fs_list_state != STAT_DOWNLOADING: # all of url are not donwload.
                    time.sleep(2)
                    continue
                index = 0
                count = self._fs_list_cnt
                self._download_threads = list()
                # create thread to download url.
                while index < count:
                    self._class = None
                    info = self._fs_list[index]
                    index += 1
                    url = self.reclaim_url_address(info._url)
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
                        t.start()
                        self._download_thread_queue.put(url)
                        self._download_threads.append(t)
                for t in self._download_threads:
                    t.join()
            else:
                time.sleep(1)
                continue

    def create_widget_cmd_vars(self):
        self._lbfs_var = StringVar()
        self._path_var = StringVar()
        self._type_var = StringVar()
        self._type_chk = StringVar()
        self._type_start = StringVar()
        self._type_end = StringVar()
        widget_cmds = {'menu_file_open' : self.menu_file_open,
                       'menu_about_about' : self.menu_about_about,
                       'on_run_click' : self.on_run_click,
                       'on_chk_type_click' : self.on_chk_type_click,
                       'on_bn_type_click' : self.on_bn_type_click
                       }
        widget_vars = {'lbfs_var' : self._lbfs_var,
                       'path_var' : self._path_var,
                       'type_var' : self._type_var,
                       'type_chk' : self._type_chk,
                       'type_start' : self._type_start,
                       'type_end' : self._type_end
                       }
        return widget_cmds, widget_vars

    def main(self):
        widget_cmds, widget_vars = self.create_widget_cmd_vars()
        self.register_widget_handlers(widget_cmds, widget_vars)
        self.run()

        # exit
        self._update_thread_run = 0
        self._crawler_thread_run = 0
        if self._update_thread:
            self._update_thread.join()
        if self._crawler_thread:
            self._crawler_thread.join()


if __name__ == '__main__':
    ui = WebImageCrawlerUI()
    ui.main()