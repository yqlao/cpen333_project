# Group#: A13
# Student Names: Renzon Gabriel, Yuqi Lao

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
        """Initializes the GUI, sets up the listening socket, and starts the acceptor thread."""
        # --- Initialize GUI ---
        self.window = window
        self.window.title("Chat Server")
        self.window.configure(background="#def2fe")
        self.window.geometry("350x450")

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        Label(self.window, text="Let's chit chat!", bg="#def2fe").pack()

        self.text_area = Text(self.window, state=DISABLED) # Read-only
        self.text_area.pack(pady=5)
        # Text styles
        self.text_area.tag_config("system", foreground="#888888", font=("Helvetica", 9, "italic"))
        self.text_area.tag_config("chat", foreground="#000000", font=("Helvetica", 10, "normal"))
        self.text_area.tag_config("error", foreground="#d9534f", font=("Helvetica", 10, "bold"))

        input_frame = Frame(self.window, bg="#def2fe")
        input_frame.pack(pady=5, padx=10, fill=X)

        self.entry = Entry(input_frame, width=30)
        self.entry.pack(side=LEFT, padx=(0,5))

        # --- Initialize Socket Connection ---
        self.HOST = '127.0.0.1'
        self.PORT = 12345 # Base port number
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of the address to avoid "Address already in use" errors
        
        try:
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen()

            self.log_activity("Server is online and waiting for clients...") # Deafult: "system" tag
            print(f"[SERVER] Listening on {self.HOST}:{self.PORT}")

            self.clients = [] # List to keep track of connected clients
            threading.Thread(target=self.accept_clients, daemon=True).start() # Acceptor thread to handle incoming client connections and avoid blocking the GUI
        except OSError as e:
            print(f"[SERVER] Bind failed: {e}")
            self.log_activity(f"Failed to start server.", "error")

                
    def accept_clients(self) -> None:
        """ Accept incoming client connections and start a new thread for each client."""
        while True:
            try:
                conn, addr = self.server_socket.accept()
                client_port = addr[1] # Grab their unique port number
                # self.clients.append((conn, client_port)) # Store the connection and client ID
                # self.log_activity(f"Client at port {client_port} joined the chat.")
                print(f"[SERVER] Connection established with {addr[0]}:{addr[1]}")
                threading.Thread(target=self.receive_message, args=(conn, client_port), daemon=True).start() # Spawn a new thread for a new client connection
            except OSError:
                break # If the server socket is closed, break out of the loop to allow clean shutdown
                

    def receive_message(self, conn: socket.socket, client_id: int) -> None:
        """ Receive messages from a specific client and broadcast to others."""
        # Handshake: get client ID
        initial_data = conn.recv(1024)
        if not initial_data:
            conn.close()
            return
        client_id: str = initial_data.decode('utf-8')

        # Store the client connection and ID
        self.clients.append((conn, client_id))
        self.log_activity(f"{client_id} joined the chat.") # Display join message on server GUI

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break # Client gracefully disconnected

                # Display message on server GUI
                message = data.decode('utf-8')
                gui_message = f"{client_id}: {message}"
                self.log_activity(gui_message, "chat") # Uses the 'chat' tag

                # Broadcast the message to all other clients
                for c_conn, c_id in self.clients:
                    try:
                        c_conn.sendall(gui_message.encode('utf-8'))
                    except:
                        # If a broadcast fails, just skip them. Their own thread will clean them up.
                        continue

            except:
                print(f"[SERVER] Connection with {client_id} lost.")
                break
        
        # --- Clean Up if a Client Disconnects ---
        self.log_activity(f"{client_id} left the chat.")
        print(f"[SERVER] Cleaning up socket for {client_id}")
        self.clients = [(c, cid) for c, cid in self.clients if cid != client_id] # Remove the disconnected client from the list
        conn.close()

    def log_activity(self, msg: str, tag: str = "system") -> None:
        """Helper method to update the server's visual log."""
        self.text_area.config(state=NORMAL)
        self.text_area.insert(END, f"{msg}\n", tag)
        self.text_area.see(END)
        self.text_area.config(state=DISABLED)

    def on_closing(self) -> None:
        """ Shuts down the server, disconnecting all clients and freeing the port."""
        for c_conn, _ in self.clients:
            try:
                c_conn.close() # Attempt to close all client connections gracefully
            except Exception:
                pass
        try:
            self.server_socket.close() # Close the server socket to free the port
        except Exception:
            pass
        self.window.destroy()

def main()-> None: #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()