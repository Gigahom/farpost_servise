#!/bin/bash

# Получение или обновление сертификатов
certbot certonly --nginx -d farpost-boost.ru --non-interactive --agree-tos -m 89246763535@mail.ru --keep

# Перезапуск Nginx с новыми сертификатами
nginx -g 'daemon off;'
