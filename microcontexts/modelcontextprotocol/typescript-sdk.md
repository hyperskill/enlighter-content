# Model Context Protocol - TypeScript SDK

## Implementing an Echo MCP Server with Resources, Tools, and Prompts
This example showcases a simple MCP server named "Echo" that defines a resource, a tool, and a prompt. The "echo" resource returns the input message as text, the "echo" tool returns the input message as content, and the "echo" prompt formats the input message into a user message. It demonstrates basic usage of McpServer, ResourceTemplate, and Zod for schema validation.

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "Echo",
  version: "1.0.0"
});

server.resource(
  "echo",
  new ResourceTemplate("echo://{message}", { list: undefined }),
  async (uri, { message }) => ({
    contents: [{
      uri: uri.href,
      text: `Resource echo: ${message}`
    }]
  })
);

server.tool(
  "echo",
  { message: z.string() },
  async ({ message }) => ({
    content: [{ type: "text", text: `Tool echo: ${message}` }]
  })
);

server.prompt(
  "echo",
  { message: z.string() },
  ({ message }) => ({
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Please process this message: ${message}`
      }
    }]
  })
);
```

## Implementing Simple and Asynchronous MCP Tools
This example demonstrates how to register tools with an MCP server. It includes a simple 'calculate-bmi' tool that performs a calculation and an asynchronous 'fetch-weather' tool that makes an external API call, showcasing how tools enable LLMs to perform actions and interact with external services.

```typescript
// Simple tool with parameters
server.tool(
  "calculate-bmi",
  {
    weightKg: z.number(),
    heightM: z.number()
  },
  async ({ weightKg, heightM }) => ({
    content: [{
      type: "text",
      text: String(weightKg / (heightM * heightM))
    }]
  })
);

// Async tool with external API call
server.tool(
  "fetch-weather",
  { city: z.string() },
  async ({ city }) => {
    const response = await fetch(`https://api.weather.com/${city}`);
    const data = await response.text();
    return {
      content: [{ type: "text", text: data }]
    };
  }
);
```

## Proxying OAuth Requests Upstream with Model Context Protocol SDK
This snippet demonstrates how to configure the Model Context Protocol SDK's mcpAuthRouter to proxy OAuth authorization requests to an external provider using ProxyOAuthServerProvider. It shows how to define external OAuth endpoints, implement custom access token validation, and manage client redirect URIs, allowing delegation of OAuth flow while maintaining control.

```typescript
import express from 'express';
import { ProxyOAuthServerProvider } from '@modelcontextprotocol/sdk/server/auth/providers/proxyProvider.js';
import { mcpAuthRouter } from '@modelcontextprotocol/sdk/server/auth/router.js';

const app = express();

const proxyProvider = new ProxyOAuthServerProvider({
    endpoints: {
        authorizationUrl: "https://auth.external.com/oauth2/v1/authorize",
        tokenUrl: "https://auth.external.com/oauth2/v1/token",
        revocationUrl: "https://auth.external.com/oauth2/v1/revoke"
    },
    verifyAccessToken: async (token) => {
        return {
            token,
            clientId: "123",
            scopes: ["openid", "email", "profile"]
        }
    },
    getClient: async (client_id) => {
        return {
            client_id,
            redirect_uris: ["http://localhost:3000/callback"]
        }
    }
})

app.use(mcpAuthRouter({
    provider: proxyProvider,
    issuerUrl: new URL("http://auth.external.com"),
    baseUrl: new URL("http://mcp.example.com"),
    serviceDocumentationUrl: new URL("https://docs.example.com/")
}))
```

## Interacting with MCP Servers using the High-Level Client
This snippet demonstrates how to use the high-level Client interface to connect to an MCP server and perform various operations. It covers listing prompts and resources, getting specific prompts and resources, and calling tools, showcasing the client's capabilities for interacting with a connected server.

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "node",
  args: ["server.js"]
});

const client = new Client(
  {
    name: "example-client",
    version: "1.0.0"
  }
);

await client.connect(transport);

// List prompts
const prompts = await client.listPrompts();

// Get a prompt
const prompt = await client.getPrompt({
  name: "example-prompt",
  arguments: {
    arg1: "value"
  }
});

// List resources
const resources = await client.listResources();

// Read a resource
const resource = await client.readResource({
  uri: "file:///example.txt"
});

// Call a tool
const result = await client.callTool({
  name: "example-tool",
  arguments: {
    arg1: "value"
  }
});
```

## Setting Up Streamable HTTP Server with Session Management
This comprehensive example sets up an Express.js server to handle MCP communication over Streamable HTTP, including session management. It uses `StreamableHTTPServerTransport` to manage client-to-server requests (POST), server-to-client notifications (GET via SSE), and session termination (DELETE), ensuring stateful interactions across requests using session IDs.

```typescript
import express from "express";
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js"



const app = express();
app.use(express.json());

// Map to store transports by session ID
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

// Handle POST requests for client-to-server communication
app.post('/mcp', async (req, res) => {
  // Check for existing session ID
  const sessionId = req.headers['mcp-session-id'] as string | undefined;
  let transport: StreamableHTTPServerTransport;

  if (sessionId && transports[sessionId]) {
    // Reuse existing transport
    transport = transports[sessionId];
  } else if (!sessionId && isInitializeRequest(req.body)) {
    // New initialization request
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sessionId) => {
        // Store the transport by session ID
        transports[sessionId] = transport;
      }
    });

    // Clean up transport when closed
    transport.onclose = () => {
      if (transport.sessionId) {
        delete transports[transport.sessionId];
      }
    };
    const server = new McpServer({
      name: "example-server",
      version: "1.0.0"
    });

    // ... set up server resources, tools, and prompts ...

    // Connect to the MCP server
    await server.connect(transport);
  } else {
    // Invalid request
    res.status(400).json({
      jsonrpc: '2.0',
      error: {
        code: -32000,
        message: 'Bad Request: No valid session ID provided',
      },
      id: null,
    });
    return;
  }

  // Handle the request
  await transport.handleRequest(req, res, req.body);
});

// Reusable handler for GET and DELETE requests
const handleSessionRequest = async (req: express.Request, res: express.Response) => {
  const sessionId = req.headers['mcp-session-id'] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send('Invalid or missing session ID');
    return;
  }

  const transport = transports[sessionId];
  await transport.handleRequest(req, res);
};

// Handle GET requests for server-to-client notifications via SSE
app.get('/mcp', handleSessionRequest);

// Handle DELETE requests for session termination
app.delete('/mcp', handleSessionRequest);

app.listen(3000);
```

## Creating a Basic MCP Server with Tools and Resources
This snippet demonstrates how to set up a simple MCP server. It initializes an `McpServer` instance, registers an 'add' tool for basic arithmetic, and defines a dynamic 'greeting' resource. Finally, it connects the server to a `StdioServerTransport` to handle communication via standard input/output.

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create an MCP server
const server = new McpServer({
  name: "Demo",
  version: "1.0.0"
});

// Add an addition tool
server.tool("add",
  { a: z.number(), b: z.number() },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }]
  })
);

