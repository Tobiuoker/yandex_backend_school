# Задание для школы бэкэнд-разработки Yandex

 * [Описание задания](#description)
 * [Реализованные обработчики](#handlers)
 * [Запуск приложения](#app-start)
 * [Запуск тестов](#tests)

## <a name="description"></a> Описание задания
В данном задании вам предлагается реализовать бэкенд для веб-сервиса сравнения цен, аналогичный сервису [Яндекс Товары](https://yandex.ru/products). Обычно взаимодействие с такими сервисами происходит следующим образом:
1. Представители магазинов загружают информацию о своих товарах и категориях. Также можно изменять и удалять информацию о ранее загруженных товарах и категориях.
2. Покупатели, пользуясь веб-приложением, могут искать предложения разных магазинов, сравнивать цены и следить за их динамикой и историей.

Задача - разработать REST API сервис, который позволяет магазинам загружать и обновлять информацию о товарах, а пользователям - смотреть какие товары были обновлены за последние сутки, а также следить за динамикой цен товара или категории за указанный интервал времени.

## <a name="handlers"></a> Реализованные обработчики
1. /imports
Импортирует новые товары и/или категории. Товары/категории импортированные повторно обновляют текущие. Изменение типа элемента с товара на категорию или с категории на товар не допускается. Порядок элементов в запросе является произвольным.

  - uuid товара или категории является уникальным среди товаров и категорий
  - родителем товара или категории может быть только категория
  - принадлежность к категории определяется полем parentId
  - товар или категория могут не иметь родителя
  - название элемента не может быть null
  - у категорий поле price должно содержать null
  - при обновлении товара/категории обновленными считаются **все** их параметры
  - при обновлении параметров элемента обязательно обновляется поле **date** в соответствии с временем обновления
  - в одном запросе не может быть двух элементов с одинаковым id

Гарантируется, что во входных данных нет циклических зависимостей и поле updateDate монотонно возрастает

2. /delete/{id}
Удаляет элемент по идентификатору. При удалении категории удаляются все дочерние элементы.

3. /nodes/{id}
Получить информацию об элементе по идентификатору. При получении информации о категории также предоставляется информация о её дочерних элементах.

- цена категории - это средняя цена всех её товаров, включая товары дочерних категорий. Если категория не содержит товаров цена равна null.

4. /sales
Получение списка **товаров**, цена которых была обновлена за последние 24 часа от времени переданном в запросе.

5. /node/{id}/statistic
Получение статистики (истории обновлений) по цене товара/категории за заданный интервал. Статистика по удаленным элементам недоступна.

- цена категории - это средняя цена всех её товаров, включая товары дочерних категорий.Если категория не содержит товаров цена равна null.
- можно получить статистику за всё время.

6. /swagger
Swagger документация

## <a name="app-start"></a> Запуск приложения

Находясь в папке с файлом `docker-compose.yml` выполнить в терминале:

  docker-compose build
  docker-compose up

## <a name="tests"></a> Запуск тестов
Выполнить команды:
source env/bin/activate
pip install pytest
python -m pytest
