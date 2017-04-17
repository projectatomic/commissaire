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
Basic Model structure for commissaire.
"""

import copy
import re
import json

from datetime import datetime

from commissaire import constants as C
from commissaire.errors import CommissaireError


class ModelError(CommissaireError):
    """
    Base exception class for Model errors.
    """
    pass


class ValidationError(ModelError):
    """
    Exception class for validation errors.
    """
    pass


class CoercionError(ModelError):
    """
    Exception class for coercion errors.
    """
    pass


class Model(object):
    """
    Parent class for models.
    """

    #: Dict of attribute_name->{type, regex}. Regex is optional.
    _attribute_map = {}
    #: Attributes which should only be shown if the render is 'secure'
    _hidden_attributes = ()
    #: The primary way of looking up an instance
    _primary_key = None
    #: Defaults to use for attributes when calling new()
    _attribute_defaults = {}

    def __init__(self, **kwargs):
        """
        Creates a new instance of a Model.

        :param kwargs: All keyword arguments to create the model.
        :type kwargs: dict
        :returns: The Model instance.
        :rtype: commissaire.model.Model
        """
        # self._attributes = self._attribute_map.keys()
        for key in list(self._attribute_map.keys()):
            if key not in kwargs:
                raise TypeError(
                    '{}.__init__() missing 1 or more required '
                    'keyword arguments: {}'.format(
                        self.__class__.__name__,
                        ', '.join(self._attribute_map.keys())))
            setattr(self, key, kwargs[key])

    @classmethod
    def new(cls, **kwargs):
        """
        Returns an instance with default values.

        :param kwargs: Any arguments explicitly set.
        :type kwargs: dict
        """
        instance = cls.__new__(cls)
        init_args = copy.deepcopy(cls._attribute_defaults)
        init_args.update(kwargs)
        instance.__init__(**init_args)
        return instance

    def __str__(self):  # pragma: no cover
        """
        Returns a string representation of the instance.

        :returns: String representation of this instance.
        :rtype: str
        """
        readable = '<{}'.format(self.__class__.__name__)
        for k, v in self.to_dict_safe().items():
            readable += ' {}={},'.format(k, v or '<Empty>')
        return readable + '...>'

    @property
    def primary_key(self):  # pragma: no cover
        """
        Shortcut property to get the value of the primary key.

        :returns: The primary key value.
        :rtype: mixed
        """
        return getattr(self, self._primary_key)

    def _struct_for_json(self, secure=False):
        """
        Returns the proper structure for a model to be used in JSON.

        :param secure: If the structure needs to respect _hidden_attributes.
        :type secure: bool
        :returns: A dict or list depending
        :rtype: dict or list
        """
        data = {}
        for key in list(self._attribute_map.keys()):
            if secure:
                data[key] = getattr(self, key)
            elif key not in self._hidden_attributes:
                data[key] = getattr(self, key)
        return data

    def to_json(self, expose=[]):
        """
        Returns a JSON representation of this model.

        :param expose: List of non-exposed attributes to include in result.
        :type expose: list
        :returns: The JSON representation.
        :rtype: str
        """
        struct = self._struct_for_json(secure=True)
        for key in expose:
            value = getattr(self, key)
            if value:
                struct[key] = value
        return json.dumps(struct)

    def to_json_safe(self, expose=[]):
        """
        Returns a JSON representation of this model, omitting all hidden
        attributes.  Use this when preparing data for display to users.

        :param expose: List of non-exposed attributes to include in result.
        :type expose: list
        :returns: The JSON representation.
        :rtype: str
        """
        struct = self._struct_for_json(secure=False)
        for key in expose:
            value = getattr(self, key)
            if value:
                struct[key] = value
        return json.dumps(struct)

    def to_dict(self, expose=[]):
        """
        Returns a dict representation of this model. This is different than
        using __dict__ as the returned data will be model specific only.

        :param expose: List of non-exposed attributes to include in result.
        :type expose: list
        :returns: the dict representation.
        :rtype: dict
        """
        # Instead of reimplementing the logic take the performance hit of
        # going between native and json
        return json.loads(self.to_json(expose))

    def to_dict_safe(self, expose=[]):
        """
        Returns a dict representation of this model, omitting all hidden
        attributes.  This is different than using __dict__ as the returned
        data will be model specific only.  Use this when preparing data for
        display to users.

        :param expose: List of non-exposed attributes to include in result.
        :type expose: list
        :returns: the dict representation.
        :rtype: dict
        """
        # Instead of reimplementing the logic take the performance hit of
        # going between native and json
        return json.loads(self.to_json_safe(expose))

    def _validate(self, errors=[]):
        """
        Validates the attribute data of the current instance.

        :param errors: Errors from any pre-validation.
        :type errors: list

        :raises: ValidationError
        """
        all_errors = [] + errors
        for attr, spec in self._attribute_map.items():
            value = getattr(self, attr)
            if not isinstance(value, spec['type']):
                all_errors.append(
                    '{}.{}: Expected type {}. Got {}'.format(
                        self.__class__.__name__, attr,
                        spec['type'], type(value)))

            try:
                if spec.get('regex') and not re.match(spec['regex'], value):
                    all_errors.append(
                        '{}.{}: Value did validate against the '
                        'provided regular expression "{}"'.format(
                            self.__class__.__name__, attr, spec['regex']))
            except TypeError:
                all_errors.append(
                    '{}.{}: Value can not be validated by a '
                    'regular expression'.format(self.__class__.__name__, attr))

        if all_errors:
            raise ValidationError(
                '{} instance is invalid due to {} errors.'.format(
                    self.__class__.__name__, len(all_errors)), all_errors)

    def _must_be_in(self, attribute, allowed_types, errors):
        """
        Used to ensure an attribute is of one of the allowed types.

        :param attribute: The name of the attribute to check.
        :type attribute: str
        :param allowed_types: List of allowed types
        :param errors: Error list used in validation
        :type errors: list
        :returns: The updated error list.
        :rtype: list
        """
        if getattr(self, attribute) not in allowed_types:
            errors.append(
                'Container {} must be one of the following: {}'.format(
                    attribute, ', '.join(allowed_types)))
        return errors

    def _coerce(self):
        """
        Attempts to force the typing set forth in _attribute_map.

        :raises: commissaire.model.CoercionError
        """
        errors = []
        for attr, spec in self._attribute_map.items():
            value = getattr(self, attr)
            if not isinstance(value, spec['type']):
                try:
                    caster = spec['type']
                    if spec['type'] is str:
                        caster = str

                    setattr(self, attr, caster(value))
                except Exception as ex:
                    errors.append(
                        '{}.{} can not be coerced from {} to {} '
                        'due to {}: {}'.format(
                            self.__class__.__name__, attr,
                            type(value), spec['type'], type(ex), ex))
        if errors:
            raise CoercionError(
                '{} instance failed coercion due to {} errors.'.format(
                    len(errors), errors))


class SecretModel(Model):
    """
    Parent class for all models which must be stored in the secrets store.
    """
    pass


class ListModel(Model):
    """
    Base class for models representing a list of models.
    """

    #: The attribute name which stores items
    _list_attr = None
    #: The class for items which will be stored in the list
    _list_class = None

    def __str__(self):  # pragma: no cover
        """
        Returns a string representation of the instance.

        :returns: String representation of this instance.
        :rtype: str
        """
        return '<{} {}...>'.format(
            self.__class__.__name__,
            self.to_json_safe())

    def _struct_for_json(self, secure=False):
        """
        Returns the proper structure for a model to be used in JSON.

        :param secure: If the structure needs to respect _hidden_attributes.
        :type secure: bool
        :returns: A dict or list depending
        :rtype: dict or list
        """
        if len(self._attribute_map.keys()) == 1:
            data = getattr(self, list(self._attribute_map.keys())[0])
        return [x._struct_for_json(secure) for x in data]


class Network(Model):
    """
    Representation of a network.

    .. note::

       This model is similar to ContainerManagerConfig.
    """
    _attribute_map = {
        'name': {'type': str},
        'type': {'type': str},
        'options': {'type': dict},
    }
    _attribute_defaults = {
        'type': C.NETWORK_TYPE_FLANNEL_ETCD,
        'options': {},
    }
    _primary_key = 'name'

    def _validate(self):
        """
        Extra validation to ensure the type is valid.
        """
        errors = []
        self._must_be_in('type', C.NETWORK_TYPES, errors)
        super()._validate(errors)


class Networks(ListModel):
    """
    Representation of a group of one or more Networks.
    """
    _attribute_map = {
        'networks': {'type': list},
    }
    _attribute_defaults = {'networks': []}
    _list_attr = 'networks'
    _list_class = Network


class Cluster(Model):
    """
    Representation of a Cluster.
    """
    _attribute_map = {
        'name': {'type': str},
        'status': {'type': str},
        'network': {'type': str},
        'hostset': {'type': list},
        'container_manager': {'type': str},
    }
    _hidden_attributes = ('hostset',)
    _attribute_defaults = {
        'status': '',
        'hostset': [],
        'network': C.DEFAULT_CLUSTER_NETWORK_JSON['name'],
        'container_manager': '',
    }
    _primary_key = 'name'

    def __init__(self, **kwargs):
        """
        Creates a new instance of Cluster.

        :param kwargs: All keyword arguments to create the Cluster model.
        :type kwargs: dict
        :returns: The Cluster instance.
        :rtype: commissaire.model.Cluster
        """
        Model.__init__(self, **kwargs)
        # Hosts is always calculated, not stored in etcd.
        self.hosts = {'total': 0,
                      'available': 0,
                      'unavailable': 0}


class ClusterDeploy(Model):
    """
    Representation of a Cluster deploy operation.
    """
    _attribute_map = {
        'name': {'type': str},
        'status': {'type': str},
        'version': {'type': str},
        'deployed': {'type': list},
        'in_process': {'type': list},
        'started_at': {'type': str},
        'finished_at': {'type': str},
    }
    _attribute_defaults = {
        'status': '', 'version': '',
        'deployed': [], 'in_process': [], 'started_at': '', 'finished_at': ''}
    _primary_key = 'name'

    def _validate(self):
        """
        Extra validation for ClusterDeploy.
        """
        errors = []
        if self.version in ('', None):
            errors.append('version must be a non empty string')
        if self.name in ('', None):
            errors.append('name must be a non empty string')
        super()._validate(errors)


class ClusterRestart(Model):
    """
    Representation of a Cluster restart operation.
    """
    _attribute_map = {
        'name': {'type': str},
        'status': {'type': str},
        'restarted': {'type': list},
        'in_process': {'type': list},
        'started_at': {'type': str},
        'finished_at': {'type': str},
    }

    _attribute_defaults = {
        'status': '', 'restarted': [],
        'in_process': [], 'started_at': '', 'finished_at': ''}
    _primary_key = 'name'

    def _validate(self):
        """
        Extra validation for ClusterRestart.
        """
        errors = []
        if self.name in ('', None):
            errors.append('name must be a non empty string')
        super()._validate(errors)


class ClusterUpgrade(Model):
    """
    Representation of a Cluster upgrade operation.
    """
    _attribute_map = {
        'name': {'type': str},
        'status': {'type': str},
        'upgraded': {'type': list},
        'in_process': {'type': list},
        'started_at': {'type': str},
        'finished_at': {'type': str},
    }

    _attribute_defaults = {
        'status': '', 'upgraded': [],
        'in_process': [], 'started_at': '', 'finished_at': ''}
    _primary_key = 'name'

    def _validate(self):
        """
        Extra validation for ClusterRestart.
        """
        errors = []
        if self.name in ('', None):
            errors.append('name must be a non empty string')
        super()._validate(errors)


class Clusters(ListModel):
    """
    Representation of a group of one or more Clusters.
    """
    _attribute_map = {
        'clusters': {'type': list},
    }
    _attribute_defaults = {'clusters': []}
    _list_attr = 'clusters'
    _list_class = Cluster


class Host(Model):
    """
    Representation of a Host.
    """
    _attribute_map = {
        'address': {'type': str},
        'status': {'type': str},
        'os': {'type': str},
        'cpus': {'type': int},
        'memory': {'type': int},
        'space': {'type': int},
        'last_check': {'type': str},
        'source': {'type': str},
    }
    _attribute_defaults = {
        'status': '', 'os': '', 'cpus': 0,
        'memory': 0, 'space': 0, 'last_check': '', 'source': ''}
    _primary_key = 'address'


class HostCreds(SecretModel):
    """
    Representation of Host credentials.
    """
    _json_type = dict
    _attribute_map = {
        'address': {'type': str},
        'ssh_priv_key': {'type': str},
        'remote_user': {'type': str},
    }
    _attribute_defaults = {
        'ssh_priv_key': '',
        'remote_user': 'root',
    }
    _primary_key = 'address'


class HostStatus(Model):
    """
    Representation of Host status.
    """
    _attribute_map = {
        'type': {'type': str},
        'host': {'type': dict},
        'container_manager': {'type: dict'},
    }
    _attribute_defaults = {
        'type': '',
        'host': {},
        'container_manager': {}
    }


class Hosts(ListModel):
    """
    Representation of a group of one or more Hosts.
    """
    _attribute_map = {
        'hosts': {'type': list},
    }
    _attribute_defaults = {'hosts': []}
    _list_attr = 'hosts'
    _list_class = Host


class WatcherRecord(Model):
    """
    Representation of a single record in a watcher queue.
    """
    _attribute_map = {
        'address': {'type': str},
        'last_check': {'type': str},
    }
    _attribute_defaults = {
        'address': '',
        'last_check': datetime.max.isoformat(),
    }

    def _validate(self):
        """
        Extra validation for WatcherRecord.
        """
        errors = []
        try:
            datetime.strptime(self.last_check, C.DATE_FORMAT)
        except ValueError:
            errors.append(
                'last_check must be in isoformat: "{}"'.format(C.DATE_FORMAT))
        super()._validate(errors)


class ContainerManagerConfig(Model):
    """
    Representation of a ContainerManager configuration record.

    .. note::

       This model is similar to Network. The options attribute holds
       configuration items used to create a ContainerManager instance.
    """
    _attribute_map = {
        'name': {'type': str},
        'type': {'type': str},
        'options': {'type': dict},
    }
    _attribute_defaults = {
        'type': C.CONTAINER_MANAGER_DEFAULT,
        'options': {},
    }
    _primary_key = 'name'

    def _validate(self):
        """
        Extra validation for ContainerManager.
        """
        errors = []
        self._must_be_in('type', C.CONTAINER_MANAGER_TYPES, errors)
        super()._validate(errors)


class ContainerManagerConfigs(ListModel):
    """
    Representation of a group of one or more ContainerManagers.
    """
    _attribute_map = {
        'container_managers': {'type': list},
    }
    _attribute_defaults = {'container_managers': []}
    _list_attr = 'container_managers'
    _list_class = ContainerManagerConfig
