# Model Context Protocol - Python SDK

## Defining Computational Tools with FastMCP in Python
This snippet demonstrates how to define tools using the `@mcp.tool()` decorator. Tools allow LLMs to perform actions, execute computations, and have side effects. Examples include a synchronous function for BMI calculation and an asynchronous function for fetching weather data using `httpx`.

```python
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text
```

## Implementing OAuth Authentication for MCP Client in Python
This snippet demonstrates how to set up OAuth authentication for an MCP client using the Python SDK. It includes a custom in-memory token storage implementation and shows how to initialize `OAuthClientProvider` and use it with `streamablehttp_client` and `ClientSession` to establish an authenticated session.

```python
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

class CustomTokenStorage(TokenStorage):
    """Simple in-memory token storage implementation."""

    async def get_tokens(self) -> OAuthToken | None:
        pass

    async def set_tokens(self, tokens: OAuthToken) -> None:
        pass

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        pass

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        pass

async def main():
    # Set up OAuth authentication
    oauth_auth = OAuthClientProvider(
        server_url="https://api.example.com",
        client_metadata=OAuthClientMetadata(
            client_name="My Client",
            redirect_uris=["http://localhost:3000/callback"],
            client_uri="http://localhost:3000",
            logo_uri="http://localhost:3000/logo.png",
            tos_uri="http://localhost:3000/tos",
            policy_uri="http://localhost:3000/policy",
            jwks_uri="http://localhost:3000/jwks",
        ),
        token_storage=CustomTokenStorage(),
    )

    # Create a client session with OAuth authentication
    async with ClientSession(
        streamablehttp_client("https://api.example.com/mcp"),
        auth=oauth_auth,
    ) as session:
        # Use the session to interact with the MCP server
        pass
```

## Creating a Simple MCP Server with FastMCP in Python
This snippet demonstrates how to create a simple MCP server using FastMCP. It defines a resource, a tool, and a prompt, and then starts the server using the Streamable HTTP transport.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn

mcp = FastMCP("My App")

@mcp.resource("greeting")
async def greeting(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.prompt()
def greeting_prompt(name: str) -> dict:
    """Create a greeting prompt for the given name."""
    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Say hello to {name}!"
                }
            }
        ]
    }

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing a Database Query Tool with MCP in Python
This snippet demonstrates how to implement a database query tool using MCP. It connects to a SQLite database and provides a tool to execute SQL queries.

```python
import sqlite3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Database Explorer")

@mcp.tool()
def query_database(sql: str) -> list:
    """Execute a SQL query against the database."""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

@mcp.resource("schema")
async def get_schema() -> str:
    """Get the database schema."""
    conn = sqlite3.connect("database.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        return "\n".join([table[0] for table in tables])
    finally:
        conn.close()
```

## Using the MCP Client to Interact with a Server in Python
This snippet demonstrates how to use the MCP client to interact with an MCP server. It shows how to connect to a server, list available tools and resources, and call tools.

```python
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    # Connect to an MCP server
    async with ClientSession(streamablehttp_client("https://api.example.com/mcp")) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Call a tool
        result = await session.call_tool("add", {"a": 5, "b": 3})
        print(f"Result of add tool: {result}")
        
        # List available resources
        resources = await session.list_resources()
        print(f"Available resources: {[resource.name for resource in resources]}")
        
        # Read a resource
        greeting = await session.read_resource("greeting://John")
        print(f"Greeting resource: {greeting}")
        
        # Get a prompt
        prompt = await session.get_prompt("greeting_prompt", {"name": "John"})
        print(f"Greeting prompt: {prompt}")
```

