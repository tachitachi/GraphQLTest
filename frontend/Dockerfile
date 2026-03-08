FROM node:20-alpine

# Install bash AND glibc compatibility for the Cursor/VS Code agent
RUN apk add --no-cache bash libstdc++ gcompat

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]

