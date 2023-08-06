from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

from kfsd.apps.models.base import BaseModel
from kfsd.apps.core.utils.system import System
from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.core.msmq.rabbitmq.base import RabbitMQ


class Outpost(BaseModel):
    STATUS_CHOICES = (
        ("P", "PENDING"),
        ("I", "IN-PROGRESS"),
        ("C", "COMPLETED"),
    )

    msg_queue_info = models.JSONField(default=dict)
    msg = models.JSONField(default=dict)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
    attempts = models.IntegerField(default=0)
    debug_info = models.CharField(max_length=MAX_LENGTH, default="")

    def save(self, *args, **kwargs):
        self.identifier = System.uuid(32)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Outpost"
        verbose_name_plural = "Outpost"


@receiver(post_save, sender=Outpost)
def send_msg(sender, instance, created, **kwargs):
    if created:
        rabbitMQ = RabbitMQ()
        rabbitMQ.publish_msg_and_close_connection(
            instance.msg_queue_info["exchange_name"],
            instance.msg_queue_info["queue_name"],
            instance.msg_queue_info["routing_key"],
            json.dumps(instance.msg),
        )
