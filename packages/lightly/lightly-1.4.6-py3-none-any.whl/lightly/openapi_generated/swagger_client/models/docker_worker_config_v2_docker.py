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


class DockerWorkerConfigV2Docker(object):
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
        'checkpoint': 'str',
        'corruptness_check': 'DockerWorkerConfigV3DockerCorruptnessCheck',
        'datasource': 'DockerWorkerConfigV3DockerDatasource',
        'embeddings': 'str',
        'enable_training': 'bool',
        'method': 'str',
        'normalize_embeddings': 'bool',
        'output_image_format': 'str',
        'object_level': 'DockerWorkerConfigV2DockerObjectLevel',
        'pretagging': 'bool',
        'pretagging_upload': 'bool',
        'relevant_filenames_file': 'str',
        'selected_sequence_length': 'int',
        'stopping_condition': 'DockerWorkerConfigV2DockerStoppingCondition',
        'upload_report': 'bool'
    }

    attribute_map = {
        'checkpoint': 'checkpoint',
        'corruptness_check': 'corruptnessCheck',
        'datasource': 'datasource',
        'embeddings': 'embeddings',
        'enable_training': 'enableTraining',
        'method': 'method',
        'normalize_embeddings': 'normalizeEmbeddings',
        'output_image_format': 'outputImageFormat',
        'object_level': 'objectLevel',
        'pretagging': 'pretagging',
        'pretagging_upload': 'pretaggingUpload',
        'relevant_filenames_file': 'relevantFilenamesFile',
        'selected_sequence_length': 'selectedSequenceLength',
        'stopping_condition': 'stoppingCondition',
        'upload_report': 'uploadReport'
    }

    def __init__(self, checkpoint=None, corruptness_check=None, datasource=None, embeddings=None, enable_training=None, method=None, normalize_embeddings=None, output_image_format=None, object_level=None, pretagging=None, pretagging_upload=None, relevant_filenames_file=None, selected_sequence_length=None, stopping_condition=None, upload_report=None, _configuration=None):  # noqa: E501
        """DockerWorkerConfigV2Docker - a model defined in Swagger"""  # noqa: E501
        if _configuration is None:
            _configuration = Configuration()
        self._configuration = _configuration

        self._checkpoint = None
        self._corruptness_check = None
        self._datasource = None
        self._embeddings = None
        self._enable_training = None
        self._method = None
        self._normalize_embeddings = None
        self._output_image_format = None
        self._object_level = None
        self._pretagging = None
        self._pretagging_upload = None
        self._relevant_filenames_file = None
        self._selected_sequence_length = None
        self._stopping_condition = None
        self._upload_report = None
        self.discriminator = None

        if checkpoint is not None:
            self.checkpoint = checkpoint
        if corruptness_check is not None:
            self.corruptness_check = corruptness_check
        if datasource is not None:
            self.datasource = datasource
        if embeddings is not None:
            self.embeddings = embeddings
        if enable_training is not None:
            self.enable_training = enable_training
        if method is not None:
            self.method = method
        if normalize_embeddings is not None:
            self.normalize_embeddings = normalize_embeddings
        if output_image_format is not None:
            self.output_image_format = output_image_format
        if object_level is not None:
            self.object_level = object_level
        if pretagging is not None:
            self.pretagging = pretagging
        if pretagging_upload is not None:
            self.pretagging_upload = pretagging_upload
        if relevant_filenames_file is not None:
            self.relevant_filenames_file = relevant_filenames_file
        if selected_sequence_length is not None:
            self.selected_sequence_length = selected_sequence_length
        if stopping_condition is not None:
            self.stopping_condition = stopping_condition
        if upload_report is not None:
            self.upload_report = upload_report

    @property
    def checkpoint(self):
        """Gets the checkpoint of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The checkpoint of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: str
        """
        return self._checkpoint

    @checkpoint.setter
    def checkpoint(self, checkpoint):
        """Sets the checkpoint of this DockerWorkerConfigV2Docker.


        :param checkpoint: The checkpoint of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: str
        """

        self._checkpoint = checkpoint

    @property
    def corruptness_check(self):
        """Gets the corruptness_check of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The corruptness_check of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: DockerWorkerConfigV3DockerCorruptnessCheck
        """
        return self._corruptness_check

    @corruptness_check.setter
    def corruptness_check(self, corruptness_check):
        """Sets the corruptness_check of this DockerWorkerConfigV2Docker.


        :param corruptness_check: The corruptness_check of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: DockerWorkerConfigV3DockerCorruptnessCheck
        """

        self._corruptness_check = corruptness_check

    @property
    def datasource(self):
        """Gets the datasource of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The datasource of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: DockerWorkerConfigV3DockerDatasource
        """
        return self._datasource

    @datasource.setter
    def datasource(self, datasource):
        """Sets the datasource of this DockerWorkerConfigV2Docker.


        :param datasource: The datasource of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: DockerWorkerConfigV3DockerDatasource
        """

        self._datasource = datasource

    @property
    def embeddings(self):
        """Gets the embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: str
        """
        return self._embeddings

    @embeddings.setter
    def embeddings(self, embeddings):
        """Sets the embeddings of this DockerWorkerConfigV2Docker.


        :param embeddings: The embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: str
        """

        self._embeddings = embeddings

    @property
    def enable_training(self):
        """Gets the enable_training of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The enable_training of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: bool
        """
        return self._enable_training

    @enable_training.setter
    def enable_training(self, enable_training):
        """Sets the enable_training of this DockerWorkerConfigV2Docker.


        :param enable_training: The enable_training of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: bool
        """

        self._enable_training = enable_training

    @property
    def method(self):
        """Gets the method of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The method of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: str
        """
        return self._method

    @method.setter
    def method(self, method):
        """Sets the method of this DockerWorkerConfigV2Docker.


        :param method: The method of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: str
        """

        self._method = method

    @property
    def normalize_embeddings(self):
        """Gets the normalize_embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The normalize_embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: bool
        """
        return self._normalize_embeddings

    @normalize_embeddings.setter
    def normalize_embeddings(self, normalize_embeddings):
        """Sets the normalize_embeddings of this DockerWorkerConfigV2Docker.


        :param normalize_embeddings: The normalize_embeddings of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: bool
        """

        self._normalize_embeddings = normalize_embeddings

    @property
    def output_image_format(self):
        """Gets the output_image_format of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The output_image_format of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: str
        """
        return self._output_image_format

    @output_image_format.setter
    def output_image_format(self, output_image_format):
        """Sets the output_image_format of this DockerWorkerConfigV2Docker.


        :param output_image_format: The output_image_format of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: str
        """

        self._output_image_format = output_image_format

    @property
    def object_level(self):
        """Gets the object_level of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The object_level of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: DockerWorkerConfigV2DockerObjectLevel
        """
        return self._object_level

    @object_level.setter
    def object_level(self, object_level):
        """Sets the object_level of this DockerWorkerConfigV2Docker.


        :param object_level: The object_level of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: DockerWorkerConfigV2DockerObjectLevel
        """

        self._object_level = object_level

    @property
    def pretagging(self):
        """Gets the pretagging of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The pretagging of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: bool
        """
        return self._pretagging

    @pretagging.setter
    def pretagging(self, pretagging):
        """Sets the pretagging of this DockerWorkerConfigV2Docker.


        :param pretagging: The pretagging of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: bool
        """

        self._pretagging = pretagging

    @property
    def pretagging_upload(self):
        """Gets the pretagging_upload of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The pretagging_upload of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: bool
        """
        return self._pretagging_upload

    @pretagging_upload.setter
    def pretagging_upload(self, pretagging_upload):
        """Sets the pretagging_upload of this DockerWorkerConfigV2Docker.


        :param pretagging_upload: The pretagging_upload of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: bool
        """

        self._pretagging_upload = pretagging_upload

    @property
    def relevant_filenames_file(self):
        """Gets the relevant_filenames_file of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The relevant_filenames_file of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: str
        """
        return self._relevant_filenames_file

    @relevant_filenames_file.setter
    def relevant_filenames_file(self, relevant_filenames_file):
        """Sets the relevant_filenames_file of this DockerWorkerConfigV2Docker.


        :param relevant_filenames_file: The relevant_filenames_file of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: str
        """

        self._relevant_filenames_file = relevant_filenames_file

    @property
    def selected_sequence_length(self):
        """Gets the selected_sequence_length of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The selected_sequence_length of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: int
        """
        return self._selected_sequence_length

    @selected_sequence_length.setter
    def selected_sequence_length(self, selected_sequence_length):
        """Sets the selected_sequence_length of this DockerWorkerConfigV2Docker.


        :param selected_sequence_length: The selected_sequence_length of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: int
        """

        self._selected_sequence_length = selected_sequence_length

    @property
    def stopping_condition(self):
        """Gets the stopping_condition of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The stopping_condition of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: DockerWorkerConfigV2DockerStoppingCondition
        """
        return self._stopping_condition

    @stopping_condition.setter
    def stopping_condition(self, stopping_condition):
        """Sets the stopping_condition of this DockerWorkerConfigV2Docker.


        :param stopping_condition: The stopping_condition of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: DockerWorkerConfigV2DockerStoppingCondition
        """

        self._stopping_condition = stopping_condition

    @property
    def upload_report(self):
        """Gets the upload_report of this DockerWorkerConfigV2Docker.  # noqa: E501


        :return: The upload_report of this DockerWorkerConfigV2Docker.  # noqa: E501
        :rtype: bool
        """
        return self._upload_report

    @upload_report.setter
    def upload_report(self, upload_report):
        """Sets the upload_report of this DockerWorkerConfigV2Docker.


        :param upload_report: The upload_report of this DockerWorkerConfigV2Docker.  # noqa: E501
        :type: bool
        """

        self._upload_report = upload_report

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
        if issubclass(DockerWorkerConfigV2Docker, dict):
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
        if not isinstance(other, DockerWorkerConfigV2Docker):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DockerWorkerConfigV2Docker):
            return True

        return self.to_dict() != other.to_dict()
