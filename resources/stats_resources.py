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
class ResourceGetUserStats(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserStats, self).on_post(req, resp, *args, **kwargs)

        try:
            stats = self.db_session.query(Stats).filter(Stats.id == kwargs["user_id"]).one()
            resp.media = stats.json_model
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceUpdateUserStats(DAMCoreResource):
 def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUpdateUserStats, self).on_put(req, resp, *args, **kwargs)

        try:
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

