import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  ApolloClient,
  HttpLink,
  InMemoryCache,
} from "@apollo/client";
import {
  ApolloProvider,
  useQuery,
  useMutation
} from "@apollo/client/react";
import { GET_BOOKS, ADD_BOOK } from "./queries";

const client = new ApolloClient({
  link: new HttpLink({ uri: "http://localhost:8000/graphql" }),
  cache: new InMemoryCache(),
});

type Author = {
  id: number;
  name: string;
  bio?: string | null;
};

type Book = {
  id: number;
  title: string;
  description?: string | null;
  author: Author;
};

interface GetBooksData {
  books: Book[];
}

interface AddBookData {
  addBook: Book;
}

interface AddBookVariables {
  title: string;
  authorId: number;
  description?: string | null;
}

type WsServerMessage =
  | { type: "subscribed"; eventId: string }
  | { type: "unsubscribed"; eventId: string }
  | { type: "error"; error: string }
  | { eventId: string; data: unknown };

function BooksView() {
  const { data, loading, error } = useQuery<GetBooksData>(GET_BOOKS);
  const [addBook] = useMutation<AddBookData, AddBookVariables>(ADD_BOOK, {
    refetchQueries: [{ query: GET_BOOKS }],
  });

  const [selectedBookId, setSelectedBookId] = useState<number | null>(null);
  const [title, setTitle] = useState<string>("");
  const [authorId, setAuthorId] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (loading) return <p>Loading books...</p>;
  if (error) return <p>Error loading books: {error.message}</p>;

  const books = data?.books ?? [];
  const selectedBook = books.find((b) => b.id === selectedBookId);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!title || !authorId) return;
    try {
      setSubmitting(true);
      await addBook({
        variables: {
          title,
          authorId: Number(authorId),
          description: description || null,
        },
      });
      setTitle("");
      setAuthorId("");
      setDescription("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: "1rem" }}>Personal Book Tracker</h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1.5fr",
          gap: "2rem",
        }}
      >
        <div>
          <h2>Books</h2>
          <ul style={{ listStyle: "none", padding: 0 }}>
            {books.map((book) => (
              <li
                key={book.id}
                onClick={() => setSelectedBookId(book.id)}
                style={{
                  padding: "0.75rem 1rem",
                  marginBottom: "0.5rem",
                  borderRadius: 8,
                  border: "1px solid #e0e0e0",
                  cursor: "pointer",
                  backgroundColor:
                    selectedBookId === book.id ? "#f0f4ff" : "#fff",
                  transition:
                    "background-color 0.15s ease, box-shadow 0.15s ease",
                  boxShadow:
                    selectedBookId === book.id ? "0 0 0 1px #3b82f6" : "none",
                }}
              >
                <div style={{ fontWeight: 600 }}>{book.title}</div>
                <div style={{ fontSize: 14, color: "#555" }}>
                  by {book.author.name}
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div>
          {selectedBook ? (
            <div style={{ marginBottom: "2rem" }}>
              <h2>Author Details</h2>
              <div
                style={{
                  padding: "1rem",
                  borderRadius: 8,
                  border: "1px solid #e0e0e0",
                  backgroundColor: "#fafafa",
                }}
              >
                <h3 style={{ marginTop: 0 }}>{selectedBook.author.name}</h3>
                {selectedBook.author.bio && (
                  <p>{selectedBook.author.bio}</p>
                )}
                <p
                  style={{
                    marginTop: "0.75rem",
                    fontSize: 14,
                    color: "#555",
                  }}
                >
                  Currently viewing: <strong>{selectedBook.title}</strong>
                </p>
              </div>
            </div>
          ) : (
            <div style={{ marginBottom: "2rem" }}>
              <h2>Author Details</h2>
              <p style={{ color: "#666" }}>
                Select a book to see its author&apos;s details.
              </p>
            </div>
          )}

          <div>
            <h2>Add a New Book</h2>
            <form
              onSubmit={handleSubmit}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
                padding: "1rem",
                borderRadius: 8,
                border: "1px solid #e0e0e0",
                backgroundColor: "#fafafa",
              }}
            >
              <label>
                <div style={{ fontSize: 14, marginBottom: 4 }}>Title</div>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Book title"
                  style={{
                    width: "90%",
                    padding: "0.5rem 0.75rem",
                    borderRadius: 6,
                    border: "1px solid #d1d5db",
                  }}
                />
              </label>
              <label>
                <div style={{ fontSize: 14, marginBottom: 4 }}>Author ID</div>
                <input
                  type="number"
                  value={authorId}
                  onChange={(e) => setAuthorId(e.target.value)}
                  placeholder="Existing author ID (e.g. 1)"
                  style={{
                    width: "90%",
                    padding: "0.5rem 0.75rem",
                    borderRadius: 6,
                    border: "1px solid #d1d5db",
                  }}
                />
              </label>
              <label>
                <div style={{ fontSize: 14, marginBottom: 4 }}>
                  Description (optional)
                </div>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Short description of the book"
                  rows={3}
                  style={{
                    width: "90%",
                    padding: "0.5rem 0.75rem",
                    borderRadius: 6,
                    border: "1px solid #d1d5db",
                    resize: "vertical",
                  }}
                />
              </label>
              <button
                type="submit"
                disabled={submitting || !title || !authorId}
                style={{
                  marginTop: "0.5rem",
                  padding: "0.6rem 1rem",
                  borderRadius: 999,
                  border: "none",
                  backgroundColor:
                    submitting || !title || !authorId ? "#9ca3af" : "#3b82f6",
                  color: "#fff",
                  fontWeight: 600,
                  cursor:
                    submitting || !title || !authorId
                      ? "not-allowed"
                      : "pointer",
                }}
              >
                {submitting ? "Adding..." : "Add Book"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function SubscriptionsView() {
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<
    "connecting" | "open" | "closed" | "error"
  >("connecting");
  const [eventIdInput, setEventIdInput] = useState("");
  const [subscriptions, setSubscriptions] = useState<string[]>([]);
  const [latestByEvent, setLatestByEvent] = useState<Record<string, unknown>>(
    {}
  );
  const [lastError, setLastError] = useState<string | null>(null);

  const wsUrl = useMemo(() => {
    // Frontend runs in the browser; backend port mapping is localhost:8000
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://localhost:8000/ws/events`;
  }, []);

  useEffect(() => {
    setStatus("connecting");
    setLastError(null);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setStatus("open");
    ws.onclose = () => setStatus("closed");
    ws.onerror = () => setStatus("error");
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data) as WsServerMessage;
        if ("type" in msg && msg.type === "error") {
          setLastError(msg.error);
          return;
        }
        if ("eventId" in msg && "data" in msg) {
          setLatestByEvent((prev) => ({ ...prev, [msg.eventId]: msg.data }));
        }
      } catch {
        // ignore non-json
      }
    };

    return () => {
      try {
        ws.close();
      } catch {
        // ignore
      }
      wsRef.current = null;
    };
  }, [wsUrl]);

  const send = (payload: unknown) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify(payload));
  };

  const subscribe = (eventId: string) => {
    const trimmed = eventId.trim();
    if (!trimmed) return;
    setSubscriptions((prev) =>
      prev.includes(trimmed) ? prev : [...prev, trimmed]
    );
    send({ action: "subscribe", eventId: trimmed });
  };

  const unsubscribe = (eventId: string) => {
    setSubscriptions((prev) => prev.filter((x) => x !== eventId));
    setLatestByEvent((prev) => {
      const next = { ...prev };
      delete next[eventId];
      return next;
    });
    send({ action: "unsubscribe", eventId });
  };

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: "0.5rem" }}>Event Subscriptions</h1>
      <div style={{ color: "#555", marginBottom: "1.25rem" }}>
        WebSocket status:{" "}
        <strong
          style={{
            color:
              status === "open"
                ? "#059669"
                : status === "connecting"
                  ? "#2563eb"
                  : "#dc2626",
          }}
        >
          {status}
        </strong>
        {lastError ? (
          <span style={{ marginLeft: 12, color: "#dc2626" }}>
            Server error: {lastError}
          </span>
        ) : null}
      </div>

      <div
        style={{
          display: "flex",
          gap: "0.75rem",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <input
          value={eventIdInput}
          onChange={(e) => setEventIdInput(e.target.value)}
          placeholder="Event ID (e.g. 1)"
          style={{
            flex: 1,
            padding: "0.6rem 0.75rem",
            borderRadius: 8,
            border: "1px solid #d1d5db",
          }}
        />
        <button
          onClick={() => {
            subscribe(eventIdInput);
            setEventIdInput("");
          }}
          disabled={status !== "open" || !eventIdInput.trim()}
          style={{
            padding: "0.6rem 1rem",
            borderRadius: 999,
            border: "none",
            backgroundColor:
              status !== "open" || !eventIdInput.trim() ? "#9ca3af" : "#3b82f6",
            color: "#fff",
            fontWeight: 600,
            cursor:
              status !== "open" || !eventIdInput.trim()
                ? "not-allowed"
                : "pointer",
          }}
        >
          Create subscription
        </button>
      </div>

      <div
        style={{
          padding: "1rem",
          borderRadius: 10,
          border: "1px solid #e5e7eb",
          backgroundColor: "#fafafa",
        }}
      >
        <h2 style={{ marginTop: 0 }}>Active subscriptions</h2>
        {subscriptions.length === 0 ? (
          <p style={{ color: "#666" }}>
            No active subscriptions. Add one above.
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {subscriptions.map((eventId) => (
              <div
                key={eventId}
                style={{
                  display: "grid",
                  gridTemplateColumns: "180px 1fr 140px",
                  gap: 12,
                  alignItems: "start",
                  padding: "0.75rem",
                  borderRadius: 10,
                  border: "1px solid #e5e7eb",
                  backgroundColor: "#fff",
                }}
              >
                <div>
                  <div style={{ fontWeight: 700 }}>Event {eventId}</div>
                  <div style={{ fontSize: 12, color: "#6b7280" }}>
                    Channel: event:{eventId}
                  </div>
                </div>
                <pre
                  style={{
                    margin: 0,
                    padding: "0.6rem",
                    borderRadius: 8,
                    backgroundColor: "#0b1220",
                    color: "#e5e7eb",
                    overflowX: "auto",
                    minHeight: 48,
                  }}
                >
                  {latestByEvent[eventId] === undefined
                    ? "(waiting for data...)"
                    : JSON.stringify(latestByEvent[eventId], null, 2)}
                </pre>
                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <button
                    onClick={() => unsubscribe(eventId)}
                    style={{
                      padding: "0.5rem 0.9rem",
                      borderRadius: 999,
                      border: "1px solid #ef4444",
                      backgroundColor: "#fff",
                      color: "#ef4444",
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    Unsubscribe
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  const [page, setPage] = useState<"books" | "subscriptions">("subscriptions");

  return (
    <ApolloProvider client={client}>
      <div
        style={{
          position: "sticky",
          top: 0,
          background: "white",
          borderBottom: "1px solid #e5e7eb",
          padding: "0.75rem 0",
          zIndex: 10,
        }}
      >
        <div
          style={{
            maxWidth: 900,
            margin: "0 auto",
            padding: "0 2rem",
            display: "flex",
            gap: 8,
          }}
        >
          <button
            onClick={() => setPage("books")}
            style={{
              padding: "0.5rem 0.9rem",
              borderRadius: 999,
              border: "1px solid #d1d5db",
              backgroundColor: page === "books" ? "#111827" : "#fff",
              color: page === "books" ? "#fff" : "#111827",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Books
          </button>
          <button
            onClick={() => setPage("subscriptions")}
            style={{
              padding: "0.5rem 0.9rem",
              borderRadius: 999,
              border: "1px solid #d1d5db",
              backgroundColor: page === "subscriptions" ? "#111827" : "#fff",
              color: page === "subscriptions" ? "#fff" : "#111827",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Subscriptions
          </button>
        </div>
      </div>

      {page === "books" ? <BooksView /> : <SubscriptionsView />}
    </ApolloProvider>
  );
}

export default App;

