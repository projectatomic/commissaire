# Copyright (C) 2016  Red Hat, Inc
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

import kombu

import commissaire.models as models

from commissaire.bus import RemoteProcedureCallError
from commissaire.storage import get_uniform_model_type


NOTIFY_EVENT_CREATED = 'created'
NOTIFY_EVENT_DELETED = 'deleted'
NOTIFY_EVENT_CHANGED = 'changed'
NOTIFY_EVENT_ANY = '*'


class StorageClient:
    """
    Convenience API for talking to the storage service.
    """

    def __init__(self, bus_mixin):
        """
        Creates a new StorageClient.

        :param bus_mixin: An object that includes the BusMixin API
        :type bus_mixin: commissaire.bus.BusMixin
        """
        self.bus_mixin = bus_mixin
        self.notify_callbacks = {}

    def register_callback(self, callback,
                          model_type=None,
                          event=NOTIFY_EVENT_ANY):
        """
        Registers a callback to be invoked on receipt of a change notification
        from the storage service whose routing key matches the given model type
        and event name.  Pass None for the model_type, and/or NOTIFY_EVENT_ANY
        for the event to use wildcards in routing key pattern to match.

        The signature of the callback must take two arguments: (body, message),
        which is the decoded message body and the Message instance.

        :param callback: A callable to invoke.
        :type callback: callable
        :param model_type: A model type to filter on, or None.
        :type model_type: Type or None
        :param event: An event name to filter on, or NOTIFY_EVENT_ANY.
        :type event: str
        """
        type_name = '*' if model_type is None else model_type.__name__
        routing_key = 'notify.storage.{}.{}'.format(type_name, event)
        callback_list = self.notify_callbacks.setdefault(routing_key, [])
        callback_list.append(callback)

    def get_consumers(self, Consumer, channel):
        """
        Returns a list of kombu.Consumer instances to service all registered
        notification callbacks.

        If using the kombu.mixin.ConsumerMixin mixin class, these instances
        should be included in its get_consumers() method.

        :param Consumer: Message consumer class.
        :type Consumer: class
        :param channel: An open channel.
        :type channel: kombu.transport.*.Channel
        :returns: A list of consumer instances
        :rtype: [kombu.Consumer, ....]
        """
        consumer_list = []
        exchange = self.bus_mixin.producer.exchange
        for routing_key, callbacks in self.notify_callbacks.items():
            queue = kombu.Queue(
                exchange=exchange, routing_key=routing_key)
            consumer = Consumer(
                queues=queue, callbacks=callbacks)
            consumer_list.append(consumer)
            self.bus_mixin.logger.info(
                'Listening for "%s" notifications', routing_key)
        return consumer_list

    def get(self, model_instance):
        """
        Issues a "storage.get" request over the bus using identifying
        data from the model instance and returns a new model instance
        from the response data.

        :param model_instance: Model instance with identifying data
        :type model_instance: commissaire.models.Model
        :returns: A new model instance with stored data
        :rtype: commissaire.models.Model
        :raises: commissaire.bus.RemoteProcedureCallError
        """
        try:
            params = {
                'model_type_name': model_instance.__class__.__name__,
                'model_json_data': model_instance.to_dict()
            }
            response = self.bus_mixin.request('storage.get', params=params)
            return model_instance.__class__.new(**response['result'])
        except RemoteProcedureCallError as error:
            self.bus_mixin.logger.error(
                '%s: Unable to get %s "%s": %s',
                self.bus_mixin.__class__.__name__,
                model_instance.__class__.__name__,
                model_instance.primary_key,
                error)
            raise error

    def get_many(self, list_of_model_instances):
        """
        Similar to StorageClient.get(), but takes a list of model instances and
        returns a list of model instances.  The models must be of the same type
        or else the function throws a TypeError.

        :param list_of_model_instances: List of model instances with
                                        identifying data
        :type list_of_model_instances: [commissaire.models.Model, ...]
        :returns: List of new model instances with stored data
        :rtype: [commissaire.models.Model, ...]
        :raises: TypeError, commissaire.bus.RemoteProcedureCallError
        """
        # Handle the trivial case immediately
        if len(list_of_model_instances) == 0:
            return []

        model_class = get_uniform_model_type(list_of_model_instances)

        try:
            model_json_data = [x.to_dict() for x in list_of_model_instances]
            params = {
                'model_type_name': model_class.__name__,
                'model_json_data': model_json_data
            }
            response = self.bus_mixin.request('storage.get', params=params)
            return [model_class.new(**x) for x in response['result']]
        except RemoteProcedureCallError as error:
            self.bus_mixin.logger.error(
                '%s: Unable to get multiple %s records: %s',
                self.bus_mixin.__class__.__name__,
                model_class.__name__,
                error)
            raise error

    def save(self, model_instance):
        """
        Issues a "storage.save" request over the bus using data from
        the model instance and returns a new model instance from the
        response data.  The model instance is validated prior to the
        remote procedure call.

        :param model_instance: Model instance with data to save
        :type model_instance: commissaire.models.Model
        :returns: A new model instance with all saved fields
        :rtype: commissaire.models.Model
        :raises: commissaire.bus.RemoteProcedureCallError,
                 commissaire.models.ValidationError
        """
        try:
            model_instance._validate()
            params = {
                'model_type_name': model_instance.__class__.__name__,
                'model_json_data': model_instance.to_dict()
            }
            response = self.bus_mixin.request('storage.save', params=params)
            return model_instance.__class__.new(**response['result'])
        except (RemoteProcedureCallError, models.ValidationError) as error:
            self.bus_mixin.logger.error(
                '%s: Unable to save %s "%s": %s',
                self.bus_mixin.__class__.__name__,
                model_instance.__class__.__name__,
                model_instance.primary_key,
                error)
            raise error

    def save_many(self, list_of_model_instances):
        """
        Similar to StorageClient.save(), but takes a list of model instances
        and returns a list of model instances.  The models must be of the same
        type or else the function throws a TypeError.

        :param list_of_model_instances: List of model instances with data to
                                        save
        :type list_of_model_instances: [commissaire.models.Model, ...]
        :returns: List of new model instances with all saved fields
        :rtype: [commissaire.models.Model, ...]
        :raises: TypeError, commissaire.bus.RemoteProcedureCallError,
                 commissaire.models.ValidationError
        """
        # Handle the trivial case immediately
        if len(list_of_model_instances) == 0:
            return []

        model_class = get_uniform_model_type(list_of_model_instances)

        try:
            for model_instance in list_of_model_instances:
                model_instance._validate()
            model_json_data = [x.to_dict() for x in list_of_model_instances]
            params = {
                'model_type_name': model_class.__name__,
                'model_json_data': model_json_data
            }
            response = self.bus_mixin.request('storage.save', params=params)
            return [model_class.new(**x) for x in response['result']]
        except (RemoteProcedureCallError, models.ValidationError) as error:
            self.bus_mixin.logger.error(
                '%s: Unable to save multiple %s records: %s',
                self.bus_mixin.__class__.__name__,
                model_class.__name__,
                error)
            raise error

    def delete(self, model_instance):
        """
        Issues a "storage.delete" request over the bus using identifying
        data from the model instance.

        :param model_instance: Model instance with identifying data
        :type model_instance: commissaire.models.Model
        :raises: commissaire.bus.RemoteProcedureCallError
        """
        try:
            params = {
                'model_type_name': model_instance.__class__.__name__,
                'model_json_data': model_instance.to_dict()
            }
            self.bus_mixin.request('storage.delete', params=params)
        except RemoteProcedureCallError as error:
            self.bus_mixin.logger.error(
                '%s: Unable to delete %s "%s": %s',
                self.bus_mixin.__class__.__name__,
                model_instance.__class__.__name__,
                model_instance.primary_key,
                error)
            raise error

    def delete_many(self, list_of_model_instances):
        """
        Similar to StorageClient.delete(), but takes a list of model instances.
        The models must be of the same type or else the function throws a
        TypeError.

        :param list_of_model_instances: List of model instances with
                                        identifying data
        :type list_of_model_instances: [commissaire.models.Model, ...]
        :raises: TypeError, commissaire.bus.RemoteProcedureCallError
        """
        # Handle the trivial case immediately
        if len(list_of_model_instances) == 0:
            return

        model_class = get_uniform_model_type(list_of_model_instances)

        try:
            model_json_data = [x.to_dict() for x in list_of_model_instances]
            params = {
                'model_type_name': model_class.__name__,
                'model_json_data': model_json_data
            }
            self.bus_mixin.request('storage.delete', params=params)
        except RemoteProcedureCallError as error:
            self.bus_mixin.logger.error(
                '%s: Unable to delete multiple %s records: %s',
                self.bus_mixin.__class__.__name__,
                model_class.__name__,
                error)
            raise error

    def list(self, model_class):
        """
        Issues a "storage.list" request over the bus for the given model
        class, and returns a new model instance from the response data.

        :param model_class: A concrete list model class
        :type model_class: commissaire.models.ListModel
        :returns: A new model instance
        :rtype: model_class
        :raises: commissaire.bus.RemoteProcedureCallError,
                 commissaire.models.ValidationError
        """
        try:
            assert issubclass(model_class, models.ListModel)
            params = {
                'model_type_name': model_class.__name__
            }
            response = self.bus_mixin.request('storage.list', params=params)
            model_list = []
            child_class = model_class._list_class
            for child_dict in response['result']:
                child_instance = child_class.new(**child_dict)
                child_instance._validate()
                model_list.append(child_instance)
            model_instance = model_class.new()
            setattr(model_instance, model_class._list_attr, model_list)
            return model_instance
        except (RemoteProcedureCallError, models.ValidationError) as error:
            self.bus_mixin.logger.error(
                '%s: Unable to list %ss: %s',
                self.bus_mixin.__class__.__name__,
                model_class.__name__,
                error)
            raise error

    # -----------------------------------------------------------------------
    # Model-specific methods (esp. listable types)
    # -----------------------------------------------------------------------

    def get_cluster(self, name):
        """
        Issues a "storage.get" request for a cluster record over the bus
        and returns a new Cluster instance from the response data.

        :param name: Cluster name
        :type name: str
        :returns: A new Cluster instance with stored data
        :rtype: commissaire.models.Cluster
        :raises: commissaire.bus.RemoteProcedureCallError
        """
        return self.get(models.Cluster.new(name=name))

    def get_host(self, address):
        """
        Issues a "storage.get" request for a host record over the bus
        and returns a new Host instance from the response data.

        :param address: Host address
        :type address: str
        :returns: A new Host instance with stored data
        :rtype: commissaire.models.Host
        :raises: commissaire.bus.RemoteProcedureCallError
        """
        return self.get(models.Host.new(address=address))

    def get_network(self, name):
        """
        Issues a "storage.get" request for a network record over the bus
        and returns a new Network instance from the response data.

        :param name: Network name
        :type name: str
        :returns: A new Network instance with stored data
        :rtype: commissaire.models.Network
        :raises: commissaire.bus.RemoteProcedureCallError
        """
        return self.get(models.Network.new(name=name))
