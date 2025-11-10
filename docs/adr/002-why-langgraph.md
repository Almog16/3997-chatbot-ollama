# ADR 002: Why LangGraph was Chosen for Agent Orchestration

## Status

Accepted

## Context

The project required a robust framework to build a stateful, multi-step agent that can use tools to answer questions. The initial "Simple Mode" directly queries the LLM, but "Agent Mode" needs to support more complex workflows, including:
- Deciding whether to use a tool or not.
- Calling a tool with the correct arguments.
- Processing the tool's output.
- Continuing the reasoning process until a final answer is reached.
- Streaming the intermediate steps (tool calls, results) to the frontend for transparency.

We considered using custom-built loops, the standard LangChain Agent Executor, and LangGraph.

## Decision

We decided to use **LangGraph** to build the agent. LangGraph is a library built on top of LangChain specifically designed for creating cyclical, stateful agent runtimes.

We defined a graph where each node represents a step in the reasoning process (e.g., "call agent," "execute tool") and the edges represent the conditional logic that determines the next step.

## Consequences

### Positive:
- **Explicit State Management:** LangGraph forces the explicit definition of a `State` object that is passed between nodes. This makes the agent's memory and the flow of information clear and easy to debug.
- **Cyclical and Controllable:** Unlike linear chains, LangGraph excels at building cyclical graphs where the agent can loop through the "think -> act" cycle multiple times. This is essential for complex problem-solving. We can also add explicit controls, like a maximum number of iterations, to prevent infinite loops.
- **Streaming and Transparency:** LangGraph's `astream` method provides a detailed, real-time stream of the events happening inside the graph, including which node is running and what its output is. This was crucial for implementing the tool usage indicators on the frontend.
- **Modularity:** Each step in the agent's reasoning process is a separate node (a Python function). This makes the agent easy to extend, modify, and test. Adding a new tool or changing the agent's logic can be done by modifying a specific node or edge without rewriting the entire loop.

### Negative:
- **Higher Initial Complexity:** The concepts of graphs, nodes, and edges introduce a higher level of abstraction compared to a simple `while` loop. The initial setup and learning curve are steeper.
- **Verbose for Simple Cases:** For a very simple agent that only ever calls one tool, LangGraph can feel overly verbose. However, it provides a solid foundation that can scale to more complex behaviors without a complete rewrite.