// Add a dynamic greeting resource
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [{
      uri: uri.href,
      text: `Hello, ${name}!`
    }]
  })
);

// Start receiving messages on stdin and sending messages on stdout
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Building an MCP Server for SQLite Database Exploration
This snippet provides a more complex MCP server example that integrates with a SQLite database. It defines a "schema" resource to retrieve the database schema (table SQL definitions) and a "query" tool to execute arbitrary SQL queries against the database. It uses sqlite3 and promisify for asynchronous database operations and includes error handling for queries.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import sqlite3 from "sqlite3";
import { promisify } from "util";
import { z } from "zod";

const server = new McpServer({
  name: "SQLite Explorer",
  version: "1.0.0"
});

// Helper to create DB connection
const getDb = () => {
  const db = new sqlite3.Database("database.db");
  return {
    all: promisify<string, any[]>(db.all.bind(db)),
    close: promisify(db.close.bind(db))
  };
};

server.resource(
  "schema",
  "schema://main",
  async (uri) => {
    const db = getDb();
    try {
      const tables = await db.all(
        "SELECT sql FROM sqlite_master WHERE type='table'"
      );
      return {
        contents: [{
          uri: uri.href,
          text: tables.map((t: {sql: string}) => t.sql).join("\n")
        }]
      };
    } finally {
      await db.close();
    }
  }
);

