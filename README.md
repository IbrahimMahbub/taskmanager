# Taskmanager - A multi user task management system - CLI 
Distributed System - Microservice Architecture

## Core Features

### 1 User Management
Each user has a unique ID (upon registration).
Login is done using this unique ID.

### 2 Task Management
Tasks can be created by users. 
Assigned tasks to other users. Owners of tasks can Add/remove members from the task.
Mark tasks as "In Progress" or "Done". 
Comments/message inside each task for better task management.

## Architecture
microservice architecture
```mermaid
graph TD;
    Client-->Middleware (LB);
    Middleware (LB)-->Server(s);
    Server(s)-->json DB;
    Server(s)-->chat_service,Task_service,user_service;
```



### Components:
1. Client 
2. Server(s) (multi-threaded)
3. Middleware (Load Balancer) that assigns clients to servers.

4. Storage: Mock database using JSON

Written in Python.

## How to run it? (example terminal codes are for Windows. might not work on Mac/Linux)
1. Clone the Github repo
2. Get inside folder named "taskmanager" ```cd taskmanager```
3. open Terminal/Powershell
4. Run middleware first ```python middleware\load_balancer.py```
5. Next, run server as many as you want (recommanded max 3 for local server) in a separate terminal ```python -m server.main 5000``` 
*** Remember to change port for each server like (server 2) ```python -m server.main 5001``` (server 3) ```python -m server.main 5002``` ***
6. Next run as many clients as you want at the same time in saperate terminal window. ```python client/client.py```
7. User the system from the client terminal CLI, You will get all the system features command on the chat terminal. Enjoy! 