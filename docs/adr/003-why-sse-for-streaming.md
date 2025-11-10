# ADR 003: Why Server-Sent Events (SSE) were Chosen for Streaming

## Status

Accepted

## Context

The application requires a real-time, unidirectional communication channel from the server to the client to stream chat responses and agent actions. The key requirement is to push updates from the backend to the frontend as they become available.

The two primary technologies considered for this were:
1.  **WebSockets:** A protocol providing full-duplex (two-way) communication.
2.  **Server-Sent Events (SSE):** A standard that allows a server to push data to a client over a single, long-lived HTTP connection.

## Decision

We decided to use **Server-Sent Events (SSE)** for streaming data from the backend to the frontend.

FastAPI provides excellent support for SSE via `StreamingResponse`, which integrates naturally with asynchronous generator functions. On the frontend, the `EventSource` API provides a standardized, browser-native way to consume SSE streams.

## Consequences

### Positive:
- **Simplicity:** SSE is simpler to implement on both the backend and frontend than WebSockets. It operates over a standard HTTP connection, avoiding the need for a separate protocol and the complexities of connection upgrades.
- **Lightweight:** For unidirectional data flow (server to client), SSE is a more lightweight solution. It does not have the overhead of the two-way communication features of WebSockets.
- **Automatic Reconnection:** The browser's `EventSource` API automatically handles reconnection if the connection is dropped, a feature that must be manually implemented when using WebSockets.
- **Firewall and Proxy Compatibility:** Since SSE is based on plain HTTP, it is generally more compatible with existing network infrastructure (firewalls, proxies) than WebSockets.

### Negative:
- **Unidirectional:** The primary limitation of SSE is that it is for server-to-client communication only. If the application ever required real-time, client-to-server communication (beyond standard HTTP requests), SSE would be insufficient, and we would need to add or switch to WebSockets. For this project's requirements, this is not a current limitation.
- **Connection Limit:** Browsers limit the number of concurrent SSE connections per domain (typically around 6), which could be a concern for applications that require many simultaneous streams. This is not an issue for our single-user, local-first application.
