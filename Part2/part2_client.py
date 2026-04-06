# Group#: A13
# Student Names:

#Content of client.py; to complete/implement

from tkinter import *
import socket
import threading
from multiprocessing import current_process #only needed for getting the current process name

class ChatClient:
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    # To implement

    def __init__(self, window):
        # --- Initialize GUI ---
        self.window = window

        self.window.title("Chat Client - " + current_process().name) # Display the current process name in the title
        self.window.configure(background="#def2fe")
        self.window.geometry("350x450")

        Label(self.window, text="Let's chit chat!").pack()

        self.Text = Text(self.window, state=DISABLED) # Read-only
        self.Text.pack(pady=5)

        input_frame = Frame(self.window, bg="#def2fe")
        input_frame.pack(pady=5, padx=10, fill=X)
        self.entry = Entry(input_frame, width=30)
        self.entry.pack(side=LEFT, padx=(0,5))

        Button(input_frame, text="Send", command=self.send_message).pack(side=LEFT)        
        Button(self.window, text="Exit", command=self.window.destroy).pack(anchor="e", padx=10, pady=10)

        # --- Initialize Socket Connection ---
        self.HOST = '127.0.0.1'
        self.PORT = 12345
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect((self.HOST, self.PORT))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except:
            print("[Client] Failed to establish connection to server.")

        
    def send_message(self):
        message = self.entry.get()
        if message.strip():
            self.client_socket.sendall(message.encode('utf-8')) # Send the message to the server
            self.entry.delete(0, END) # Clear the entry field after sending the message

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.Text.config(state=NORMAL) # Enable editing to insert the received message
                    self.Text.insert(END, message + '\n')
                    self.Text.see(END) # Auto-scroll
                    self.Text.config(state=DISABLED) # Disable editing again
            except:
                print("[Client] Connection to server lost.")
                break
    

def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed 

if __name__ == '__main__': # May be used ONLY for debugging
    main()