# Frontend Dockerfile
FROM node:20-alpine as build
WORKDIR /app

# 传入 API 基地址（用于构建时注入）
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