## Implementing Retry Logic for MCP Client in Python
This snippet demonstrates how to implement retry logic for MCP client requests. It uses a custom retry strategy to handle transient errors.

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def query_with_retries(session, tool_name, args, max_retries=3, initial_delay=1):
    """Execute a tool call with retry logic for transient errors."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            return await session.call_tool(tool_name, args)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise the exception
                raise
            
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
            # Exponential backoff
            delay *= 2

async def main():
    async with ClientSession(streamablehttp_client("https://api.example.com/mcp")) as session:
        try:
            result = await query_with_retries(session, "weather", {"city": "New York"})
            print(f"Weather result: {result}")
        except Exception as e:
            print(f"Failed after multiple retries: {e}")
```

## Implementing a File System Resource in MCP Python
This snippet demonstrates how to implement a file system resource in MCP. It allows accessing files on the server's file system through MCP resources.

```python
import os
from mcp.server.fastmcp import FastMCP
from mcp.server.resource import ResourceTemplate

mcp = FastMCP("File System Explorer")

@mcp.resource("file", ResourceTemplate("file://{path}"))
async def get_file(path: str) -> str:
    """Get the contents of a file."""
    if not os.path.exists(path):
        raise ValueError(f"File not found: {path}")
    
    with open(path, "r") as f:
        return f.read()

@mcp.resource("directory", ResourceTemplate("directory://{path}"))
async def list_directory(path: str) -> list:
    """List the contents of a directory."""
    if not os.path.exists(path) or not os.path.isdir(path):
        raise ValueError(f"Directory not found: {path}")
    
    return os.listdir(path)
```

## Implementing a Notification System with MCP in Python
This snippet demonstrates how to implement a notification system using MCP. It shows how to send notifications to clients when certain events occur.

```python
import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport

mcp = FastMCP("Notification System")

# Store connected clients
clients = set()

@mcp.on_connect
async def handle_connect(client_id):
    """Handle client connection."""
    clients.add(client_id)
    print(f"Client connected: {client_id}")

@mcp.on_disconnect
async def handle_disconnect(client_id):
    """Handle client disconnection."""
    if client_id in clients:
        clients.remove(client_id)
    print(f"Client disconnected: {client_id}")

@mcp.tool()
async def subscribe_to_notifications(topic: str) -> str:
    """Subscribe to notifications for a specific topic."""
    # In a real implementation, you would store the subscription
    return f"Subscribed to {topic}"

async def send_notifications():
    """Send periodic notifications to all connected clients."""
    while True:
        if clients:
            for client_id in clients:
                await mcp.send_notification(client_id, {
                    "type": "update",
                    "message": "This is a periodic update"
                })
        await asyncio.sleep(10)  # Send notification every 10 seconds

# Start the notification task when the server starts
@mcp.on_startup
async def startup():
    """Start the notification task when the server starts."""
    asyncio.create_task(send_notifications())

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing Authentication and Authorization in MCP Python
This snippet demonstrates how to implement authentication and authorization in an MCP server. It shows how to protect resources and tools with authentication requirements.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.auth import AuthProvider, AuthContext
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn

# Custom authentication provider
class SimpleAuthProvider(AuthProvider):
    async def authenticate(self, request) -> AuthContext:
        """Authenticate the request and return an AuthContext."""
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return AuthContext(authenticated=False)
        
        # Extract the token
        token = auth_header.replace("Bearer ", "")
        
        # Validate the token (in a real implementation, you would verify the token)
        if token == "valid-token":
            return AuthContext(
                authenticated=True,
                user_id="user123",
                scopes=["read", "write"]
            )
        
        return AuthContext(authenticated=False)

mcp = FastMCP("Authenticated App", auth_provider=SimpleAuthProvider())

@mcp.tool(requires_auth=True)
def protected_tool(data: str) -> str:
    """This tool requires authentication."""
    return f"Protected data: {data}"

@mcp.tool(requires_scopes=["write"])
def write_data(data: str) -> str:
    """This tool requires the 'write' scope."""
    return f"Data written: {data}"

@mcp.resource("protected", requires_auth=True)
async def protected_resource() -> str:
    """This resource requires authentication."""
    return "Protected resource content"

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing a Chat Application with MCP in Python
This snippet demonstrates how to implement a chat application using MCP. It shows how to manage chat sessions, send messages, and receive notifications.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn
import uuid
from datetime import datetime

mcp = FastMCP("Chat Application")

# Store chat messages
chat_messages = []

@mcp.tool()
async def send_message(user: str, message: str) -> dict:
    """Send a chat message."""
    msg_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    new_message = {
        "id": msg_id,
        "user": user,
        "message": message,
        "timestamp": timestamp
    }
    
    chat_messages.append(new_message)
    
    # Notify all clients about the new message
    await mcp.broadcast_notification({
        "type": "new_message",
        "message": new_message
    })
    
    return new_message

@mcp.tool()
async def get_messages(limit: int = 50) -> list:
    """Get recent chat messages."""
    return chat_messages[-limit:]

@mcp.resource("chat-history")
async def chat_history() -> str:
    """Get the chat history as a formatted string."""
    if not chat_messages:
        return "No messages yet."
    
    formatted = []
    for msg in chat_messages:
        formatted.append(f"[{msg['timestamp']}] {msg['user']}: {msg['message']}")
    
    return "\n".join(formatted)

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing a Weather Service with MCP in Python
This snippet demonstrates how to implement a weather service using MCP. It shows how to fetch weather data from an external API and provide it through MCP tools and resources.

```python
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn

mcp = FastMCP("Weather Service")

# Cache for weather data
weather_cache = {}

async def fetch_weather_data(city: str) -> dict:
    """Fetch weather data from an external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weatherapi.com/v1/current.json",
            params={
                "key": "your-api-key",
                "q": city
            }
        )
        return response.json()

