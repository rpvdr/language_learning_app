# 1. Build stage
FROM node:20-bullseye AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

# ВАЖНО! Копируем .env (или .env.production)
COPY .env .env

# Теперь остальной код
COPY . .

# Генерируем хуки
RUN npm run generate-client

# Делаем build
RUN npm run build

# 2. Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]