server.tool(
  "query",
  { sql: z.string() },
  async ({ sql }) => {
    const db = getDb();
    try {
      const results = await db.all(sql);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(results, null, 2)
        }]
      };
    } catch (err: unknown) {
      const error = err as Error;
      return {
        content: [{
          type: "text",
          text: `Error: ${error.message}`
        }],
        isError: true
      };
    } finally {
      await db.close();
    }
  }
);
```

## Running Simple Streamable HTTP Server
This command starts a basic MCP server implementing the Streamable HTTP transport, featuring session management, in-memory event store for resumability, `greet` and `multi-greet` tools, `greeting-template` prompt, static resource exposure, SSE notification support, and session termination via DELETE requests.

```bash
npx tsx src/examples/server/simpleStreamableHttp.ts
```

## Creating Dynamic MCP Servers with Tool Management
This snippet demonstrates how to create an McpServer that can dynamically enable, disable, update, and remove tools after connection. It shows how listChanged notifications are automatically emitted upon tool state changes, allowing for adaptive server behavior based on user actions or external state.

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "Dynamic Example",
  version: "1.0.0"
});

const listMessageTool = server.tool(
  "listMessages",
  { channel: z.string() },
  async ({ channel }) => ({
    content: [{ type: "text", text: await listMessages(channel) }]
  })
);

const putMessageTool = server.tool(
  "putMessage",
  { channel: z.string(), message: z.string() },
  async ({ channel, message }) => ({
    content: [{ type: "text", text: await putMessage(channel, string) }]
  })
);
// Until we upgrade auth, `putMessage` is disabled (won't show up in listTools)
putMessageTool.disable()

const upgradeAuthTool = server.tool(
  "upgradeAuth",
  { permission: z.enum(["write', admin"])},
  // Any mutations here will automatically emit `listChanged` notifications
  async ({ permission }) => {
    const { ok, err, previous } = await upgradeAuthAndStoreToken(permission)
    if (!ok) return {content: [{ type: "text", text: `Error: ${err}` }]}

    // If we previously had read-only access, 'putMessage' is now available
    if (previous === "read") {
      putMessageTool.enable()
    }

    if (permission === 'write') {
      // If we've just upgraded to 'write' permissions, we can still call 'upgradeAuth' 
      // but can only upgrade to 'admin'. 
      upgradeAuthTool.update({
        paramSchema: { permission: z.enum(["admin"]) }, // change validation rules
      })
    } else {
      // If we're now an admin, we no longer have anywhere to upgrade to, so fully remove that tool
      upgradeAuthTool.remove()
    }
  }
)

// Connect as normal
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Setting up a Stateless MCP Server with Express.js
This snippet demonstrates how to create a stateless Model Context Protocol (MCP) server using Express.js. It sets up a POST endpoint '/mcp' to handle incoming MCP requests, ensuring each request is processed with a new, isolated StreamableHTTPServerTransport and McpServer instance to prevent request ID collisions in concurrent environments. It also defines GET and DELETE endpoints that return 'Method not allowed' errors.

```typescript
const app = express();
app.use(express.json());

app.post('/mcp', async (req: Request, res: Response) => {
  // In stateless mode, create a new instance of transport and server for each request
  // to ensure complete isolation. A single instance would cause request ID collisions
  // when multiple clients connect concurrently.

  try {
    const server = getServer(); 
    const transport: StreamableHTTPServerTransport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    res.on('close', () => {
      console.log('Request closed');
      transport.close();
      server.close();
    });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error('Error handling MCP request:', error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: '2.0',
        error: {
          code: -32603,
          message: 'Internal server error',
        },
        id: null,
      });
    }
  }
});

app.get('/mcp', async (req: Request, res: Response) => {
  console.log('Received GET MCP request');
  res.writeHead(405).end(JSON.stringify({
    jsonrpc: "2.0",
    error: {
      code: -32000,
      message: "Method not allowed."
    },
    id: null
  }));
});

app.delete('/mcp', async (req: Request, res: Response) => {
  console.log('Received DELETE MCP request');
  res.writeHead(405).end(JSON.stringify({
    jsonrpc: "2.0",
    error: {
      code: -32000,
      message: "Method not allowed."
    },
    id: null
  }));
});


// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`MCP Stateless Streamable HTTP Server listening on port ${PORT}`);
});
```

## Defining Static and Dynamic MCP Resources
This snippet illustrates how to define both static and dynamic resources on an MCP server. Static resources provide fixed data, while dynamic resources use `ResourceTemplate` to allow URI parameters (like `userId`) to fetch context-specific information for LLMs.

```typescript
// Static resource
server.resource(
  "config",
  "config://app",
  async (uri) => ({
    contents: [{
      uri: uri.href,
      text: "App configuration here"
    }]
  })
);

// Dynamic resource with parameters
server.resource(
  "user-profile",
  new ResourceTemplate("users://{userId}/profile", { list: undefined }),
  async (uri, { userId }) => ({
    contents: [{
      uri: uri.href,
      text: `Profile data for user ${userId}`
    }]
  })
);
```

## Running Streamable HTTP Client
This command executes a full-featured interactive client demonstrating connection management, tool and prompt calls, notification handling, resource listing, session termination, and resumability with Last-Event-ID tracking, connecting to a Streamable HTTP server.

```bash
npx tsx src/examples/client/simpleStreamableHttp.ts
```

## Implementing Server-Side Transport Compatibility for Model Context Protocol SDK
This snippet shows how a Model Context Protocol server can support both modern StreamableHTTPServerTransport and deprecated SSEServerTransport clients. It sets up Express routes to handle different transport types, including a legacy SSE endpoint and a message endpoint for older clients, ensuring backwards compatibility while encouraging migration to Streamable HTTP.

```typescript
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

const server = new McpServer({
  name: "backwards-compatible-server",
  version: "1.0.0"
});

// ... set up server resources, tools, and prompts ...

const app = express();
app.use(express.json());

// Store transports for each session type
const transports = {
  streamable: {} as Record<string, StreamableHTTPServerTransport>,
  sse: {} as Record<string, SSEServerTransport>
};

// Modern Streamable HTTP endpoint
app.all('/mcp', async (req, res) => {
  // Handle Streamable HTTP transport for modern clients
  // Implementation as shown in the "With Session Management" example
  // ...
});

// Legacy SSE endpoint for older clients
app.get('/sse', async (req, res) => {
  // Create SSE transport for legacy clients
  const transport = new SSEServerTransport('/messages', res);
  transports.sse[transport.sessionId] = transport;

  res.on("close", () => {
    delete transports.sse[transport.sessionId];
  });

  await server.connect(transport);
});

// Legacy message endpoint for older clients
app.post('/messages', async (req, res) => {
  const sessionId = req.query.sessionId as string;
  const transport = transports.sse[sessionId];
  if (transport) {
    await transport.handlePostMessage(req, res, req.body);
  } else {
    res.status(400).send('No transport found for sessionId');
  }
});

app.listen(3000);
```

## Implementing Client-Side Transport Fallback for Model Context Protocol SDK
This snippet illustrates how a Model Context Protocol client can attempt to connect using the modern StreamableHTTPClientTransport and gracefully fall back to the deprecated SSEClientTransport if the initial connection fails. This ensures backwards compatibility for clients interacting with servers that might use older transport versions.

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
let client: Client|undefined = undefined
const baseUrl = new URL(url);
try {
  client = new Client({
    name: 'streamable-http-client',
    version: '1.0.0'
  });
  const transport = new StreamableHTTPClientTransport(
    new URL(baseUrl)
  );
  await client.connect(transport);
  console.log("Connected using Streamable HTTP transport");
} catch (error) {
  // If that fails with a 4xx error, try the older SSE transport
  console.log("Streamable HTTP connection failed, falling back to SSE transport");
  client = new Client({
    name: 'sse-client',
    version: '1.0.0'
  });
  const sseTransport = new SSEClientTransport(baseUrl);
  await client.connect(sseTransport);
  console.log("Connected using SSE transport");
}
```

## Defining a Code Review Prompt with MCP TypeScript
This snippet demonstrates how to define a reusable prompt named 'review-code' on an MCP server. It expects a 'code' string as input and constructs a user message for an LLM to review the provided code. This allows for templated interactions with language models.

```typescript
server.prompt(
  "review-code",
  { code: z.string() },
  ({ code }) => ({
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: `Please review this code:\n\n${code}`
      }
    }]
  })
);
```

## Running Simple Streamable HTTP Server with OAuth
This command starts the simple Streamable HTTP server with an added demonstration of OAuth authentication.

```bash
npx tsx src/examples/server/simpleStreamableHttp.ts --oauth
```

