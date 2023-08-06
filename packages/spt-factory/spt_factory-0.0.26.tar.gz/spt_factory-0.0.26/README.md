
## Либка для получения доступа к ресурсам spt

Один раз инициализируете фабрику и потом с помощью методов `get_<recource_name>`(получить креды `get_<recource_name>_credentials`) получаете наобходимый доступ без прописывания всех логинов, явок, паролей

Реализованные ресурсы на текущий момент:

- Доступы к базам
- S3Manager по умолчанию подключается к aws s3 storage. 
- DataVault
- ModelManager
- ModelStorage
- Grafana Loki
- TelegramAlert
- PrometheusPushgateway

## Пример использования

Необходимо установить сертификат:

```bash
sudo mkdir -p /usr/local/share/ca-certificates/Yandex && \
sudo wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt
```

Так же необходимо указать две переменные окружения: 

 - MONGO_URL=<url>
 - SSLROOT=/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt


```python
import os
from spt_factory import MongoFactory as SPTFactory

f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)

print(f.get_postgres_credentials())

with f.get_postgres(dbname='moniback') as conn:
    print("Happy coding")
```

## Работа с локальными ресурсами

При вызове получения ресурса вы можете переписать значения из монги своими значениями:

```python
import os
from spt_factory import MongoFactory as SPTFactory

f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)

params = {
    'host': 'localhost',
    'port': '5432',
    ...
} if os.getenv('ENV') == 'LOCAL' else {} 

print(f.get_postgres_credentials(**params))

with f.get_postgres(dbname='moniback') as conn:
    print("Happy coding")
```


## DS часть

Фабрика позволяет получить доступ к `ModelManager` & `PipelineManager`, которые являются singleton'ами

```python
...
# Вернет один и тот же объект
model_manager_1 = f.get_model_manager()
model_manager_2 = f.get_model_manager()

# Вернет один и тот же объект
pipeline_manager_1 = f.get_pipeline_manager()
pipeline_manager_2 = f.get_pipeline_manager()
```


## Работа с хранилищем S3

Также можно получить доступ к хранилищу S3 посредством фабрики и загружать или выгружать файлы с хранилища.

Метод `upload_file` позволяет загрузить в хранилище любой readable object. 

В тоже время `upload_binstr` позволяет загрузить в хранилище только бинарный файл.

Метод `download_file` загружает файл на ваше устройство.

`download_bin` загружает бинарный файл на ваше устройство.

`delete_object` удаляет файл или бинарный файл из бакета

```python
import os
from spt_factory.factory import MongoFactory as SPTFactory


s = b'example string'
f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)
manager = f.get_s3_manager()
manager.upload_bin(bucket_name='theme-models', id='1', bin_str=s)
manager.upload_file(bucket_name='theme-models', id='2', filepath='test.py', author='Walle')
manager.download_file(bucket_name='theme-models', id='1', filepath='../downloaded_file.txt')
data = manager.download_bin('theme-models', '91')
print(data)   # b'exapmle string'
manager.delete_object('theme-models', '1')
manager.delete_object('theme-models', '2')
```


# DataVault

Для работы с Data Vault реализован класс `DataVault`, обладающий классами `hub, sattelite, link`, предназначенными для 
упрощения работы с Data Vault и устранением SQL кода из проектов.

В качестве аргументов данных методов являются `data_df` - датафрейм, который нужно загрузить, 
в нем предварительно нужно указать названия колонок, `config` - конфиг файл, для более определения, 
что хешировать, какие колонки являются натуральным ключом, и где первичный ключ (шаблоны будут описаны ниже),
`conn` - сам клиент, уже подключенный к базе.

Перед началом загрузки нужно подготовить `config`

Рассмотрим пример загрузки данных в hub:

```python
from spt_factory.utils.data_vault import DataVault
from spt_factory.factory import MongoFactory
import pandas as pd
import os


config_hub = {
    'schema': 'test', # целевая схема, по умолчанию business_vault
    'table': 'h_position', # целевая таблица
    'src_pk': 'position_pk', # название первичного ключа, указанного в таблице
    'src_nk': 'position', # натуральный ключ, от которого берется хэш
    'record_source': 'test', # откуда берутся данные
}
# Датафрейм, который мы хотим загрузить
df_hub = pd.DataFrame(
    {
        'position': ['Engineer', 'Devops', 'Chill']
    },
    columns=['position']
)

# Получаем подключение к базе
spt = MongoFactory(
        mongo_url=os.getenv('MONGO_URL'),
        tlsCAFile=os.getenv('SSLROOT'),
    )

with spt.get_greenplum() as conn:
    DataVault.hub(df_hub, config_hub, conn)
```

