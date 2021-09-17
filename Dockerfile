# Берем нужный базовый образ
FROM python:3.8-alpine
# Копируем все файлы из текущей директории в /app контейнера
COPY ./ /app
# Устанавливаем все зависимости
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
# Говорим контейнеру какой порт слушай
EXPOSE 80
# Монтируем папку /db для совместного использования с контейнером
VOLUME /db
# В качестве альтернативы distutils можно просто указать что выполнить
CMD python /app/main.py