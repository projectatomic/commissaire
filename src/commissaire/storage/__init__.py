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


class ConfigurationError(Exception):
    """
    Exception class for user configuration errors.
    """
    pass


class StoreHandlerBase(object):
    """
    Base class for all StoreHandler classes.
    """

    # Subclasses override this, if applicable.
    container_manager_class = None

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
            '{0}.check_config() must be overridden.'.format(cls.__name__))

    def __init__(self, config):
        """
        :param config: Configuration details for the StoreHandler.
        :type config: dict
        """
        self._config = config
        self._store = None

    def _get_connection(self):
        """
        Returns an instance of the store. If one has not been created this call
        will also create the client using the self.config.

        :returns: The store instance.
        :rtype: Store Instance
        """
        raise NotImplementedError('_get_connection must be overriden.')

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
        """
        raise NotImplementedError('_get must be overriden.')

    def _delete(self, model_instance):
        """
        Deletes data from a store.

        :param model_instance: Model instance to delete.
        :type model_instance: commissaire.model.Model
        """
        raise NotImplementedError('_delete must be overriden.')

    def _list(self, model_instance):
        """
        Lists data at a location in a store and returns back model instances.

        :param model_instance: Model instance to search for and list.
        :type model_instance: commissaire.model.Model
        :returns: A list of models.
        :rtype: list
        """
        raise NotImplementedError('_list must be overriden.')
