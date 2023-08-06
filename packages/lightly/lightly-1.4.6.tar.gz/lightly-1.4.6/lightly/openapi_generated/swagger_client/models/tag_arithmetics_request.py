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


class TagArithmeticsRequest(object):
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
        'tag_id1': 'MongoObjectID',
        'tag_id2': 'MongoObjectID',
        'operation': 'TagArithmeticsOperation',
        'new_tag_name': 'TagName',
        'creator': 'TagCreator',
        'run_id': 'MongoObjectID'
    }

    attribute_map = {
        'tag_id1': 'tagId1',
        'tag_id2': 'tagId2',
        'operation': 'operation',
        'new_tag_name': 'newTagName',
        'creator': 'creator',
        'run_id': 'runId'
    }

    def __init__(self, tag_id1=None, tag_id2=None, operation=None, new_tag_name=None, creator=None, run_id=None, _configuration=None):  # noqa: E501
        """TagArithmeticsRequest - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._tag_id1 = None
        self._tag_id2 = None
        self._operation = None
        self._new_tag_name = None
        self._creator = None
        self._run_id = None
        self.discriminator = None

        self.tag_id1 = tag_id1
        self.tag_id2 = tag_id2
        self.operation = operation
        if new_tag_name is not None:
            self.new_tag_name = new_tag_name
        if creator is not None:
            self.creator = creator
        if run_id is not None:
            self.run_id = run_id

    @property
    def tag_id1(self):
        """Gets the tag_id1 of this TagArithmeticsRequest.  # noqa: E501


        :return: The tag_id1 of this TagArithmeticsRequest.  # noqa: E501
        :rtype: MongoObjectID
        """
        return self._tag_id1

    @tag_id1.setter
    def tag_id1(self, tag_id1):
        """Sets the tag_id1 of this TagArithmeticsRequest.


        :param tag_id1: The tag_id1 of this TagArithmeticsRequest.  # noqa: E501
        :type: MongoObjectID
        """
        if self._configuration.client_side_validation and tag_id1 is None:
            raise ValueError("Invalid value for `tag_id1`, must not be `None`")  # noqa: E501

        self._tag_id1 = tag_id1

    @property
    def tag_id2(self):
        """Gets the tag_id2 of this TagArithmeticsRequest.  # noqa: E501


        :return: The tag_id2 of this TagArithmeticsRequest.  # noqa: E501
        :rtype: MongoObjectID
        """
        return self._tag_id2

    @tag_id2.setter
    def tag_id2(self, tag_id2):
        """Sets the tag_id2 of this TagArithmeticsRequest.


        :param tag_id2: The tag_id2 of this TagArithmeticsRequest.  # noqa: E501
        :type: MongoObjectID
        """
        if self._configuration.client_side_validation and tag_id2 is None:
            raise ValueError("Invalid value for `tag_id2`, must not be `None`")  # noqa: E501

        self._tag_id2 = tag_id2

    @property
    def operation(self):
        """Gets the operation of this TagArithmeticsRequest.  # noqa: E501


        :return: The operation of this TagArithmeticsRequest.  # noqa: E501
        :rtype: TagArithmeticsOperation
        """
        return self._operation

    @operation.setter
    def operation(self, operation):
        """Sets the operation of this TagArithmeticsRequest.


        :param operation: The operation of this TagArithmeticsRequest.  # noqa: E501
        :type: TagArithmeticsOperation
        """
        if self._configuration.client_side_validation and operation is None:
            raise ValueError("Invalid value for `operation`, must not be `None`")  # noqa: E501

        self._operation = operation

    @property
    def new_tag_name(self):
        """Gets the new_tag_name of this TagArithmeticsRequest.  # noqa: E501


        :return: The new_tag_name of this TagArithmeticsRequest.  # noqa: E501
        :rtype: TagName
        """
        return self._new_tag_name

    @new_tag_name.setter
    def new_tag_name(self, new_tag_name):
        """Sets the new_tag_name of this TagArithmeticsRequest.


        :param new_tag_name: The new_tag_name of this TagArithmeticsRequest.  # noqa: E501
        :type: TagName
        """

        self._new_tag_name = new_tag_name

    @property
    def creator(self):
        """Gets the creator of this TagArithmeticsRequest.  # noqa: E501


        :return: The creator of this TagArithmeticsRequest.  # noqa: E501
        :rtype: TagCreator
        """
        return self._creator

    @creator.setter
    def creator(self, creator):
        """Sets the creator of this TagArithmeticsRequest.


        :param creator: The creator of this TagArithmeticsRequest.  # noqa: E501
        :type: TagCreator
        """

        self._creator = creator

    @property
    def run_id(self):
        """Gets the run_id of this TagArithmeticsRequest.  # noqa: E501


        :return: The run_id of this TagArithmeticsRequest.  # noqa: E501
        :rtype: MongoObjectID
        """
        return self._run_id

    @run_id.setter
    def run_id(self, run_id):
        """Sets the run_id of this TagArithmeticsRequest.


        :param run_id: The run_id of this TagArithmeticsRequest.  # noqa: E501
        :type: MongoObjectID
        """

        self._run_id = run_id

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
        if issubclass(TagArithmeticsRequest, dict):
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
        if not isinstance(other, TagArithmeticsRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TagArithmeticsRequest):
            return True

        return self.to_dict() != other.to_dict()
