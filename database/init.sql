CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    bio TEXT
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    author_id INTEGER NOT NULL REFERENCES authors (id) ON DELETE CASCADE
);

INSERT INTO authors (name, bio) VALUES
    ('J.K. Rowling', 'British author best known for the Harry Potter series.'),
    ('J.R.R. Tolkien', 'English writer and academic, author of The Lord of the Rings.'),
    ('George Orwell', 'English novelist and critic, author of 1984 and Animal Farm.')
ON CONFLICT DO NOTHING;

INSERT INTO books (title, description, author_id) VALUES
    ('Harry Potter and the Sorcerer''s Stone', 'First book in the Harry Potter series.', 1),
    ('The Fellowship of the Ring', 'First of three volumes of The Lord of the Rings.', 2),
    ('1984', 'Dystopian novel about a totalitarian surveillance state.', 3)
ON CONFLICT DO NOTHING;

