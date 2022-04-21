#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Stats, User
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetUserAchievements(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserAchievements, self).on_get(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceUnlock(DAMCoreResource):
 def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUnlock, self).on_put(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
