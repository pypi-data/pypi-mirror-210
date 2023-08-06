"""
Copyright (c) 2021 Ricardo Baylon rbaylon@outlook.com

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
from ctypes import CDLL, c_char_p
import os, pwd, re


class Validator(object):
    def is_username_valid(self, username):
        """
           Validate username based on OpenBSD's passwd(5) username specs.
        """
        if re.search('^[a-z]+[0-9|\-|_|a-z]+$', username) and len(username) <= 31:
            return True
        else:
            return False

    def is_password_valid(self, password):
        """
           Validate password based on OpenBSD's passwd(1) password specs.
        """
        if len(password) >= 6 and len(password) <= 128:
            return True
        else:
            return False


class UserOkay(object):
    """
        Initialize this object with username and password strings.
        If username and password are None then return None. For security
        reason make sure to delete the password variable after you psss it 
        to this class.
    """
    def __init__(self, username=None, password=None):
        v = Validator()
        if not username or not password:
            raise ValueError('Empty username or password not allowed.')

        if v.is_username_valid(username) and v.is_password_valid(password):
            user = c_char_p()
            passwd = c_char_p()
            user.value = str.encode(username)
            passwd.value = str.encode(password)
            self.username = user
            self.password = passwd
        else:
            raise ValueError('Invalid username or password')

    def login(self):
        """
            Using OpenBSD's auth_userokay(3) from libc BSD Auth api. auth_userokay(3)
            deletes the password from memory for security reasons. Be sure to
            instanciate this class every after self.login() call if you need to login
            again. If calling process is not owned by root return None. root privilege 
            is required by BSD Auth.
        """
        sofile = '/usr/lib/libc.so*'
        authstyle = c_char_p()
        authstyle.value = str.encode('passwd')
        authtype = c_char_p()
        authtype.value = str.encode('auth-python')
        auth = CDLL(sofile)
        ret = auth.auth_userokay(self.username, authstyle, authtype, self.password)
        if ret != 0:
            return True
        else:
            return False

    def destroypw(self):
        """ 
            Delete password stored in memory in case self.login() is not called.
        """
        self.password.value = None