@mcp.tool()
async def get_weather(city: str) -> dict:
    """Get the current weather for a city."""
    # Check cache first
    if city in weather_cache:
        return weather_cache[city]
    
    # Fetch from API
    weather_data = await fetch_weather_data(city)
    
    # Cache the result
    weather_cache[city] = weather_data
    
    return weather_data

@mcp.tool()
async def get_temperature(city: str) -> float:
    """Get the current temperature for a city in Celsius."""
    weather_data = await get_weather(city)
    return weather_data["current"]["temp_c"]

@mcp.resource("weather", ResourceTemplate("weather://{city}"))
async def weather_resource(city: str) -> str:
    """Get a formatted weather report for a city."""
    weather_data = await get_weather(city)
    
    current = weather_data["current"]
    location = weather_data["location"]
    
    return f"""
Weather for {location['name']}, {location['country']}:
Temperature: {current['temp_c']}°C ({current['temp_f']}°F)
Condition: {current['condition']['text']}
Wind: {current['wind_kph']} km/h
Humidity: {current['humidity']}%
    """

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing a Calculator with MCP in Python
This snippet demonstrates how to implement a calculator using MCP. It provides tools for basic arithmetic operations.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn

mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent

@mcp.prompt()
def calculator_prompt() -> dict:
    """Create a calculator prompt."""
    return {
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": "You are a calculator assistant. Use the provided tools to perform calculations."
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": "Please help me with a calculation."
                }
            }
        ]
    }

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Implementing a Todo List with MCP in Python
This snippet demonstrates how to implement a todo list application using MCP. It provides tools for managing tasks and a resource for viewing the task list.

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.transports.streamable_http import StreamableHttpTransport
import uvicorn
import uuid
from datetime import datetime

mcp = FastMCP("Todo List")

# Store tasks
tasks = {}

@mcp.tool()
def add_task(title: str, description: str = "") -> dict:
    """Add a new task to the todo list."""
    task_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "completed": False,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    tasks[task_id] = task
    return task

@mcp.tool()
def complete_task(task_id: str) -> dict:
    """Mark a task as completed."""
    if task_id not in tasks:
        raise ValueError(f"Task with ID {task_id} not found")
    
    tasks[task_id]["completed"] = True
    tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    return tasks[task_id]

@mcp.tool()
def update_task(task_id: str, title: str = None, description: str = None) -> dict:
    """Update a task's title or description."""
    if task_id not in tasks:
        raise ValueError(f"Task with ID {task_id} not found")
    
    if title is not None:
        tasks[task_id]["title"] = title
    
    if description is not None:
        tasks[task_id]["description"] = description
    
    tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    return tasks[task_id]

@mcp.tool()
def delete_task(task_id: str) -> dict:
    """Delete a task from the todo list."""
    if task_id not in tasks:
        raise ValueError(f"Task with ID {task_id} not found")
    
    task = tasks.pop(task_id)
    return {"success": True, "deleted_task": task}

@mcp.tool()
def list_tasks(completed: bool = None) -> list:
    """List all tasks, optionally filtered by completion status."""
    if completed is None:
        return list(tasks.values())
    
    return [task for task in tasks.values() if task["completed"] == completed]

@mcp.resource("todo-list")
async def todo_list() -> str:
    """Get the todo list as a formatted string."""
    if not tasks:
        return "No tasks yet."
    
    formatted = []
    for task in tasks.values():
        status = "[x]" if task["completed"] else "[ ]"
        formatted.append(f"{status} {task['title']}")
        if task["description"]:
            formatted.append(f"    {task['description']}")
    
    return "\n".join(formatted)

# Start the server with Streamable HTTP transport
if __name__ == "__main__":
    app = mcp.create_app(StreamableHttpTransport())
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Building and Deploying MCP Servers in Python

### Installation
```bash
pip install mcp-sdk
```

### Running a Simple Server
```bash
python -m mcp.server.run --app my_app:mcp
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "mcp.server.run", "--app", "my_app:mcp", "--host", "0.0.0.0", "--port", "8000"]
```

### Building the Docker Image
```bash
docker build -t my-mcp-server .
```

### Running the Docker Container
```bash
docker run -p 8000:8000 my-mcp-server
```