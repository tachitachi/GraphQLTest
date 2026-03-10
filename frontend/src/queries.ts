import { gql } from "@apollo/client";

export const GET_BOOKS = gql`
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
`;

export const ADD_BOOK = gql`
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
`;

