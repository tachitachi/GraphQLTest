import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://backend:8000';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

function graphqlRequest(query, variables = {}) {
  return http.post(
    `${BASE_URL}/graphql`,
    JSON.stringify({ query, variables }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
}

export default function () {
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, { 'health status 200': (r) => r.status === 200 });

  const booksRes = graphqlRequest(`
    query {
      books {
        id
        title
        description
        author { id name bio }
      }
    }
  `);
  check(booksRes, { 'books status 200': (r) => r.status === 200 });

  const authorsRes = graphqlRequest(`
    query {
      authors {
        id
        name
        bio
      }
    }
  `);
  check(authorsRes, { 'authors status 200': (r) => r.status === 200 });

  const bookRes = graphqlRequest(
    `
    query GetBook($id: Int!) {
      book(id: $id) {
        id
        title
        description
        author { id name bio }
      }
    }
  `,
    { id: 1 }
  );
  check(bookRes, { 'book by id status 200': (r) => r.status === 200 });

  const authorRes = graphqlRequest(
    `
    query GetAuthor($id: Int!) {
      author(id: $id) {
        id
        name
        bio
      }
    }
  `,
    { id: 1 }
  );
  check(authorRes, { 'author by id status 200': (r) => r.status === 200 });

  sleep(0.5);

  const addBookRes = graphqlRequest(
    `
    mutation AddBook($title: String!, $authorId: Int!, $description: String) {
      books {
        addBook(title: $title, authorId: $authorId, description: $description) {
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
    }
    `,
    {
      title: `test ${Math.floor(Math.random() * 1000)}`,
      authorId: Math.floor(Math.random() * 3) + 1,
      description: `test description ${Math.floor(Math.random() * 1000)}`
    }
  );
  check(addBookRes, { 'addBook status 200': (r) => r.status === 200 });
  
  sleep(0.5);
}
