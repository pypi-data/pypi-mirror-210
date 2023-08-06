# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Membership Handler
"""

import warnings

from rattail.util import load_object
from rattail.app import GenericHandler


class MembershipHandler(GenericHandler):
    """
    Base class and default implementation for membership handlers.
    """

    def ensure_member(self, person, **kwargs):
        """
        Returns the Member record associated with the given person, creating
        it first if necessary.
        """
        raise NotImplementedError

    def make_member(self, person, **kwargs):
        """
        Make and return a new Member instance.
        """
        raise NotImplementedError

    def begin_membership(self, member, **kwargs):
        """
        Begin an active membership.
        """
        raise NotImplementedError

    def get_member(self, obj):
        """
        Returns the member associated with the given person, if there is one.
        """
        model = self.model

        if isinstance(obj, model.Member):
            return obj

        person = self.app.get_person(obj)
        if person and person.members:
            return person.members[0]

    def get_customer(self, obj):
        """
        Returns the customer associated with the given member, if there is one.
        """
        warnings.warn("MembershipHandler.get_customer() is deprecated; "
                      "please use AppHandler.get_customer() instead")

        return self.app.get_customer(obj)

    def get_person(self, obj):
        """
        Returns the person associated with the given member, if there is one.
        """
        warnings.warn("MembershipHandler.get_person() is deprecated; "
                      "please use AppHandler.get_person() instead")

        return self.app.get_person(obj)

    def get_last_patronage_date(self, member, **kwargs):
        raise NotImplementedError
