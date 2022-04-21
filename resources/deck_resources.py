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
class ResourceCreateDeck(DAMCoreResource):
 def on_post(self, req, resp, *args, **kwargs):
        super(ResourceCreateDeck, self).on_post(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceUpdateDeck(DAMCoreResource):
 def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUpdateDeck, self).on_put(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceGetDeck(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetDeck, self).on_get(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceGetUserDecks(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserDecks, self).on_get(req, resp, *args, **kwargs)

        if "user_id" in kwargs:
            try:
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.user_not_found)
