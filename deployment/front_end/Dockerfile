FROM node:20-alpine AS builder
WORKDIR /front_end

COPY front_end/package.json ./
COPY front_end/package-lock.json ./
RUN npm ci

COPY front_end/ .
RUN npm run build

FROM nginx:stable-alpine
COPY --from=builder /front_end/dist /usr/share/nginx/html

COPY deployment/front_end/nginx.conf /etc/nginx/conf.d/default.conf
RUN chmod 644 /etc/nginx/conf.d/default.conf

EXPOSE 80