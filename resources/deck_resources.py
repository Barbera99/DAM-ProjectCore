#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Stats, User, Deck, Card,Deck_Card_Association
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
            all_cards = self.db_session.query(Deck_Card_Association).filter(Deck_Card_Association.deck_id == kwargs["deck_id"]).all()
            for d in all_cards:
                if d.card_id == kwargs["r_card_id"]:
                    d.card_id = kwargs["i_card_id"]
                    self.db_session.add(d)
                    self.db_session.commit()
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
            decks_json = []
            decks = self.db_session.query(Deck).filter(Deck.user_id == kwargs["id"]).all()
            for d in decks:
                deck = {
                    "id": d.id,
                }
                decks_json.append(deck)
            resp.media = decks_json
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
