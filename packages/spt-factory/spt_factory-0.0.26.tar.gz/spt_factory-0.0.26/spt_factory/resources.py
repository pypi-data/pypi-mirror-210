from abc import ABC, abstractmethod
from psycopg2 import connect
from pymongo import MongoClient
from boto3 import client
from clickhouse_driver import Client as click_client


from spt_factory.utils.alert_sender import AlertSender
from spt_factory.utils.grafana_loki import GrafanaLoki
from spt_factory.utils.prometheus import PrometheusResource
from spt_factory.credentials import Credentials
from spt_factory.utils.s3_manager import S3Manager


class Resource(ABC):

    def __init__(self, c: Credentials):
        self.c = c

    @abstractmethod
    def get_object(self):
        pass

    @staticmethod
    @abstractmethod
    def get_name():
        pass


class Postgres(Resource):

    def get_object(self):
        return connect(**self.c.get_credentials())

    @staticmethod
    def get_name():
        return 'postgres'


class Greenplum(Resource):

    def get_object(self):
        return connect(**self.c.get_credentials())

    @staticmethod
    def get_name():
        return 'greenplum'


class Mongo(Resource):

    def get_object(self):
        return MongoClient(**self.c.get_credentials())

    @staticmethod
    def get_name():
        return 'mongo'


class Any:
    __slots__ = "creds"

    def __init__(self, creds):
        self.creds = creds

    def get_creds(self):
        return self.creds


class AnyCreds(Resource):

    def get_object(self):
        return Any(self.c.get_credentials())

    @staticmethod
    def get_name():
        return 'any_creds'


class S3ManagerResource(Resource):

    def get_object(self):
        return S3Manager(client(**self.c.get_credentials()))

    @staticmethod
    def get_name():
        return 's3_manager'


class PrometheusPushgatewayResource(Resource):
    def get_object(self):
        crede = self.c.get_credentials()
        gateway = crede.get('pushgateway_url')

        return PrometheusResource(gateway)

    @staticmethod
    def get_name():
        return 'prometheus_pushgateway'


class TelegramAlertsResource(Resource):
    def get_object(self):
        crede = self.c.get_credentials()

        alert_sender = AlertSender(
            token=crede.get('bot_token'),
            chat_id=crede.get('chat_id')
        )
        return alert_sender

    @staticmethod
    def get_name():
        return 'telegram_alerts'


class GrafanaLokiResource(Resource):
    def get_object(self):
        crede = self.c.get_credentials()

        loki_resource = GrafanaLoki(
            url=crede.get('loki_url'),
            tags=crede.get('tags'),
            username=crede.get('username'),
            password=crede.get('password')
        )
        return loki_resource

    @staticmethod
    def get_name():
        return 'grafana_loki'


class Clickhouse(Resource):

    def get_object(self):
        return click_client(**self.c.get_credentials())

    @staticmethod
    def get_name():
        return 'clickhouse'