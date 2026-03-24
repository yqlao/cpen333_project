# CPEN333 Course Project


This repository contains the implementation for a two-part Python course project. It features a simplified, interactive Snake game and a multi-process local chat application.

## Part 1: Simplified Snake Game
A custom implementation of the classic Snake game, featuring specific logic for prey generation and collision detection.

**Key Mechanics & Design Decisions:**
* **Prey Capture Logic:** *placeholder*
* **Smart Prey Placement:** *placeholder*

**System Architecture:**
* *placeholder*

## Part 2: Simple Chat Application
A local chat application designed to demonstrate concurrent programming and networking. The app runs entirely on the loopback address (`127.0.0.1`).

**System Architecture:**
* `main.py`: The application entry point. It uses `multiprocessing` to spawn and manage the server and client processes.
* `server.py`: Manages network connections and broadcasts messages between connected clients.
* `client.py`: Features a `tkinter` GUI for users to send and receive messages in real-time.

**Tech Stack:**
* `socket` (Networking)
* `multiprocessing` & `threading` (Concurrency)
* `tkinter` (GUI)

## How to Run
*(Execution instructions to be added once the implementation is complete)*