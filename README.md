## Personal Book Tracker – Full Stack GraphQL Demo

This repository is a small, end‑to‑end example of a **GraphQL** application using:

- **Backend**: Python, FastAPI, Strawberry GraphQL, SQLAlchemy Core, PostgreSQL
- **Frontend**: React + TypeScript, Apollo Client, Vite
- **Infra / Tooling**: Docker, Docker Compose, Poetry (Python deps), Node + npm, Dev Containers (optional)

It is designed as an onboarding example so you can understand the full flow and then adapt it to your own application.

---

### 1. Repository structure

- `docker-compose.yml` – Orchestrates database, backend API, and frontend.
- `.devcontainer/`
  - `.devcontainer/backend/devcontainer.json` – Dev Container targeting the **backend** service from `docker-compose.yml`, with Python tooling extensions.
  - `.devcontainer/frontend/devcontainer.json` – Dev Container targeting the **frontend** service from `docker-compose.yml`, with JS/TS tooling extensions.
- `backend/`
  - `main.py` – FastAPI entrypoint and Strawberry GraphQL router at `/graphql`.
  - `schema.py` – Strawberry GraphQL schema and resolvers (queries + mutations).
  - `models.py` – SQLAlchemy **Core** table definitions (`authors`, `books`).
  - `database.py` – Async PostgreSQL engine and session factory.
  - `pyproject.toml` – Poetry dependency configuration.
  - `Dockerfile` – Python 3.11 image running `uvicorn`.
- `frontend/`
  - `src/App.tsx` – React UI for listing books, showing author details, adding books.
  - `src/index.tsx` – React entrypoint.
  - `src/queries.ts` – GraphQL queries/mutations used by Apollo Client.
  - `vite.config.ts`, `tsconfig*.json` – Vite + TypeScript config.
  - `package.json` – Frontend dependencies and scripts.
  - `Dockerfile` – Node 20 image running Vite dev server.
- `database/init.sql` – PostgreSQL schema + seed data.

---

### 2. Stack overview

#### Backend stack

- **FastAPI**: Modern, async Python web framework. Handles HTTP, CORS, and dependency injection.
- **Strawberry GraphQL**: Schema‑first GraphQL library. We define:
  - `Query` type for `books`, `book`, `authors`, `author`.
  - `Mutation` type for `addBook`.
- **SQLAlchemy Core**: Uses table objects and explicit `select`/`insert` instead of ORM models. This is close to “raw SQL with safety”:
  - Joins `books` and `authors` for list/detail queries.
  - Inserts rows into `books` with Postgres `RETURNING`.
- **PostgreSQL**: Stores authors and books. `database/init.sql` creates tables and seed rows.
- **Poetry**: Manages Python dependencies via `pyproject.toml` instead of `requirements.txt`.

#### Frontend stack

- **React + TypeScript**: Component‑based UI with static typing.
- **Vite**: Fast dev server and bundler for modern React apps.
- **Apollo Client**: GraphQL client used to:
  - Fetch all books and their authors.
  - Send the `addBook` mutation when the form is submitted.

The UI lets you:

- See a **list of books**.
- Click a book to view its **author details**.
- Use a form to **add a new book** pointing to an existing author ID.

---

### 3. Running with Docker / Docker Compose

#### Prerequisites

- Docker
- Docker Compose (often bundled with Docker Desktop)

#### Start everything

From the repo root:

```bash
docker-compose up --build
```

Services:

- **db** – PostgreSQL with initial schema + data from `database/init.sql`.
- **backend** – FastAPI + Strawberry app on `http://localhost:8000`.
  - GraphQL endpoint: `http://localhost:8000/graphql`
  - Health check: `http://localhost:8000/health`
- **frontend** – Vite dev server on `http://localhost:5173`.

Once everything is up:

- Open `http://localhost:5173` to use the React app.
- The frontend talks to `http://localhost:8000/graphql` via Apollo Client.

#### Stopping

```bash
docker-compose down
```

This stops and removes containers. The data is ephemeral by default (reseeded on next `up`).

---

### 4. Running locally without Docker (optional)

You can also run backend and frontend directly on your machine.

#### Backend (FastAPI + Strawberry)

Requirements:

- Python 3.11
- Poetry
- Local PostgreSQL (with a database named `booksdb`, or adjust `DATABASE_URL`)

Steps:

```bash
cd backend
poetry install

# Ensure DATABASE_URL in environment if needed, e.g.:
# export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/booksdb"

poetry run uvicorn main:app --reload
```

Backend will be at `http://localhost:8000`.

#### Frontend (React + Vite)

Requirements:

- Node 18+ (Node 20 recommended)
- npm or another Node package manager

Steps:

```bash
cd frontend
npm install
npm run dev
```

Vite will start at `http://localhost:5173`.

Make sure the backend is reachable at `http://localhost:8000` (or update the `ApolloClient` URI in `src/App.tsx` if you change ports).

---

### 5. GraphQL API quick tour

At `http://localhost:8000/graphql` you can use a GraphQL IDE (Strawberry’s GraphiQL or another client).

Examples:

**Query all books:**

```graphql
query GetBooks {
  books {
    id
    title
    description
    author {
      id
      name
      bio
    }
  }
}
```

**Add a new book:**

```graphql
mutation AddBook {
  addBook(title: "My New Book", authorId: 1, description: "Demo") {
    id
    title
    author {
      id
      name
    }
  }
}
```

Use these examples as a template for building your own queries and mutations when adapting the app.

---

### 6. Dev Containers & Cursor usage

This repo already includes **Dev Container** definitions under `.devcontainer/` so you can develop directly “inside” the running Docker services using VS Code or Cursor.

#### Available Dev Containers

- **Backend Dev Container** – `.devcontainer/backend/devcontainer.json`
  - Uses `docker-compose.yml`, attaches to the `backend` service.
  - Mounts the repo at `/app`.
  - Adds Python‑oriented extensions (e.g. `ms-python.python`, `strawberry-graphql.vscode-strawberry`).
- **Frontend Dev Container** – `.devcontainer/frontend/devcontainer.json`
  - Uses `docker-compose.yml`, attaches to the `frontend` service.
  - Mounts the repo at `/app`.
  - Adds JS/TS‑oriented extensions (ESLint, Prettier, etc.).

#### How to use in Cursor / VS Code

1. Make sure Docker is running.
2. In **Cursor** (or VS Code), open this folder (`GraphQLTest`).
3. Use the command palette:
   - Select the **backend** Dev Container if you want to work on the API.
   - Select the **frontend** Dev Container if you want to work on the React app.
4. Once inside the container:
   - Use the integrated terminal for commands like `docker-compose up --build`, `poetry install`, or `npm install` as needed.
   - Use Cursor’s inline chat/agents to explore and refactor code, just as you would locally.

These Dev Containers give you a preconfigured environment tied to the running Docker services, so you do not need to manually install Python, Node, or Postgres on your host machine.

---

### 7. Adapting this template to your own app

To create your own GraphQL app based on this example:

1. **Change the domain:**
   - Update `database/init.sql` for your tables and seed data.
   - Update `backend/models.py` table definitions.
2. **Update GraphQL schema:**
   - Modify `backend/schema.py` types (`Author`, `Book`) and resolvers to match your entities.
3. **Update frontend UI:**
   - Adjust `src/queries.ts` for your new queries and mutations.
   - Update `src/App.tsx` to render your data instead of books/authors.
4. **Rebuild and run:**
   - `docker-compose up --build` or run backend/frontend locally.

By following these steps, you can quickly bootstrap a GraphQL + FastAPI + React application tailored to your use case while keeping the same overall architecture shown here.

