"""
Author : tharindra galahena (inf0_warri0r)
Project: l_viewer
Blog   : http://www.inf0warri0r.blogspot.com
Date   : 30/04/2013
License:

     Copyright 2013 Tharindra Galahena

l_viewer is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. l_viewer is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

* You should have received a copy of the GNU General Public License along with
this. If not, see http://www.gnu.org/licenses/.

"""

import Tkinter as tk
import l_system
import thread
from threading import Lock
import time
import tkFileDialog
import tkMessageBox as dialog


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()

        self.run = False
        self.l_sys = None
        self.pause = False
        self.file = ''
        self.mutex = Lock()
        self.createWidgets()

    def createWidgets(self):

        self.load_button = tk.Button(self, text='load', command=self.load)

        self.start_button = tk.Button(self, text='start', command=self.start)
        self.stop_button = tk.Button(self, text='stop', command=self.stop)
        self.zoom_in_button = tk.Button(self, text='+', command=self.zoom_in)
        self.zoom_out_button = tk.Button(self, text='-', command=self.zoom_out)

        self.up_button = tk.Button(self, text='^', command=self.go_up)
        self.down_button = tk.Button(self, text='v', command=self.go_down)
        self.left_button = tk.Button(self, text='<', command=self.go_left)
        self.right_button = tk.Button(self, text='>', command=self.go_right)

        self.pause_button = tk.Button(self, text='pause/restart',
                                        command=self.toggle_pause)

        self.load_button.grid(column=0, row=0,
                                columnspan=4, sticky=tk.W + tk.E)

        self.start_button.grid(column=0, row=1,
                                columnspan=2, sticky=tk.W + tk.E)
        self.stop_button.grid(column=2, row=1,
                                columnspan=2, sticky=tk.W + tk.E)
        self.zoom_in_button.grid(column=0, row=2,
                                columnspan=2, sticky=tk.W + tk.E)
        self.zoom_out_button.grid(column=2, row=2,
                                columnspan=2, sticky=tk.W + tk.E)

        self.up_button.grid(column=1, row=3,
                                columnspan=2, sticky=tk.W + tk.E)
        self.left_button.grid(column=0, row=4,
                                columnspan=2, sticky=tk.W + tk.E)
        self.right_button.grid(column=2, row=4,
                                columnspan=2, sticky=tk.W + tk.E)
        self.down_button.grid(column=1, row=5,
                                columnspan=2, sticky=tk.W + tk.E)

        self.pause_button.grid(column=1, row=6,
                                columnspan=2, sticky=tk.W + tk.E)

        self.file_name = tk.StringVar()
        self.file_entry = tk.Entry(textvariable=self.file_name)
        self.content = tk.StringVar()
        self.max_entry = tk.Entry(textvariable=self.content)
        self.max_entry.insert(0, '10')
        self.gen_entry = tk.Entry()

        tk.Label(text="file :").grid(column=0, row=7, sticky=tk.W)

        self.file_entry.grid(column=0, row=8)

        tk.Label(text="maximum generations :").grid(column=0,
                                                    row=9, sticky=tk.W)
        self.max_entry.grid(column=0, row=10)
        tk.Label(text="current generation :").grid(column=0,
                                                    row=11, sticky=tk.W)
        self.gen_entry.grid(column=0, row=12)

        tk.Label(text="").grid(column=0, row=13, rowspan=10, sticky=tk.W)
        self.canvas = tk.Canvas(width=640, height=640, background="black")
        self.canvas.grid(row=0, rowspan=23,
                        column=4, sticky=tk.W + tk.E + tk.N + tk.S)

        self.x_scale = 1
        self.y_scale = 1

    def start(self):
        if self.run is False:
            self.file = self.file_name.get()
            if self.file != '':
                if self.read_file(self.file):
                    self.run = True
                    try:
                        thread.start_new_thread(self.thread_func, ())
                    except Exception, e:
                        dialog.showerror(title='ERROR !!', message='Thread error')

    def read_file(self, name):
        f = open(name, 'r')
        try:
            cat = f.read()
            f.close()
            self.lst_rules = list()
            self.lst_symbols = list()
            lines = cat.splitlines()
            self.axiom = lines[0]
            self.angle = float(lines[1])
            self.ang = float(lines[2])
            num_rules = int(lines[3])
            for i in range(4, num_rules + 4):
                rule = lines[i].split('=')
                self.lst_rules.append((rule[0], rule[1]))

            num_symbols = int(lines[num_rules + 4])
            for i in range(num_rules + 5, num_rules + 5 + num_symbols):
                symbol = lines[i].split('=')
                commands = symbol[1].split(',')
                self.lst_symbols.append((symbol[0], commands))
            return True
        except Exception:
            dialog.showerror(title='ERROR !!', message='Invailed File')

    def stop(self):
        self.run = False

    def load(self):
        self.file = tkFileDialog.askopenfilename()
        if self.file != '':
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, self.file)

    def redraw(self):
        self.mutex.acquire()
        self.canvas.delete(tk.ALL)
        self.l_sys.reset()
        lst = self.l_sys.draw()

        for li in lst:
            if not self.run:
                break

            self.canvas.create_line(li[0][0],
                                    li[0][1],
                                    li[1][0],
                                    li[1][1],
                                    fill='yellow')
        self.canvas.update()
        self.mutex.release()

    def zoom_in(self):

        if self.l_sys is not None:
            self.l_sys.length = self.l_sys.length + 0.5
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def zoom_out(self):

        if self.l_sys is not None and self.l_sys.length >= 1.0:
            self.l_sys.length = self.l_sys.length - 0.5
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def go_left(self):
        if self.l_sys is not None:
            self.l_sys.st_x = self.l_sys.st_x - 10
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def go_right(self):
        if self.l_sys is not None:
            self.l_sys.st_x = self.l_sys.st_x + 10
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def go_up(self):
        if self.l_sys is not None:
            self.l_sys.st_y = self.l_sys.st_y - 10
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def go_down(self):
        if self.l_sys is not None:
            self.l_sys.st_y = self.l_sys.st_y + 10
            if self.pause:
                thread.start_new_thread(self.redraw, ())

    def toggle_pause(self):
        if self.pause:
            self.pause = False
        else:
            self.pause = True

    def thread_func(self):

        self.l_sys = l_system.l_system(self.axiom,
                                        300, 300,
                                        600, 600,
                                        5,
                                        self.angle, self.ang)

        self.l_sys.set_symbols(self.lst_symbols)
        self.l_sys.set_rules(self.lst_rules)
        self.run = True
        self.pause = False
        text = self.content.get()
        self.max = int(text)
        self.gen_count = 0
        while self.run:
            self.mutex.acquire()
            self.l_sys.reset()
            self.gen_entry.delete(0, tk.END)
            self.gen_entry.insert(0, str(self.gen_count + 1))
            if not self.pause and self.gen_count < self.max:
                self.gen_count = self.gen_count + 1
                self.l_sys.next_gen()
            lst = self.l_sys.draw()
            self.canvas.delete(tk.ALL)
            for li in lst:
                if not self.run:
                    break
                self.canvas.create_line(li[0][0],
                                        li[0][1],
                                        li[1][0],
                                        li[1][1],
                                        fill='yellow')
                self.canvas.update()
            self.mutex.release()
            while self.gen_count >= self.max or self.pause:
                time.sleep(0.01)
                if not self.run:
                    break

            time.sleep(1)
        self.canvas.delete(tk.ALL)

