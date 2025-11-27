# Multi-stage Dockerfile for Next.js 15 frontend

# Development stage
FROM node:20-alpine AS development

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# Dependencies stage
FROM node:20-alpine AS deps

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json* ./

# Install production dependencies only
RUN npm ci --omit=dev

# Builder stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json* ./

# Install all dependencies (including dev)
RUN npm ci

# Copy source code
COPY . .

# Create public directory if it doesn't exist
RUN mkdir -p public

# Build Next.js app
RUN npm run build

# Production runtime stage
FROM node:20-alpine AS production

WORKDIR /app

# Copy necessary files from deps and builder (use existing node user)
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/package.json ./
COPY --from=builder --chown=node:node /app/next.config.ts ./

USER node

EXPOSE 3000

ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "start"]
