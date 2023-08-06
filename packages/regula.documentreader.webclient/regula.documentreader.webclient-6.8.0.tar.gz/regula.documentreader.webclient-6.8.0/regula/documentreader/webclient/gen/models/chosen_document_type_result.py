# coding: utf-8

"""
    Generated by: https://openapi-generator.tech
"""

import pprint
import re  # noqa: F401

import six

from regula.documentreader.webclient.gen.configuration import Configuration
# this line was added to enable pycharm type hinting
from regula.documentreader.webclient.gen.models import *


"""
Contains information about the type of document that was determined based on the analysis of the provided image
"""
class ChosenDocumentTypeResult(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'one_candidate': 'OneCandidate',
        'buf_length': 'int',
        'light': 'int',
        'list_idx': 'int',
        'page_idx': 'int',
        'result_type': 'int'
    }

    attribute_map = {
        'one_candidate': 'OneCandidate',
        'buf_length': 'buf_length',
        'light': 'light',
        'list_idx': 'list_idx',
        'page_idx': 'page_idx',
        'result_type': 'result_type'
    }

    def __init__(self, one_candidate=None, buf_length=None, light=None, list_idx=None, page_idx=None, result_type=0, local_vars_configuration=None):  # noqa: E501
        """ChosenDocumentTypeResult - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._one_candidate = None
        self._buf_length = None
        self._light = None
        self._list_idx = None
        self._page_idx = None
        self._result_type = None
        self.discriminator = None

        if one_candidate is not None:
            self.one_candidate = one_candidate
        if buf_length is not None:
            self.buf_length = buf_length
        if light is not None:
            self.light = light
        if list_idx is not None:
            self.list_idx = list_idx
        if page_idx is not None:
            self.page_idx = page_idx
        self.result_type = result_type

    @property
    def one_candidate(self):
        """Gets the one_candidate of this ChosenDocumentTypeResult.  # noqa: E501


        :return: The one_candidate of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: OneCandidate
        """
        return self._one_candidate

    @one_candidate.setter
    def one_candidate(self, one_candidate):
        """Sets the one_candidate of this ChosenDocumentTypeResult.


        :param one_candidate: The one_candidate of this ChosenDocumentTypeResult.  # noqa: E501
        :type one_candidate: OneCandidate
        """

        self._one_candidate = one_candidate

    @property
    def buf_length(self):
        """Gets the buf_length of this ChosenDocumentTypeResult.  # noqa: E501


        :return: The buf_length of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: int
        """
        return self._buf_length

    @buf_length.setter
    def buf_length(self, buf_length):
        """Sets the buf_length of this ChosenDocumentTypeResult.


        :param buf_length: The buf_length of this ChosenDocumentTypeResult.  # noqa: E501
        :type buf_length: int
        """

        self._buf_length = buf_length

    @property
    def light(self):
        """Gets the light of this ChosenDocumentTypeResult.  # noqa: E501


        :return: The light of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: int
        """
        return self._light

    @light.setter
    def light(self, light):
        """Sets the light of this ChosenDocumentTypeResult.


        :param light: The light of this ChosenDocumentTypeResult.  # noqa: E501
        :type light: int
        """

        self._light = light

    @property
    def list_idx(self):
        """Gets the list_idx of this ChosenDocumentTypeResult.  # noqa: E501


        :return: The list_idx of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: int
        """
        return self._list_idx

    @list_idx.setter
    def list_idx(self, list_idx):
        """Sets the list_idx of this ChosenDocumentTypeResult.


        :param list_idx: The list_idx of this ChosenDocumentTypeResult.  # noqa: E501
        :type list_idx: int
        """

        self._list_idx = list_idx

    @property
    def page_idx(self):
        """Gets the page_idx of this ChosenDocumentTypeResult.  # noqa: E501


        :return: The page_idx of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: int
        """
        return self._page_idx

    @page_idx.setter
    def page_idx(self, page_idx):
        """Sets the page_idx of this ChosenDocumentTypeResult.


        :param page_idx: The page_idx of this ChosenDocumentTypeResult.  # noqa: E501
        :type page_idx: int
        """

        self._page_idx = page_idx

    @property
    def result_type(self):
        """Gets the result_type of this ChosenDocumentTypeResult.  # noqa: E501

        Same as Result type, but used for safe parsing of not-described values. See Result type.  # noqa: E501

        :return: The result_type of this ChosenDocumentTypeResult.  # noqa: E501
        :rtype: int
        """
        return self._result_type

    @result_type.setter
    def result_type(self, result_type):
        """Sets the result_type of this ChosenDocumentTypeResult.

        Same as Result type, but used for safe parsing of not-described values. See Result type.  # noqa: E501

        :param result_type: The result_type of this ChosenDocumentTypeResult.  # noqa: E501
        :type result_type: int
        """
        if self.local_vars_configuration.client_side_validation and result_type is None:  # noqa: E501
            raise ValueError("Invalid value for `result_type`, must not be `None`")  # noqa: E501

        self._result_type = result_type

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ChosenDocumentTypeResult):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ChosenDocumentTypeResult):
            return True

        return self.to_dict() != other.to_dict()
