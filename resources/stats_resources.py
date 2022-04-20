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
 def on_post(self, req, resp, *args, **kwargs):
        super(ResourceGetUserStats, self).on_post(req, resp, *args, **kwargs)

        try:
            aux_card = self.db_session.query(Card).filter(Card.id == kwargs["card_id"]).one()
            resp.media = aux_card.photo_path
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

