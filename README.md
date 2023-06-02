# Тестовое задание 2 (загрузка, конвертация и скачивание аудиозаписей)

### Порядок запуска и использования:
1. Клонируйте репозиторий:
```
git clone https://github.com/kizernis/task2
```
2. Перейдите в директорию проекта:
```bash
cd task2
```
3. По желанию измените пароли пользователя и суперпользователя СУБД в файлах, соответственно, ```db_password.txt``` и ```db_root_password.txt``` (в конце файла ```db_password.txt``` не должно быть переноса строки).

4. По желанию в начале файла ```docker-compose.yml``` измените значения переменных **DB_USER_NAME** и **DB_DATABASE_NAME** и в конце раскомментируйте сервис **adminer** (для управления базой данных PostgreSQL через GUI).

5. Убедитесь, что TCP-порт **8000** на вашем компьютере не занят.

6. Запустите приложение (у вас должен поддерживаться **[Compose V2](https://docs.docker.com/compose/migrate/)**):
```
docker compose up
```
или в режиме detached:
```
docker compose up -d
```
7. Для проверки работы веб-сервиса перейдите по адресу **[http://localhost:8000/docs](http://localhost:8000/docs)** или воспользуйтесь приложением, умеющим отправлять POST и GET-запросы, типа **Postman** или **curl**, например так:
```bash
curl -X 'POST' 'http://localhost:8000/create-user/' \
-H 'accept: application/json' -H 'Content-Type: application/json' \
-d '{"name": "Иван"}'
```
потом так:
```bash
curl -X 'POST' 'http://localhost:8000/add-audio/' \
-H 'accept: application/json' -H 'Content-Type: multipart/form-data' \
-F 'user_id=1' \
-F 'token=2ba1294c-b8d0-4c54-a793-150ae5b2f0fd' \
-F 'audio_file=@boing.wav;type=audio/wav'
```
и так:
```bash
curl -X 'GET' 'http://localhost:8000/record?id=783c35fc-52c8-4a62-b5ce-ed1b81217672&user=1' \
-H 'accept: application/json'
```

8. Для доступа к базе данных откройте **Adminer** (если раскомментировали) по адресу **[http://localhost:8080](http://localhost:8080)** (адрес сервера PostgreSQL оставьте **db**) или наберите в терминале:
```
docker exec -it task2-db-1 sh
```
и воспользуйтесь командой **psql**, например так:
```
psql -U user1 task2
```

9. Для завершения работы приложения и удаления контейнеров и томов наберите команду:
```
docker compose down -v
```