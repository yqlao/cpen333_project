# Group#: A13
# Student Names: 

#Content of server.py; To complete/implement

from tkinter import *
import socket
import threading

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sents 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    See the project info/video for the specs.
    """
    # To implement 
    def __init__(self, window):
        # --- Initialize GUI ---
        self.window = window

        self.window.title("Chat Server")
        self.window.configure(background="#def2fe")
        self.window.geometry("350x450")

        Label(self.window, text="Let's chit chat!").pack()

        self.Text = Text(self.window, state=DISABLED) # Read-only
        self.Text.pack(pady=5)

        input_frame = Frame(self.window, bg="#def2fe")
        input_frame.pack(pady=5, padx=10, fill=X)
        self.entry = Entry(input_frame, width=30)
        self.entry.pack(side=LEFT, padx=(0,5))

        # --- Initialize Socket Connection ---
        self.HOST = '127.0.0.1'
        self.PORT = 12345 # Base port number
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of the address to avoid "Address already in use" errors
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()

        self.clients = [] # List to keep track of connected clients

        threading.Thread(target=self.accept_clients, daemon=True).start() # Acceptor thread to handle incoming client connections and avoid blocking the GUI
                
    def accept_clients(self):
        """ Accept incoming client connections and start a new thread for each client."""
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Connected by {addr}")
            client_id = addr[1] # Grab their unique port to use as an ID
            self.clients.append((conn, client_id)) # Store the connection and client ID
            threading.Thread(target=self.receive_message, args=(conn, client_id), daemon=True).start() # Spawn a new thread for a new client connection
                

    def receive_message(self, conn, client_id):
        """ Receive messages from a specific client and broadcast to others."""
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                # Display message on server GUI
                message = data.decode('utf-8')
                gui_message = f"Client {client_id}: {message}"
                self.Text.config(state=NORMAL)
                self.Text.insert(END, gui_message + '\n')
                self.Text.see(END)
                self.Text.config(state=DISABLED)

                # Broadcast the message to all other clients
                for c_conn, c_id in self.clients:
                    try:
                        c_conn.sendall(gui_message.encode('utf-8'))
                    except:
                        # If a broadcast fails, just skip them. Their own thread will clean them up.
                        continue

            except:
                print(f"[Server] Connection with client {client_id} lost.")
                break
        
        # --- Clean Up if a Client Disconnects ---
        self.clients = [(c_conn, c_id) for c_conn, c_id in self.clients if c_id != client_id] # Remove the disconnected client from the list
        conn.close() # close the connection


def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()