"""
Instrument and Operator classes
"""
# Standard library modules
import warnings
import re
import logging

from obspy.core.inventory.util import (Operator as obspy_Operator,
                                       Person, PhoneNumber)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Operator(object):  # Previously a Channel subclass, but don't see why
    """
    Contact information for the operator of the instrumentation or network

    Attributes:
        reference_name (str): Reference name of operator as known to the FDSN
        full_name (str): Full name of operator
        contact (dict of two strings: first_name and last_name)
        email (str)
        country_code (str)
        area_code (str): unused for non-American phones.
        phone_number (str): formatted according to strange FDSN rules
            ([0-9]+-[0-9]
        website (str)
    """

    def __init__(self, attributes_dict):
        """
        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): operator information
        """
        if not attributes_dict:
            raise ValueError('No attributes dict!')

        self.reference_name = attributes_dict.get('reference_name', None)
        self.full_name = attributes_dict.get('full_name', '')
        contact_name = attributes_dict.get('contact', None)

        if contact_name:
            self.contact = contact_name.get('first_name', '') \
                           + " " + contact_name.get('last_name', '')
        else:
            self.contact = ""

        self.email = attributes_dict.get('email', None)
        self.country_code, self.area_code, self.phone_number = \
            self.convert_phone_number(attributes_dict.get('phone_number',
                                                          None))
        self.website = attributes_dict.get('website', None)

    def __str__(self):
        s = f'\nOperator: Reference Name={self.reference_name}\n'
        s += f'\tFull Name={self.full_name}\n'
        if self.contact:
            s += f'\tContact Name={self.contact}\n'
        s += f'\tEmail={self.email}\n'
        s += f'\tPhone_number={self.phone_number}\n'
        s += f'\tWebsite={self.website}'

        return s

    def convert_phone_number(self, phone):
        """
        Try to convert international numbers to the FDSN American standard.
        If already in American standard, use area code.

        Args:
            phone (str): phone number in (hopefully) one of several
                recognisable formats
        Returns:
            (tuple):
                ``country_code``
                ``area_code``: default=0
                ``phone_number``
        """
        country_code = None
        area_code = "0"
        phone_number = ""

        if not phone:
            return (country_code, area_code, phone_number)

        if isinstance(phone, dict):
            country_code = phone.get('country_code', None)
            area_code = phone.get('area_code', "")
            phone_number = phone.get('phone_number', "")
        elif isinstance(phone, type("")):
            # For reference:
            # country = re.compile("^(\+{0,1}|00)[0-9]{1,3}$")
            # area = re.compile("^\({0,1}[0-9]{3}\){0,1}$")
            # phone = re.compile("^[0-9]{3}\-[0-9]{4}$")

            us_phone_ptrn = '(?P<country>(\\+{0,1}|00)[0-9]{1,3}) '\
                            '*(?P<area>\\({0,1}[0-9]{3}\\){0,1}) '\
                            '*(?P<phone>[0-9]{3}\\-[0-9]{4})$'
            us_phone_re = re.compile(us_phone_ptrn)

            us_phone_match = us_phone_re.match(phone)
            if us_phone_match:
                country_code = us_phone_match.group['country']
                area_code = us_phone_match.group['area']
                phone_number = us_phone_match.group['phone']
            else:
                c_code_plus_ptn = '^\+([0-9]{1,3})'
                c_code_zero_ptn = "^00([0-9]{1,3})"
                c_code_plus_re = re.compile(c_code_plus_ptn)
                c_code_zero_re = re.compile(c_code_zero_ptn)
                phone_ptn = "(?P<phone>(\([0-9]+\))* *([0-9]+[ \-\.]*)*[0-9]+)$"

                c_code = c_code_plus_re.match(phone)
                if not c_code:  # | for alternatives in regex doesn't work
                    c_code = c_code_zero_re.match(phone)
                    phone_re = re.compile(c_code_zero_ptn + " *" + phone_ptn)
                else:
                    phone_re = re.compile(c_code_plus_ptn + " *" + phone_ptn)

                if c_code:
                    country_code = c_code.group(1)

                mtch = phone_re.match(phone)
                if mtch:
                    phone_number = mtch.group('phone')
                    # The following is done to avoid FDSN reg exp restrictions
                    # for phones, American based
                    for chr in ["(", ")", ".", "-", " "]:
                        phone_number = phone_number.replace(chr, "")
                    phone_number = phone_number[0:3] + "-" + phone_number[3:]
        else:
            pass
        return (country_code, area_code, phone_number)

    def to_obspy(self):
        emails = [self.email] if self.email else []
        phones = [PhoneNumber(self.area_code,
                              self.phone_number,
                              self.country_code)]\
            if self.phone_number else []
        names = [self.contact] if self.contact else []
        agencies = [self.reference_name] \
            if self.reference_name else []
        person = Person(names=names,
                        agencies=agencies,
                        emails=emails,
                        phones=phones)
        return obspy_Operator(agency=self.full_name,
                              contacts=[person],
                              website=self.website)
