# Group#: A13
# Student Names: Renzon Gabriel, Yuqi Lao 

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

    def __init__(self, window: Tk) -> None:
        """Initializes the GUI, sets up the socket, and initiates the connection."""
        # --- Initialize GUI ---
        self.window = window
        self.window.title("Chat Client - " + current_process().name) # Display the current process name in the title
        self.window.configure(background="#def2fe")
        self.window.geometry("350x450")

        # Intercept the window closing event to shut down sockets cleanly
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        Label(self.window, text="Let's chit chat!").pack()

        self.text_area = Text(self.window, state=DISABLED) # Read-only
        self.text_area.pack(pady=5)

        input_frame = Frame(self.window, bg="#def2fe")
        input_frame.pack(pady=5, padx=10, fill=X)

        self.entry = Entry(input_frame, width=30)
        self.entry.pack(side=LEFT, padx=(0,5))

        Button(input_frame, text="Send", command=self.send_message).pack(side=LEFT)
        Button(self.window, text="Exit", command=self.on_closing).pack(anchor="e", padx=10, pady=10)

        # --- Initialize Socket Connection ---
        self.HOST = '127.0.0.1'
        self.PORT = 12345

        try:
            self.client_socket.connect((self.HOST, self.PORT))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except:
            print("[Client] Failed to establish connection to server.")

        # Start the connection attempt loop
        self.connect_to_server()

    # --- Socket Communication Methods ---
    def send_message(self) -> None:
        message = self.entry.get()
        if message.strip():
            self.client_socket.sendall(message.encode('utf-8')) # Send the message to the server
            self.entry.delete(0, END) # Clear the entry field after sending the message

    def receive_message(self) -> None:
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.text_area.config(state=NORMAL) # Enable editing to insert the received message
                    self.text_area.insert(END, message + '\n')
                    self.text_area.see(END) # Auto-scroll
                    self.text_area.config(state=DISABLED) # Disable editing again
            except:
                print("[CLIENT] Connection to server lost.")
                break
    
    # --- Helper Methods ---
    def connect_to_server(self) -> None:
        """Attempts to connect to the server. Retries using Tkinter's .after() if it fails."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
            print("[CLIENT] Connected to server successfully.")
            # Spawn listening thread only after successful connection
            threading.Thread(target=self.receive_message, daemon=True).start()
        except OSError:
            print("[CLIENT] Server not found. Retrying in 2 seconds...")
            self.client_socket.close()
            self.window.after(2000, self.connect_to_server) # Use Tkinter's native delay to retry without freezing the GUI

    def on_closing(self) -> None:
        """Safely closes the network socket before destroying the GUI window."""
        try:
            self.client_socket.close()
        except Exception:
            pass
        self.window.destroy()

def main() -> None: #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed 

if __name__ == '__main__': # May be used ONLY for debugging
    main()