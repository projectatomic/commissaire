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

import commissaire.models as models

from commissaire.bus import RemoteProcedureCallError
from commissaire.storage import get_uniform_model_type


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
                '{}: Unable to get {} "{}": {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_instance.__class__.__name__,
                    model_instance.primary_key, error))
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
                '{}: Unable to get multiple {} records: {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_class.__name__, error))
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
                '{}: Unable to save {} "{}": {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_instance.__class__.__name__,
                    model_instance.primary_key, error))
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
                '{}: Unable to save multiple {} records: {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_class.__name__, error))
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
                '{}: Unable to delete {} "{}": {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_instance.__class__.__name__,
                    model_instance.primary_key, error))
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
                '{}: Unable to delete multiple {} records: {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_class.__name__, error))
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
                '{}: Unable to list {}s: {}'.format(
                    self.bus_mixin.__class__.__name__,
                    model_class.__name__, error))
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
