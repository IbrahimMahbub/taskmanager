import requests
import threading
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from typing import Optional, Tuple, Dict, List

class TaskManagerClient:
    def __init__(self):
        self.console = Console()
        self.middleware_url = "http://localhost:8000/connect"
        self.server_url: Optional[str] = None
        self.user_id: Optional[str] = None
        self.username: Optional[str] = None
        self.console_lock = threading.Lock()
        self.chat_refresh_interval = 3  # seconds

    def connect_to_server(self) -> bool:
        """Connect to an available server through the load balancer"""
        try:
            response = requests.get(self.middleware_url, timeout=5)  # Sends a GET request
            response.raise_for_status()  # Raises an exception for bad HTTP responses (e.g., 404)
            data = response.json()  # Parse the JSON response to get host and port
            self.server_url = f"http://{data['host']}:{data['port']}"  # Construct server URL
            self.console.print(Panel.fit(
                f"[green]Connected to server: [bold]{self.server_url}[/bold][/green]",
                title="Connection Established"
            ))
            return True
        except Exception as e:
            # If an exception occurs print the error and return False
            self.console.print(Panel.fit(
                f"[red]Error connecting to middleware:[/red] {str(e)}",
                title="Connection Failed",
                border_style="red"
            ))
            return False

    # Continue with the rest



    def register(self) -> Tuple[Optional[str], Optional[str]]:
        """Register a new user"""
        username = Prompt.ask("Enter your username").strip()
        if not username:
            self.console.print("[red]Username cannot be empty[/red]")
            return None, None

        try:
            response = requests.post(
                f"{self.server_url}/user/register",
                json={"username": username},
                timeout=5
            )
            if response.ok:
                user_data = response.json()
                self.console.print(Panel.fit(
                    f"[green]Registration successful![/green]\n"
                    f"User ID: [bold]{user_data['user_id']}[/bold]",
                    title="Success"
                ))
                return user_data['user_id'], username
            else:
                self.console.print(f"[red]Registration failed:[/red] {response.text}")
        except Exception as e:
            self.console.print(f"[red]Error during registration:[/red] {str(e)}")
        
        return None, None

    def login(self) -> Tuple[Optional[str], Optional[str]]:
        """Login with existing user credentials"""
        user_id = Prompt.ask("Enter your User ID").strip()
        if not user_id:
            self.console.print("[red]User ID cannot be empty[/red]")
            return None, None

        try:
            response = requests.post(
                f"{self.server_url}/user/login",
                json={"user_id": user_id},
                timeout=5
            )
            if response.ok:
                user_data = response.json()
                username = user_data.get("username", "Unknown")
                self.console.print(Panel.fit(
                    f"[green]Welcome back, [bold]{username}[/bold]![/green]",
                    title="Login Successful"
                ))
                return user_id, username
            else:
                self.console.print(f"[red]Login failed:[/red] {response.text}")
        except Exception as e:
            self.console.print(f"[red]Error during login:[/red] {str(e)}")
        
        return None, None

    def create_task(self) -> None:
        """Create a new task"""
        if not self.user_id:
            self.console.print("[yellow]Please login first[/yellow]")
            return

        title = Prompt.ask("Enter task title").strip()
        if not title:
            self.console.print("[red]Task title cannot be empty[/red]")
            return

        try:
            response = requests.post(
                f"{self.server_url}/task/create",
                json={"title": title, "owner_id": self.user_id},
                timeout=5
            )
            if response.ok:
                self.console.print(
                    f"[green]Task created with ID:[/green] [bold]{response.json()['task_id']}[/bold]"
                )
            else:
                self.console.print(f"[red]Failed to create task:[/red] {response.text}")
        except Exception as e:
            self.console.print(f"[red]Error creating task:[/red] {str(e)}")

    def list_tasks(self) -> List[Dict]:
        """Retrieve and display user's tasks"""
        if not self.user_id:
            return []

        try:
            response = requests.get(
                f"{self.server_url}/task/list",
                params={"user_id": self.user_id},
                timeout=5
            )
            if response.ok:
                return response.json()
            else:
                self.console.print(f"[red]Failed to retrieve tasks:[/red] {response.text}")
        except Exception as e:
            self.console.print(f"[red]Error fetching tasks:[/red] {str(e)}")
        
        return []

    def display_tasks(self, tasks: List[Dict]) -> None:
        """Display tasks in a rich table"""
        table = Table(title="Your Tasks", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Status", justify="right")
        table.add_column("Owner", justify="right")

        for task in tasks:
            status_color = {
                "Pending": "yellow",
                "In Progress": "blue",
                "Done": "green"
            }.get(task["status"], "red")
            
            owner_indicator = "👑" if task.get("owner_id") == self.user_id else ""
            table.add_row(
                task["id"],
                task["title"],
                f"[{status_color}]{task['status']}[/{status_color}]",
                owner_indicator
            )

        self.console.print(table)

    # (top parts of the class remain unchanged...)

    def get_username(self, user_id: str) -> str:
        """Fetch username from user ID"""
        try:
            response = requests.get(f"{self.server_url}/user/info", params={"user_id": user_id}, timeout=5)
            if response.ok:
                return response.json().get("username", "Unknown")
        except Exception:
            pass
        return "Unknown"

    def view_task(self, task: Dict) -> None:
        """View and interact with a specific task"""
        self.console.print(Panel.fit(
            f"[bold]{task['title']}[/bold]\n"
            f"Status: [blue]{task['status']}[/blue] | "
            f"ID: [cyan]{task['id']}[/cyan]",
            title="Task Details"
        ))

        chat_stop_flag = threading.Event()
        last_chat = []

        def fetch_chat() -> List[Dict]:
            try:
                response = requests.get(
                    f"{self.server_url}/chat/get",
                    params={"task_id": task["id"]},
                    timeout=3
                )
                return response.json() if response.ok else []
            except Exception:
                return []

        def print_chat(messages: List[Dict]) -> None:
            with self.console_lock:
                for msg in messages:
                    sender_id = msg.get("user_id", "unknown")
                    sender_name = msg.get("username") or self.get_username(sender_id)
                    display_name = "[bold green]You[/bold green]" if sender_id == self.user_id else f"[cyan]{sender_name}[/cyan]"
                    self.console.print(
                        f"{display_name}: {msg['message']}\n"
                        f"[dim]{msg.get('timestamp', '')}[/dim]"
                    )

        def auto_refresh() -> None:
            nonlocal last_chat
            while not chat_stop_flag.is_set():
                current_chat = fetch_chat()
                new_messages = current_chat[len(last_chat):]
                if new_messages:
                    print_chat(new_messages)
                    last_chat = current_chat
                time.sleep(self.chat_refresh_interval)

        # Initial chat display
        last_chat = fetch_chat()
        if last_chat:
            self.console.print(Panel.fit("[bold]Chat History[/bold]"))
            print_chat(last_chat)
        else:
            self.console.print("[dim]No messages yet[/dim]")

        refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
        refresh_thread.start()

        try:
            while True:
                with self.console_lock:
                    options = [
                        "Send message",
                        "Update status",
                        "Assign user" if task.get("owner_id") == self.user_id else None,
                        "Remove user" if task.get("owner_id") == self.user_id else None,
                        "Back to main menu"
                    ]
                    options = [opt for opt in options if opt]

                    for i, opt in enumerate(options, 1):
                        self.console.print(f"{i}. {opt}")

                choice = IntPrompt.ask("\nChoose an option", choices=[str(i) for i in range(1, len(options)+1)], show_choices=False)

                if choice == 1:
                    message = Prompt.ask("Your message").strip()
                    if message:
                        try:
                            response = requests.post(
                                f"{self.server_url}/chat/send",
                                json={
                                    "task_id": task["id"],
                                    "user_id": self.user_id,
                                    "message": message
                                },
                                timeout=5
                            )
                            if not response.ok:
                                self.console.print(f"[red]Failed to send message:[/red] {response.text}")
                        except Exception as e:
                            self.console.print(f"[red]Error sending message:[/red] {str(e)}")

                elif choice == 2:
                    new_status = Prompt.ask("New status", choices=["Pending", "In Progress", "Done"], default=task["status"])
                    try:
                        response = requests.post(
                            f"{self.server_url}/task/status",
                            json={"task_id": task["id"], "status": new_status},
                            timeout=5
                        )
                        if response.ok:
                            task["status"] = new_status
                            self.console.print("[green]Status updated successfully[/green]")
                        else:
                            self.console.print(f"[red]Failed to update status:[/red] {response.text}")
                    except Exception as e:
                        self.console.print(f"[red]Error updating status:[/red] {str(e)}")

                elif choice == 3 and task.get("owner_id") == self.user_id:
                    user_id = Prompt.ask("Enter User ID to assign").strip()
                    if user_id:
                        try:
                            response = requests.post(
                                f"{self.server_url}/task/assign",
                                json={"task_id": task["id"], "user_id": user_id, "actor_id": self.user_id},
                                timeout=5
                            )
                            if response.ok:
                                self.console.print("[green]User assigned successfully[/green]")
                            else:
                                self.console.print(f"[red]Failed to assign user:[/red] {response.text}")
                        except Exception as e:
                            self.console.print(f"[red]Error assigning user:[/red] {str(e)}")

                elif choice == 4 and task.get("owner_id") == self.user_id:
                    user_id = Prompt.ask("Enter User ID to remove").strip()
                    if user_id:
                        try:
                            response = requests.post(
                                f"{self.server_url}/task/remove",
                                json={"task_id": task["id"], "user_id": user_id, "actor_id": self.user_id},
                                timeout=5
                            )
                            if response.ok:
                                self.console.print("[green]User removed successfully[/green]")
                            else:
                                self.console.print(f"[red]Failed to remove user:[/red] {response.text}")
                        except Exception as e:
                            self.console.print(f"[red]Error removing user:[/red] {str(e)}")

                elif choice == len(options):
                    break

        finally:
            chat_stop_flag.set()
            refresh_thread.join()


    def dashboard(self) -> None:
        """Main user dashboard"""
        while True:
            tasks = self.list_tasks()
            self.display_tasks(tasks)

            options = [
                "Create new task",
                "View task details" if tasks else None,
                "Logout"
            ]
            options = [opt for opt in options if opt is not None]

            for i, opt in enumerate(options, 1):
                self.console.print(f"{i}. {opt}")

            choice = IntPrompt.ask(
                "Choose an option",
                choices=[str(i) for i in range(1, len(options)+1)],
                show_choices=False
            )

            if choice == 1:
                self.create_task()
            elif choice == 2 and tasks:
                task_id = Prompt.ask("Enter Task ID").strip()
                selected_task = next((t for t in tasks if t["id"] == task_id), None)
                if selected_task:
                    self.view_task(selected_task)
                else:
                    self.console.print("[red]Invalid Task ID[/red]")
            elif choice == len(options):
                self.user_id = None
                self.username = None
                break



    def main_menu(self) -> None:
        """Application entry point"""
        while True:
            self.console.print(Panel.fit(
                "[bold]Task Management System[/bold]",
                subtitle="Choose from below"
            ))

            choice = IntPrompt.ask(
                "1. Register\n2. Login\n3. Exit\nChoose an option", 
                choices=["1", "2", "3"],
                show_choices=False
            )

            if choice == 1:  # Register
                self.user_id, self.username = self.register()
                if self.user_id:
                    self.dashboard()
            elif choice == 2:  # Login
                self.user_id, self.username = self.login()
                if self.user_id:
                    self.dashboard()
            elif choice == 3:  # Exit
                self.console.print("[bold]Goodbye![/bold]")
                break

    def run(self) -> None:
        """Run the client application"""
        if not self.connect_to_server():
            return

        self.main_menu()

if __name__ == "__main__":
    client = TaskManagerClient()
    client.run()