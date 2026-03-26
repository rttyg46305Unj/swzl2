from customtkinter import *
import libswzl2

def space(mstr, hgt):
    s = CTkFrame(mstr, width=0, height=hgt)
    s.pack(padx=0, pady=0)

def paragraph(mstr, txt):
    t = CTkLabel(mstr, text=txt, fg_color="transparent", font=consb)
    t.pack(padx=0, pady=5)

def geek():
    print('stop itching around')

def encode():
    confrom = convertfrom.get('1.0', 'end-1c')
    conto = convertto.get('1.0', 'end-1c')
    libswzl2.encode(image_path=confrom, output_path=conto)

def decode():
    confrom = convertfrom.get('1.0', 'end-1c')
    conto = convertto.get('1.0', 'end-1c')
    libswzl2.decode(swzl_path=confrom, output_path=conto)



# create root window
root = CTk()
root.title("swzlr-gui")
root.geometry('360x300')
root.minsize(270, 300)
root.maxsize(540, 405)
root.iconbitmap('swzlr.ico')

rad=3
cons=("Consolas", 14)
consb=("Consolas", 16)
hclr1="orange"
hclr2="#c18634"
hclr3="#3a2200"

#title
title = CTkLabel(root, text="swzlr-gui", fg_color="transparent", font=("Consolas Bold", 40), text_color=hclr1)
title.pack(padx=20, pady=15)

#space

space(root, 10)

#frame
frame = CTkScrollableFrame(root, width=300, height=150, corner_radius=rad)
frame.pack(padx=20, pady=0)

#ui
space(frame, 10)
paragraph(frame, "Convert from")
convertfrom = CTkTextbox(frame, height=60, corner_radius=rad, font=cons)
convertfrom.pack(padx=20, pady=0)
paragraph(frame, "Convert to")
convertto = CTkTextbox(frame, height=60, corner_radius=rad, font=cons)
convertto.pack(padx=20, pady=0)
space(frame, 10)
geek1 = CTkButton(frame, text='Encode', command=encode, width=100, corner_radius=rad, font=consb, fg_color=hclr2, hover_color=hclr3)
geek1.pack(padx=20, pady=0)
space(frame, 10)
geek2 = CTkButton(frame, text='Decode', command=decode, width=100, corner_radius=rad, font=consb, fg_color=hclr2, hover_color=hclr3)
geek2.pack(padx=20, pady=0) 
space(frame, 10)

# Tkinter event loop
root.mainloop()
