# Copyright (C) 2017  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

import kombu


class StorageNotify(object):
    """
    Publishes storage changes on the "notify" exchange.
    """

    def __init__(self):
        """
        Creates a new instance of StorageNotify.

        Note, the connect() method must be called before notification
        messages can be published.
        """
        name = self.__class__.__name__
        self.logger = logging.getLogger(name)
        self._queue = None
        self._producer = None

    def connect(self, exchange, channel):  # pragma: no cover
        """
        Readies the StorageNotify for publishing notification messages by
        setting up a kombu.Producer.

        :param exchange: The exchange for publishing notifications.
        :type exchange: kombu.Exchange
        :param channel: The channel to bind to.
        :type channel: kombu.transport.base.StdChannel
        """
        name = self.__class__.__name__
        self.logger.debug('Connecting {}'.format(name))

        self._queue = kombu.Queue(exchange=exchange, channel=channel)
        self._queue.declare()

        self._producer = kombu.Producer(channel, exchange)

    def _publish(self, event, model_instance):
        """
        Internal function to publish "created", "deleted", and "updated"
        notification messages.

        :param event: The event name ("created", "deleted", or "updated")
        :type event: str
        :param model_instance: The model instance upon which the event occurred
        :type model_instance: commissaire.model.Model
        """
        class_name = model_instance.__class__.__name__
        body = {
            'event': event,
            'class': class_name,
            'model': model_instance.to_dict_safe()
        }
        routing_key = 'notify.storage.{}.{}'.format(class_name, event)
        if self._producer:
            self.logger.debug('Publish "{}": {}'.format(routing_key, body))
            self._producer.publish(
                body, routing_key,
                kombu.Exchange.TRANSIENT_DELIVERY_MODE)
        else:
            # This means the connect() method was not called.
            self.logger.warn('Not publishing "%s"', routing_key)

    def created(self, model_instance):
        """
        Publishes a message with routing key "notify.storage.MODEL.created",
        where "MODEL" is the class name of the given model instance.

        The message body consists of a dictionary with three keys: "event",
        which for this function is always "created"; "class", the class name
        of the model instance; and "model", a dictionary of the full model
        written to permanent storage (excluding hidden attributes).

        Storage backends are responsible for calling this function when
        creating a new record in permanent stroage.

        :param model_instance: The created model instance
        :type model_instance: commissaire.model.Model
        """
        self._publish('created', model_instance)

    def deleted(self, model_instance):
        """
        Publishes a message with routing key "notify.storage.MODEL.deleted",
        where "MODEL" is the class name of the given model instance.

        The message body consists of a dictionary with three keys: "event",
        which for this function is always "deleted"; "class", the class name
        of the model instance; and "model", a dictionary of the full model
        deleted from permanent storage (excluding hidden attributes).

        Storage backends are responsible for calling this function when
        deleting a record from permanent storage.

        :param model_instance: The deleted model instance
        :type model_instance: commissaire.model.Model
        """
        self._publish('deleted', model_instance)

    def updated(self, model_instance):
        """
        Publishes a message with routing key "notify.storage.MODEL.updated",
        where "MODEL" is the class name of the given model instance.

        The message body consists of a dictionary with three keys: "event",
        which for this function is always "updated"; "class", the class name
        of the model instance; and "model", a dictionary of the full model
        written to permanent storage (excluding hidden attributes).

        Storage backends are responsible for calling this function when
        updating an existing record in permanent storage.

        :param model_instance: The updated model instance
        :type model_instance: commissaire.model.Model
        """
        self._publish('updated', model_instance)
