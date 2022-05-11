#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import random
import messages
from db.models import Map
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetRandomMap(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetRandomMap, self).on_post(req, resp, *args, **kwargs)

        try:
            maps = self.db_session.query(Map).all()
            n = random.randint(0, len(maps) - 1)
            resp.media = maps[n].json_model
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
