# frontend/Dockerfile
FROM node:16

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build application
RUN npm run build

# Install serve to serve the build
RUN npm install -g serve

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]