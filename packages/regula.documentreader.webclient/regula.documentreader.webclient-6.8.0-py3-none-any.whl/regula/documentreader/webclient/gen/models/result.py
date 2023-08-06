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
Describes possible extracted result types from documents
"""
class Result(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    DOCUMENT_IMAGE = int("1")

    IMAGE_QUALITY = int("30")

    STATUS = int("33")

    TEXT = int("36")

    IMAGES = int("37")

    MRZ_TEXT = int("3")

    VISUAL_TEXT = int("17")

    BARCODE_TEXT = int("18")

    RFID_TEXT = int("102")

    LEXICAL_ANALYSIS = int("15")

    VISUAL_GRAPHICS = int("6")

    BARCODE_GRAPHICS = int("19")

    RFID_GRAPHICS = int("103")

    DOCUMENT_TYPE_CANDIDATES = int("8")

    DOCUMENT_TYPE = int("9")

    AUTHENTICITY = int("20")

    DOCUMENT_POSITION = int("85")

    BARCODES = int("5")

    LICENSE = int("50")

    ENCRYPTED_RCL = int("49")

    allowable_values = [DOCUMENT_IMAGE, IMAGE_QUALITY, STATUS, TEXT, IMAGES, MRZ_TEXT, VISUAL_TEXT, BARCODE_TEXT, RFID_TEXT, LEXICAL_ANALYSIS, VISUAL_GRAPHICS, BARCODE_GRAPHICS, RFID_GRAPHICS, DOCUMENT_TYPE_CANDIDATES, DOCUMENT_TYPE, AUTHENTICITY, DOCUMENT_POSITION, BARCODES, LICENSE, ENCRYPTED_RCL]  # noqa: E501

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
    }

    attribute_map = {
    }

    def __init__(self, local_vars_configuration=None):  # noqa: E501
        """Result - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration
        self.discriminator = None

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
        if not isinstance(other, Result):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Result):
            return True

        return self.to_dict() != other.to_dict()
