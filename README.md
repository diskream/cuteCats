# cuteCats
## Что сделано:
- Добавление, чтение, редактирование и удаление записей;
- Пагинация по 5 записей;
- Полнотекстовый поиск по породе, имени, описанию и возрасту;
- Сортировка записей как в поиске, так и при просмотре записей;
- На хостовой машине запускается в контейнере через docker compose up.

## Какие возникли проблемы:
Не удалось сделать нормальный dump БД в контейнер. На хосте работает безукоризненно, на других машинах ругается. 
Пробовал делать несколько дампов разными способами: через команды docker, через docker-compose.yaml, через СУБД.
В репозитории лежат дампы с расширением .sql на всякий случай:
- pg_dump_backup.sql через docker docker exec <container> pg_dump ... ;
- pg_dumpall_backup.sql через docker docker exec <container> pg_dumpall ... ;
- postgres_data_backup.sql полный бекап через pgAdmin4.

## Скриншоты проекта:
### Главная страница:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img1.png)
### Страница с котами:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img2.png)
### Пример полнотекстового поиска:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img3.png)
### Сортировка по породе по возрастанию:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img4.png)
### Сортировка по возрасту по убыванию:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img5.png)
### Страница кота:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img6.png)
### Добавление кота:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img7.png)
### Обновление информации о коте:
  ![](https://github.com/diskream/cuteCats/blob/master/img/img8.png)
  