## Implementing Low-Level MCP Server with Custom Request Handlers
This example illustrates how to use the Server class directly for fine-grained control over MCP server behavior. It shows how to define custom request handlers for specific schemas like ListPromptsRequestSchema and GetPromptRequestSchema, providing a flexible way to manage server capabilities.

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "example-server",
    version: "1.0.0"
  },
  {
    capabilities: {
      prompts: {}
    }
  }
);

server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [{
      name: "example-prompt",
      description: "An example prompt template",
      arguments: [{
        name: "arg1",
        description: "Example argument",
        required: true
      }]
    }]
  };
});

server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  if (request.params.name !== "example-prompt") {
    throw new Error("Unknown prompt");
  }
  return {
    description: "Example prompt",
    messages: [{
      role: "user",
      content: {
        type: "text",
        text: "Example prompt text"
      }
    }]
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Running Streamable HTTP Client with OAuth
This command executes an example client that includes OAuth authentication, connecting to a Streamable HTTP server.

```bash
npx tsx src/examples/client/simpleOAuthClient.js
```

## Running Backwards Compatible Server with Streamable HTTP and SSE
This command starts a single MCP server instance supporting both Streamable HTTP and deprecated SSE transports, handling requests at `/mcp` (GET/POST/DELETE) and `/sse` (GET) with `/messages` (POST) respectively, tracking session types, and enabling notifications and tool execution across both transport types.

```bash
npx tsx src/examples/server/sseAndStreamableHttpCompatibleServer.ts
```

## Initializing an MCP Server Instance
This code initializes a new `McpServer` instance, which serves as the core interface for the Model Context Protocol. It requires a `name` and `version` to identify the server within the MCP ecosystem.

```typescript
const server = new McpServer({
  name: "My App",
  version: "1.0.0"
});
```

## Running Streamable HTTP Server with Server Notifications
This command starts a Streamable HTTP server demonstrating server-initiated notifications, including resource list change notifications with dynamically added resources and automatic resource creation on a timed interval.

```bash
npx tsx src/examples/server/standaloneSseWithGetStreamableHttp.ts
```

## Running JSON Response Mode Streamable HTTP Server
This command starts a Streamable HTTP server with JSON response mode enabled, returning responses directly in the body without SSE, and handling unsupported methods with appropriate HTTP status codes.

```bash
npx tsx src/examples/server/jsonResponseStreamableHttp.ts
```

## Running Deprecated SSE Transport Server
This command starts a server implementing the deprecated HTTP+SSE transport, primarily for backwards compatibility testing, featuring separate `/mcp` (SSE GET) and `/messages` (client POST) endpoints, and a `start-notification-stream` tool for periodic notifications.

```bash
npx tsx src/examples/server/simpleSseServer.ts
```

## Starting Example Server - npm
This command starts the local development server for the SDK's examples, allowing contributors to interact with the SDK's functionality in a live environment. It's typically run in a separate terminal.

```bash
npm run server
```

## Running Example Client - npm
This command executes the client-side application of the SDK's examples, typically connecting to the local server to demonstrate SDK usage. It's used to test the SDK's integration.

```bash
npm run client
```

## Executing Build and Test Commands for MCP TypeScript SDK
This snippet provides common shell commands for building, linting, and running tests within the MCP TypeScript SDK project. It includes commands for a full build, linting, running all tests, and executing specific test files or patterns using Jest.

```bash
npm run build        # Build ESM and CJS versions
npm run lint         # Run ESLint
npm test             # Run all tests
npx jest path/to/file.test.ts  # Run specific test file
npx jest -t "test name"        # Run tests matching pattern
```

## Installing Dependencies - npm
This command installs all necessary project dependencies listed in the 'package.json' file, preparing the TypeScript SDK for development and building. It should be run after cloning the repository.

```bash
npm install
```

## Installing MCP TypeScript SDK
This command installs the Model Context Protocol (MCP) TypeScript SDK using npm, making it available for use in your project.

```bash
npm install @modelcontextprotocol/sdk
```

## Cloning Repository - Git
This command clones your forked Model Context Protocol TypeScript SDK repository to your local machine, allowing you to begin development. Replace 'YOUR-USERNAME' with your actual GitHub username.

```bash
git clone https://github.com/YOUR-USERNAME/typescript-sdk.git
```