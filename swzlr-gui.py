from customtkinter import *
from os import system as cmd

def space(mstr, hgt):
    s = CTkFrame(mstr, width=0, height=hgt)
    s.pack(padx=0, pady=0)

def paragraph(mstr, txt):
    t = CTkLabel(mstr, text=txt, fg_color="transparent")
    t.pack(padx=0, pady=5)

def geek():
    print('stop itching around')

def encode():
    confrom = convertfrom.get('1.0', 'end-1c')
    conto = convertto.get('1.0', 'end-1c')
    cmd(f'swzlr encode \"{confrom}\" \"{conto}\"')

def decode():
    confrom = convertfrom.get('1.0', 'end-1c')
    conto = convertto.get('1.0', 'end-1c')
    cmd(f'swzlr decode \"{confrom}\" \"{conto}\"')

# create root window
root = CTk()
root.title("swzlr-gui")
root.geometry('360x300')
root.minsize(270, 300)
root.maxsize(540, 405)

#funny title
title = CTkLabel(root, text="swzlr-gui", fg_color="transparent", font=("Consolas Bold", 30), text_color="orange")
title.pack(padx=20, pady=15)

#space

space(root, 10)

#frame
frame = CTkScrollableFrame(root, width=300, height=150)
frame.pack(padx=20, pady=0)

#ui
space(frame, 10)
paragraph(frame, "Convert from")
convertfrom = CTkTextbox(frame, height=60)
convertfrom.pack(padx=20, pady=0)
paragraph(frame, "Convert to")
convertto = CTkTextbox(frame, height=60)
convertto.pack(padx=20, pady=0)
space(frame, 10)
geek1 = CTkButton(frame, text='Encode', command=encode, width=100)
geek1.pack(padx=20, pady=0)
space(frame, 10)
geek2 = CTkButton(frame, text='Decode', command=decode, width=100)
geek2.pack(padx=20, pady=0) 
space(frame, 10)

# Tkinter event loop
root.mainloop()
