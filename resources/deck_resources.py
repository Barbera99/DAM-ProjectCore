#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Stats, User, Deck
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
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
        mylogger.info("Obtenint baralla individual...")
        try:
            aux_deck = self.db_session.query(Deck).filter(Deck.id == kwargs["id"]).one()
            resp.media = aux_deck.json_model
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceGetUserDecks(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserDecks, self).on_get(req, resp, *args, **kwargs)
        mylogger.info("Obtenint baralles d'un usuari...")
        try:
            games_json = []
            decks = self.db_session.query(Deck).filter(Deck.user_id == kwargs["id"])
            for d in decks:
                deck = {
                    "id": d.id,
                    "user_id": d.user_id
                }
                games_json.append(deck)
            resp.media = games_json
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
