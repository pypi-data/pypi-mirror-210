# coding: utf-8

"""
    Lightly API

    Lightly.ai enables you to do self-supervised learning in an easy and intuitive way. The lightly.ai OpenAPI spec defines how one can interact with our REST API to unleash the full potential of lightly.ai  # noqa: E501

    OpenAPI spec version: 1.0.0
    Contact: support@lightly.ai
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from lightly.openapi_generated.swagger_client.configuration import Configuration


class DockerWorkerConfigV3LightlyLoader(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'batch_size': 'int',
        'shuffle': 'bool',
        'num_workers': 'int',
        'drop_last': 'bool'
    }

    attribute_map = {
        'batch_size': 'batchSize',
        'shuffle': 'shuffle',
        'num_workers': 'numWorkers',
        'drop_last': 'dropLast'
    }

    def __init__(self, batch_size=None, shuffle=None, num_workers=None, drop_last=None, _configuration=None):  # noqa: E501
        """DockerWorkerConfigV3LightlyLoader - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._batch_size = None
        self._shuffle = None
        self._num_workers = None
        self._drop_last = None
        self.discriminator = None

        if batch_size is not None:
            self.batch_size = batch_size
        if shuffle is not None:
            self.shuffle = shuffle
        if num_workers is not None:
            self.num_workers = num_workers
        if drop_last is not None:
            self.drop_last = drop_last

    @property
    def batch_size(self):
        """Gets the batch_size of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501


        :return: The batch_size of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :rtype: int
        """
        return self._batch_size

    @batch_size.setter
    def batch_size(self, batch_size):
        """Sets the batch_size of this DockerWorkerConfigV3LightlyLoader.


        :param batch_size: The batch_size of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :type: int
        """

        self._batch_size = batch_size

    @property
    def shuffle(self):
        """Gets the shuffle of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501


        :return: The shuffle of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :rtype: bool
        """
        return self._shuffle

    @shuffle.setter
    def shuffle(self, shuffle):
        """Sets the shuffle of this DockerWorkerConfigV3LightlyLoader.


        :param shuffle: The shuffle of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :type: bool
        """

        self._shuffle = shuffle

    @property
    def num_workers(self):
        """Gets the num_workers of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501


        :return: The num_workers of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :rtype: int
        """
        return self._num_workers

    @num_workers.setter
    def num_workers(self, num_workers):
        """Sets the num_workers of this DockerWorkerConfigV3LightlyLoader.


        :param num_workers: The num_workers of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :type: int
        """

        self._num_workers = num_workers

    @property
    def drop_last(self):
        """Gets the drop_last of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501


        :return: The drop_last of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :rtype: bool
        """
        return self._drop_last

    @drop_last.setter
    def drop_last(self, drop_last):
        """Sets the drop_last of this DockerWorkerConfigV3LightlyLoader.


        :param drop_last: The drop_last of this DockerWorkerConfigV3LightlyLoader.  # noqa: E501
        :type: bool
        """

        self._drop_last = drop_last

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(DockerWorkerConfigV3LightlyLoader, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DockerWorkerConfigV3LightlyLoader):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DockerWorkerConfigV3LightlyLoader):
            return True

        return self.to_dict() != other.to_dict()
