# -*- coding: utf-8 -*-

"""
bandwidth

This file was automatically generated by APIMATIC v3.0 (
 https://www.apimatic.io ).
"""
from bandwidth.messaging.models.bandwidth_message import BandwidthMessage


class BandwidthCallbackMessage(object):

    """Implementation of the 'BandwidthCallbackMessage' model.

    TODO: type model description here.

    Attributes:
        time (string): TODO: type description here.
        mtype (string): TODO: type description here.
        to (string): TODO: type description here.
        error_code (string): TODO: type description here.
        description (string): TODO: type description here.
        message (BandwidthMessage): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "time": 'time',
        "mtype": 'type',
        "to": 'to',
        "error_code": 'errorCode',
        "description": 'description',
        "message": 'message'
    }

    def __init__(self,
                 time=None,
                 mtype=None,
                 to=None,
                 error_code=None,
                 description=None,
                 message=None):
        """Constructor for the BandwidthCallbackMessage class"""

        # Initialize members of the class
        self.time = time
        self.mtype = mtype
        self.to = to
        self.error_code = error_code
        self.description = description
        self.message = message

    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object
            as obtained from the deserialization of the server's response. The
            keys MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        time = dictionary.get('time')
        mtype = dictionary.get('type')
        to = dictionary.get('to')
        error_code = dictionary.get('errorCode')
        description = dictionary.get('description')
        message = BandwidthMessage.from_dictionary(dictionary.get('message')) if dictionary.get('message') else None

        # Return an object of this model
        return cls(time,
                   mtype,
                   to,
                   error_code,
                   description,
                   message)
