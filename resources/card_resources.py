#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Card
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetCardStats(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetCardStats, self).on_get(req, resp, *args, **kwargs)
        try:
            aux_card = self.db_session.query(Card).filter(Card.id == kwargs["card_id"]).one()
            resp.media = aux_card.json_model


class ResourceGetCardImage(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetCardImage, self).on_get(req, resp, *args, **kwargs)

        try:
            aux_card = self.db_session.query(Card).filter(Card.id == kwargs["card_id"]).one()
            resp.media = aux_card.image
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)


class ResourceUpgradeCard (DAMCoreResource):
 def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUpgradeCard, self).on_put(req, resp, *args, **kwargs)
        current_user = req.context["auth_user"]

        if "card_id" in kwargs:
            try:

                aux_user = self.db_session.query(User).filter(User.username == kwargs["username"]).one()

                resp.media = aux_user.public_profile
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.user_not_found)