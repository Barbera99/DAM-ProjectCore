#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Rank, User
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetRankInfo(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetRankInfo, self).on_post(req, resp, *args, **kwargs)
        try:
            rank = self.db_session.query(Rank).filter(Rank.id == kwargs["id_rank"]).one()
            resp.media = rank.json_model
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
