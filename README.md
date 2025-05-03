# Taskmanager - A multi-user task management system - CLI
Distributed System - Microservice Architecture

## Core Features

### 1. User Management
Each user has a unique ID (upon registration).
Login is done using this unique ID.

### 2. Task Management
Users can create tasks. 
Assign tasks to other users. Owners of tasks can add/remove members from the task.
Mark tasks as "In Progress" or "Done". 
Comments/messages inside each task for better task management.

## Architecture
microservice architecture
```mermaid
graph TD;
    Client-->Middleware;
    Middleware-->Server;
    Server-->jsonDB;
    Server--> chat_service, Task_service, user_service;
```

### Components:
1. Client 
2. Server(s) (multi-threaded)
3. Middleware (Load Balancer) that assigns clients to servers.
4. Storage: Mock database using JSON

Written in Python.

### install required packages
```pip install requests rich flask fasteners``` 
To check the list of installed packages in your local machine use ```pip list```

## How to run it? (Example terminal codes are for Windows. Might not work on Mac/Linux)
1. Clone the GitHub repo
2. Open Terminal/Powershell
3. Get inside folder named "taskmanager" ```cd taskmanager```
4. Run middleware first ```python middleware\load_balancer.py```
5. Next, run the server as many times as you want (recommended max 3 for local server) in a separate terminal ```python -m server.main 5000``` *** Remember to change the port for each server, like (server 2) ```python -m server.main 5001``` (server 3) ```python -m server.main 5002``` ***
6. Next, simultaneously run as many clients as you want in separate terminal windows ```python client/client.py```
7. Use the system from the client terminal CLI. The terminal will provide all the system features commands. Enjoy!