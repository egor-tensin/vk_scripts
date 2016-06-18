# Copyright 2016 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

from collections import OrderedDict
from collections.abc import Hashable, Mapping, MutableMapping
from enum import Enum

from .last_seen import LastSeen

def _parse_last_seen(x):
    if isinstance(x, LastSeen):
        return x
    elif isinstance(x, Mapping):
        return LastSeen.from_api_response(x)
    else:
        raise TypeError()

def _parse_online_flag(x):
    if isinstance(x, str):
        if str(True) == x:
            return True
        elif str(False) == x:
            return False
        else:
            raise ValueError()
    else:
        return bool(x)

class UserField(Enum):
    UID = 'uid'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    SCREEN_NAME = 'screen_name'
    ONLINE = 'online'
    LAST_SEEN = 'last_seen'

    def __str__(self):
        return self.value

class User(Hashable, MutableMapping):
    @staticmethod
    def from_api_response(source):
        instance = User()
        for field in UserField:
            if str(field) in source:
                instance[field] = source[str(field)]
        return instance

    def __init__(self, fields=None):
        if fields is None:
            fields = OrderedDict()
        self._fields = fields

    def __eq__(self, other):
        return self.get_uid() == other.get_uid()
        #return self._fields == other._fields

    def __hash__(self):
        return hash(self.get_uid())

    def __getitem__(self, field):
        return self._fields[field]

    def __setitem__(self, field, value):
        self._fields[field] = self.parse(field, value)

    def __delitem__(self, field):
        del self._fields[field]

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    @staticmethod
    def parse(field, value):
        if field in User._FIELD_PARSERS:
            return User._FIELD_PARSERS[field](value)
        else:
            return User._DEFAULT_FIELD_PARSER(value)

    _FIELD_PARSERS = {
        UserField.UID: int,
        UserField.ONLINE: _parse_online_flag,
        UserField.LAST_SEEN: _parse_last_seen,
    }

    _DEFAULT_FIELD_PARSER = str

    def get_uid(self):
        return self[UserField.UID]

    def get_first_name(self):
        return self[UserField.FIRST_NAME]

    def set_first_name(self, name):
        self[UserField.FIRST_NAME] = name

    def has_last_name(self):
        return UserField.LAST_NAME in self and self.get_last_name()

    def get_last_name(self):
        return self[UserField.LAST_NAME]

    def set_last_name(self, name):
        self[UserField.LAST_NAME] = name

    def has_screen_name(self):
        return UserField.SCREEN_NAME in self

    def get_screen_name(self):
        if self.has_screen_name():
            return self[UserField.SCREEN_NAME]
        else:
            return 'id' + str(self.get_uid())

    def set_screen_name(self, name):
        self[UserField.SCREEN_NAME] = name

    def has_online_flag(self):
        return UserField.ONLINE in self

    def is_online(self):
        return self[UserField.ONLINE]

    def is_offline(self):
        return not self.is_online()

    def set_online_flag(self, value=True):
        self[UserField.ONLINE] = value

    def has_last_seen(self):
        return UserField.LAST_SEEN in self

    def get_last_seen(self):
        return self[UserField.LAST_SEEN]

    def set_last_seen(self, last_seen):
        self[UserField.LAST_SEEN] = last_seen

    def get_last_seen_time(self):
        return self[UserField.LAST_SEEN].get_time()

    def get_last_seen_time_local(self):
        return self[UserField.LAST_SEEN].get_time().astimezone()

    def get_last_seen_platform(self):
        return self[UserField.LAST_SEEN].get_platform()
