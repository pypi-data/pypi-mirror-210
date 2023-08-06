from abc import ABC


class Credentials(ABC):
    __slots__ = 'crede', 'crede_object', 'factory_params', 'custom_params', 'spt'

    def __init__(self, spt, factory_params, custom_params):
        self.spt = spt
        self.factory_params = factory_params
        self.custom_params = custom_params

    def get_credentials(self):
        return self.crede


class PostgresMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            postgres_crede = mongo_client.spt.credentials.find_one({"type": "postgres"})
        postgres_crede['sslrootcert'] = factory_params['tlsCAFile']
        self.crede = postgres_crede
        self.crede.update(custom_params)
        del postgres_crede['_id']
        del postgres_crede['type']


class GreenplumMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            greenplum_crede = mongo_client.spt.credentials.find_one({"type": "greenplum"})
        greenplum_crede['sslrootcert'] = factory_params['tlsCAFile']
        self.crede = greenplum_crede
        self.crede.update(custom_params)
        del greenplum_crede['_id']
        del greenplum_crede['type']


class MongoMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        self.crede = {
            'host': factory_params['mongo_url'],
            'tlsCAFile': factory_params['tlsCAFile']
        }
        self.crede.update(custom_params)


class AnyMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            any_crede = mongo_client.spt.credentials.find_one({"type": custom_params.get('type', "undefined")})
        if any_crede is None:
            self.crede = {'type': custom_params.get('type', "undefined")}
        else:
            self.crede = any_crede
            self.crede.update(custom_params)
            del any_crede['_id']
            del custom_params['type']


class S3ManagerCredentials(Credentials):
    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)

        with spt.get_crede_object() as mongo_client:
            s3_crede = mongo_client.spt.credentials.find_one({"type": "theme-s3"})
        self.crede = s3_crede
        self.crede.update(custom_params)
        del s3_crede['_id']
        del s3_crede['type']


class PrometheusPushgatewayCredentials(Credentials):
    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_mongo() as mongo_client:
            crede = mongo_client.spt.credentials.find_one({"type": "prometheus"})
        self.crede = crede


class TelegramAlertsCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_mongo() as mongo_client:
            crede = mongo_client.spt.credentials.find_one({"type": "core_alert_bot"})
        self.crede = crede


class GrafanaLokiCredentials(Credentials):
    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_mongo() as mongo_client:
            crede = mongo_client.spt.credentials.find_one({"type": "core_grafana_loki"})
        self.crede = crede


class ClickhouseMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            click_crede = mongo_client.spt.credentials.find_one({"type": "clickhouse"})
        click_crede['ca_certs'] = factory_params['tlsCAFile']
        self.crede = click_crede
        self.crede.update(custom_params)
        del click_crede['_id']
        del click_crede['type']