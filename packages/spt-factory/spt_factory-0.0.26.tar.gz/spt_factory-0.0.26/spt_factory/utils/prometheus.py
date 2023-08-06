import prometheus_client


class PrometheusResource:

    def __init__(self, gateway, timeout=60):
        self.gateway = gateway
        self.timeout = timeout
        self.registry = prometheus_client.CollectorRegistry()

    def push_to_gateway(self, job: str):
        prometheus_client.push_to_gateway(
            gateway=self.gateway,
            job=job,
            registry=self.registry,
            timeout=self.timeout
        )
