from tkinter import *
from tkinter.font import *

win = Tk()
win.configure(bg="#0C0C0C")

def gui(a, b, c):
    win.title(a)
    win.geometry(f"{b}x{c}")

def gprint(d):
    global tb
    if tb is None:
        tb = Text(win, width=10000, height=10000)
        tb.configure(font="Consolas", background="#0C0C0C", foreground="white")
        tb.pack()
    tb.insert(END, d + "\n")

def gres(e):
    win.resizable(e, e)

def gprint_nn(d):
    global tb
    if tb is None:
        tb = Text(win, width=100000, height=100000)
        tb.configure(font="Consolas", background="#0C0C0C", foreground="white")
        tb.pack()
    tb.insert(END, d)

def gui_background(f):
    tb.configure(background=f)
    win.configure(bg=f)

def gui_text_color(g):
    tb.configure(foreground=g)

def gui_text_font(h, i):
    tb.configure(font=(h, i))

def gui_dis():
    tb.configure(state=DISABLED)

def gprint_i(j):
    gprint_nn("")
    tb.image_create(END, image=j)

def gui_ib():
    bt = Button(win, text="")
    bt.pack()


def run():
    win.mainloop()
