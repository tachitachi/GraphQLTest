import React, { useState } from "react";
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

function App() {
  return (
    <ApolloProvider client={client}>
      <BooksView />
    </ApolloProvider>
  );
}

export default App;

