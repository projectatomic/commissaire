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
"""
Storage related module for Commissaire.
"""

import logging

from commissaire.errors import CommissaireError
from commissaire.models import Model
from commissaire.storage.notify import StorageNotify


class ConfigurationError(CommissaireError):
    """
    Exception class for user configuration errors.
    """
    pass


class StoreHandlerBase(object):  # pragma: no cover
    """
    Base class for all StoreHandler classes.
    """

    @classmethod
    def check_config(cls, config):
        """
        Examines the configuration parameters for a particular class of
        store handler and throws a ConfigurationError if any parameters
        are invalid.

        :param config: Configuration parameters for the handler type
        :type config: dict
        :raises ConfigurationError: if any parameters are invalid
        """
        raise NotImplementedError(
            '{}.check_config() must be overridden.'.format(cls.__name__))

    def __init__(self, config):
        """
        Initializes a new instance of the StoreHandlerBase.

        :param config: Configuration details for the StoreHandler.
        :type config: dict
        """
        self._config = config
        self._store = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.notify = StorageNotify()

    def _save(self, model_instance):
        """
        Saves data to a store and returns back a saved model.

        :param model_instance: Model instance to save.
        :type model_instance: commissaire.model.Model
        :returns: The saved model instance.
        :rtype: commissaire.model.Model
        """
        raise NotImplementedError('_save must be overriden.')

    def _get(self, model_instance):
        """
        Returns data from a store and returns back a model.

        :param model_instance: Model instance to search and get.
        :type model_instance: commissaire.model.Model
        :returns: The saved model instance.
        :rtype: commissaire.model.Model
        :raises StorageLookupError: if data lookup fails
        """
        raise NotImplementedError('_get must be overriden.')

    def _delete(self, model_instance):
        """
        Deletes data from a store.

        :param model_instance: Model instance to delete.
        :type model_instance: commissaire.model.Model
        :raises StorageLookupError: if data lookup fails
        """
        raise NotImplementedError('_delete must be overriden.')

    def _list(self, model_instance):
        """
        Lists data at a location in a store and returns back model instances.

        :param model_instance: Model instance to search for and list.
        :type model_instance: commissaire.model.ListModel
        :returns: A list of models.
        :rtype: list
        """
        raise NotImplementedError('_list must be overriden.')


def get_uniform_model_type(list_of_model_instances):
    """
    Returns the model type if the models are of the same type.

    :param list_of_model_instances: List of model instances with data to save
    :type list_of_model_instances: [commissaire.models.Model, ...]
    :returns: The model unifrom type
    :rtype: commissaire.models.Model
    :raises: TypeError
    """
    set_of_types = set([type(x) for x in list_of_model_instances])
    if len(set_of_types) > 1:
        raise TypeError('Model instances must be of identical type')
    first_type = set_of_types.pop()
    if not issubclass(first_type, Model):
        raise TypeError('Type must be a Model')
    return first_type
