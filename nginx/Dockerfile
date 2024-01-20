# Используйте официальный образ Nginx
FROM nginx:latest

# Удалите стандартный конфигурационный файл Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Скопируйте ваш конфигурационный файл Nginx
COPY nginx.conf /etc/nginx/conf.d

COPY ./farpost-boost.ru /farpost-boost.ru