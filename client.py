import socket
from tkinter import *
import tkinter.scrolledtext
from tkinter import simpledialog
import threading
from tkinter import colorchooser


HOST = socket.gethostbyname(socket.gethostname())
PORT = 50000

class Client:

    def __init__(self,host,port):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((host,port))

        #variable to wait until gui is ready
        self.gui_done = False
        self.running  = True
        self.gui_start = threading.Event()
        self.receive_start = threading.Event()

        self.gui_thread = threading.Thread(target=self.gui)
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()
        self.gui_thread.start()

    def nick(self):
        # message box to take nickname of client
        msg = Tk()
        msg.title("Welcome to ChatRoom")
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname","Please choose a nickname",parent=msg)
    def gui(self):
        self.nick()
        if self.nickname != "":
            self.gui_start.set()
            self.receive_start.set()
        self.gui_start.wait()

        self.room = Tk()
        self.room.geometry('400x450')
        self.room.resizable(0,0)
        self.room.configure(bg="lightgray")
        self.room.title("Chat Room")

        self.setting = Button(self.room,text="Settings",command=self.settings)
        self.setting.grid(pady=5,ipadx=5,ipady=3,row=0,column=2)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.room,width=45,height=21)
        self.text_area.grid(padx=10,pady=5,row=1,column=0,columnspan=3)
        self.text_area.config(state='disabled',bg='lightgreen')

        self.input_area = Text(self.room ,height=1.5,width=37)
        self.input_area.grid(padx=10,pady=5,row=2,column=0,columnspan=2)

        self.send_button = Button(self.room,text="Send",command=self.write)
        self.send_button.config(font=("Arial",12))
        self.send_button.grid(ipadx=8,ipady=2,row=2,column=2)

        #use enter key to send the message
        event = threading.Event()
        self.t1 = threading.Thread(target=self.write)
        self.room.bind('<Return>',self.write)

        #to exit the chat when close is clicked
        self.room.protocol("WM_DELETE_WINDOW",self.stop)
        self.gui_done = True
        self.room.mainloop()

    def settings(self):
        self.setting.config(state='disable')
        self.win = Toplevel()
        self.win.title("Settings")
        self.win.config(bg="skyblue")

        #postion
        x1 = self.room.winfo_x()
        y1= self.room.winfo_y()
        self.win.geometry("150x150+%d+%d"%(x1,y1))

        change_backgroud = Button(self.win,text="Change Background",command=self.change_bg)
        change_backgroud.pack(pady=12,ipadx=5,ipady=7)

        change_font = Button(self.win,text="Change Font Color",command=self.change_font_color)
        change_font.pack(pady=12,ipadx=5,ipady=7)
        self.win.protocol("WM_DELETE_WINDOW", self.enable_setting)
        self.win.mainloop()

    def enable_setting(self):
        self.setting.config(state='normal')
        self.win.destroy()

    def change_bg(self):
        self.bg_color = colorchooser.askcolor(title="Choose chat background color")
        self.text_area.config(bg=self.bg_color[1])
        self.setting.config(state='normal')
        self.win.destroy()

    def change_font_color(self):
        self.font_color = colorchooser.askcolor(title="Choose Font Color")
        self.text_area.config(fg=self.font_color[1])
        self.setting.config(state='normal')
        self.win.destroy()

    def stop(self):
        self.ask = Toplevel(self.room)
        self.ask.title("Exit")

        # positon
        x1 = self.room.winfo_x()
        y1 = self.room.winfo_y()
        room_height = self.room.winfo_height()
        room_width = self.room.winfo_width()
        ask_height = self.ask.winfo_height()
        ask_width = self.ask.winfo_width()
        adj_height = room_height - ask_height
        adj_width = room_width - ask_width
        self.ask.geometry("+%d+%d" % (x1 + adj_width // 5, y1 + adj_height // 3))

        # label
        ques = Label(self.ask, text="Are you sure you want to leave the ChatRoom?")
        ques.config(font=('Arial', 8))
        ques.grid(padx=10, pady=10, row=0, column=0, columnspan=2)

        # buttons
        yes = Button(self.ask, text="Yes", command=self.yes)
        yes.config(font=('Arial', 10, 'bold'), fg='blue')
        yes.grid(pady=10, ipadx=20, row=1, column=0)

        no = Button(self.ask, text="No", command=self.no)
        no.config(font=('Arial', 10, 'bold'), fg='blue')
        no.grid(pady=10, ipadx=20, row=1, column=1)

        self.ask.mainloop()

    def yes(self):
        self.running = False
        self.room.destroy()
        self.client.send("leaving".encode('utf-8'))
        self.client.close()
        exit(0)

    def no(self):
        self.ask.destroy()

    def write(self,event=False):
        msg = f"{self.input_area.get('1.0','end')}"
        if msg.isspace():
            pass
        else:
            self.client.send(msg.encode('utf-8'))
            self.input_area.delete('1.0', 'end')

    def receive(self):
        self.receive_start.wait()
        while self.running:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                if msg =='NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', msg)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break
            except:
                print("There is some error")
                break

ob = Client(HOST,PORT)

