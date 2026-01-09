# GraphQL Integration Challenge - Task Management with Weather

## Challenge Overview

Build a GraphQL API server that integrates with your existing FastAPI REST service (Session 11 homework). Both servers will run simultaneously on different ports, with GraphQL acting as a gateway that communicates with the FastAPI backend.

## Setup

- **FastAPI REST Server**: Run on `http://localhost:8000`
- **GraphQL Server**: Run on `http://localhost:8001`

```bash
fastapi dev main.py --port=8001
```

## Requirements

### 1. GraphQL Schema

Define types for:
```graphql
type User {
  id: ID!
  name: String!
  tasks: [TaskListItem!]!
}

type TaskListItem {
  id: ID!
  title: String!
  content: String!
  city: String!
  userId: ID!
}

type Task {
  id: ID!
  title: String!
  content: String!
  city: String!
  userId: ID!
  user: User!
  weather: Weather!
}

type Weather {
  temperature: Float!
  windspeed: Float!
  weathercode: Int!
  time: String!
}
```

**Important:** `TaskListItem` does NOT include weather. Only the single `Task` query returns weather data.

### 2. Queries to Implement

```graphql
type Query {
  # Get all users
  users: [User!]!
  
  # Get single user with their tasks (no weather)
  user(id: ID!): User
  
  # Get all tasks with optional filters (no weather)
  tasks(userId: ID, city: String): [TaskListItem!]!
  
  # Get single task WITH weather forecast
  task(id: ID!): Task
}
```

### 3. Mutations to Implement

```graphql
type Mutation {
  # User operations
  createUser(name: String!): User!
  deleteUser(id: ID!): User!
  
  # Task operations
  createTask(title: String!, content: String!, city: String!, userId: ID!): Task!
  updateTask(id: ID!, title: String, content: String, city: String): Task!
  deleteTask(id: ID!): Task!
}
```

**Note:** Mutations return `Task` type (with weather) for single task operations.

### 4. Integration Requirements

Your GraphQL resolvers should:
- Make HTTP requests to FastAPI endpoints using `httpx`
- Handle async/await for all external API calls
- Map REST responses to GraphQL types
- Pass through query parameters for filtering
- **Only fetch weather when querying a single task**


### 5. Solve the N+1 Problem

When fetching `users` with their `tasks`, implement DataLoader or batch requests to avoid N+1 queries to the FastAPI server.

**Example scenario:**
```graphql
query {
  users {
    name
    tasks {
      title
      city
    }
  }
}
```

If you have 10 users, this should make **2 requests** (1 for users, 1 batched for all tasks), not 11 requests.