В случае с `sattelite`  есть 2 вариации загрузки:
1) Загрузка записи с уже известным первичным ключом. В этом случае получаем только hashdiff от нужных колонок, 
в частности от payload

```python
config_sat = {
    'table': 'hs_user',
    'src_pk': 'user_pk', # указываем какая колонка является первичным ключом в датафрейме
    'src_hashdiff': 'user_hashdiff', # имя колонки, в которой хранится hashdiff в целевой таблице
    'hashdiff_cols': ['bio'], # от каких колонок нужно получить хэш
    'src_payload': ['bio', 'u_age'], # какие свойства сущности нужно загрузить в satellite
    'record_source': 'test',
    'schema': 'test',
}
df_sat_pk = pd.DataFrame(
    {
        'user_pk': ['4j6n5j6n54j543', 'j46nj45k435', '4kj6n5jk6n45j'],  # ключ существующей записи в hub
        'bio': ['Just nice job', 'Sunshine', 'I wanna sleep'],
        'u_age': [10, 123, 124]
    }
)
with spt.get_greenplum() as conn:
    DataVault.sat(df_hub, config_hub, conn)
```

2) Загрузка записи еще, в которой еще нет хэшей, но нужно получить его по натуральному ключу

```python
config_sat_nk = {
    'table': 'hs_user',
    'src_nk': 'user', # название колонки, в которой лежит натуральный ключ
    'record_source': 'test',
    'schema': 'test',
    'src_hashdiff': 'user_hashdiff',
    'hashdiff_cols': ['bio'],
    'src_payload': ['bio', 'u_age'],
}

df_sat_nk = pd.DataFrame(
    {
        'user_pk': ['Mark', 'Walle', 'Alex'], # натуральный ключ, от которого нужно получить хэш
        'bio': ['Just nice job', 'Sunshine', 'I wanna sleep'],
        'u_age': [10, 123, 124]
    }
)
with spt.get_greenplum() as conn:
    DataVault.sat(df_hub, config_hub, conn)
```

Пример конфига и датафрейма `link`

```python
config_link = {
    'table': 'l_user_position',
    'schema': 'test',
    'src_pk': 'link_message_source_pk', # название колонки, содержащий первичный ключ самой линки
    'src_fk': ['user_pk', 'position_pk'], # сущности между которыми нужно получить линку
    'record_source': 'test',
}
df_link = pd.DataFrame(
    {
        'user_pk': ['35fd4jn3k43m5', '32j5njk5n42j3', '23jk5n3kj5n23'],
        'position_pk': ['45j4h45j33k', 'ekk5n4j5n3k335', '3k53kn3j5n353']
    }
)
with spt.get_greenplum() as conn:
    DataVault.link(df_hub, config_hub, conn)
```


## Prometheus PushGateway

Получить ресурс. 

Определить тип имя, метрики и можно пушить в pushgateway
```
prom = context.resources.prometheus
gauge = Gauge(name=m_name, documentation='test metrics', registry=prom.registry)
prom.push_to_gateway('job1_metrics')
```


## Telegram alert

Отправка сообщения в канал
```
alert = context.resources.alert_sender
alert.send_message("Sending message")
```

## Grafana Loki

Конфигурация ресурса.
```
grafana_loki = GrafanaLoki(
    url = url,
    tags = {"job": "job_name"}
)
```

Добавление обработчика логов в loki
```
loki = context.resources.grafana_loki
loki_handler = loki.get_handler()
logger = get_dagster_logger().addHandler(loki_handler)
logger.info(msg="Sending message", extra={"tags": {"service": "my-service"}})
```

Или получить логгер с обработчиком
```
loki = context.resources.grafana_loki
logger = loki.get_logger()
logger.info(msg="Sending message", extra={"tags": {"service": "my-service"}})
```
