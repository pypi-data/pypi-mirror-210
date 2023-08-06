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


class DatasourceConfigOBS(object):
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
        'obs_endpoint': 'str',
        'obs_access_key_id': 'str',
        'obs_secret_access_key': 'str'
    }

    attribute_map = {
        'obs_endpoint': 'obsEndpoint',
        'obs_access_key_id': 'obsAccessKeyId',
        'obs_secret_access_key': 'obsSecretAccessKey'
    }

    def __init__(self, obs_endpoint=None, obs_access_key_id=None, obs_secret_access_key=None, _configuration=None):  # noqa: E501
        """DatasourceConfigOBS - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._obs_endpoint = None
        self._obs_access_key_id = None
        self._obs_secret_access_key = None
        self.discriminator = None

        self.obs_endpoint = obs_endpoint
        self.obs_access_key_id = obs_access_key_id
        self.obs_secret_access_key = obs_secret_access_key

    @property
    def obs_endpoint(self):
        """Gets the obs_endpoint of this DatasourceConfigOBS.  # noqa: E501

        The Object Storage Service (OBS) endpoint to use of your S3 compatible cloud storage provider  # noqa: E501

        :return: The obs_endpoint of this DatasourceConfigOBS.  # noqa: E501
        :rtype: str
        """
        return self._obs_endpoint

    @obs_endpoint.setter
    def obs_endpoint(self, obs_endpoint):
        """Sets the obs_endpoint of this DatasourceConfigOBS.

        The Object Storage Service (OBS) endpoint to use of your S3 compatible cloud storage provider  # noqa: E501

        :param obs_endpoint: The obs_endpoint of this DatasourceConfigOBS.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and obs_endpoint is None:
            raise ValueError("Invalid value for `obs_endpoint`, must not be `None`")  # noqa: E501

        self._obs_endpoint = obs_endpoint

    @property
    def obs_access_key_id(self):
        """Gets the obs_access_key_id of this DatasourceConfigOBS.  # noqa: E501

        The Access Key Id of the credential you are providing Lightly to use  # noqa: E501

        :return: The obs_access_key_id of this DatasourceConfigOBS.  # noqa: E501
        :rtype: str
        """
        return self._obs_access_key_id

    @obs_access_key_id.setter
    def obs_access_key_id(self, obs_access_key_id):
        """Sets the obs_access_key_id of this DatasourceConfigOBS.

        The Access Key Id of the credential you are providing Lightly to use  # noqa: E501

        :param obs_access_key_id: The obs_access_key_id of this DatasourceConfigOBS.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and obs_access_key_id is None:
            raise ValueError("Invalid value for `obs_access_key_id`, must not be `None`")  # noqa: E501

        self._obs_access_key_id = obs_access_key_id

    @property
    def obs_secret_access_key(self):
        """Gets the obs_secret_access_key of this DatasourceConfigOBS.  # noqa: E501

        The Secret Access Key of the credential you are providing Lightly to use  # noqa: E501

        :return: The obs_secret_access_key of this DatasourceConfigOBS.  # noqa: E501
        :rtype: str
        """
        return self._obs_secret_access_key

    @obs_secret_access_key.setter
    def obs_secret_access_key(self, obs_secret_access_key):
        """Sets the obs_secret_access_key of this DatasourceConfigOBS.

        The Secret Access Key of the credential you are providing Lightly to use  # noqa: E501

        :param obs_secret_access_key: The obs_secret_access_key of this DatasourceConfigOBS.  # noqa: E501
        :type: str
        """
        if self._configuration.client_side_validation and obs_secret_access_key is None:
            raise ValueError("Invalid value for `obs_secret_access_key`, must not be `None`")  # noqa: E501

        self._obs_secret_access_key = obs_secret_access_key

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
        if issubclass(DatasourceConfigOBS, dict):
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
        if not isinstance(other, DatasourceConfigOBS):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DatasourceConfigOBS):
            return True

        return self.to_dict() != other.to_dict()
