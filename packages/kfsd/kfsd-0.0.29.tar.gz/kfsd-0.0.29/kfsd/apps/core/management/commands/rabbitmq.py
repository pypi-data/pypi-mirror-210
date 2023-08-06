from django.core.management.base import BaseCommand
from kfsd.apps.core.utils.dict import DictUtils
from kfsd.apps.core.msmq.rabbitmq.base import RabbitMQ


class Command(BaseCommand):
    help = "Listens to a RabbitMQ topic"

    def getConnectionArguments(self):
        connectionConfig = DictUtils.get_by_path(
            self.__config, "services.rabbitmq.connect"
        )
        authCredentials = connectionConfig.pop("credentials")
        connectionConfig["credentials"] = RabbitMQ.constructCredentials(
            DictUtils.get(authCredentials, "username"),
            DictUtils.get(authCredentials, "pwd"),
        )
        return connectionConfig

    def handle(self, *args, **options):
        msmqHandler = RabbitMQ()
        self.__config = msmqHandler.getConfig()
        exchangeName = "test_exchange"
        queueName = "test_queue"
        routingKey = "test_routing"

        msmqHandler.publish_msg(
            exchangeName, queueName, routingKey, "hi this is my first msg"
        )

        def callback(ch, method, properties, body):
            print("Msg Body: {}".format(body))

        msmqHandler.consume_msgs(callback, exchangeName, queueName, routingKey)
