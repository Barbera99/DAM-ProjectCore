#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from resources import stats_resources
import messages
from db.models import User, GenereEnum, Deck, Stats
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetUserProfile(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserProfile, self).on_get(req, resp, *args, **kwargs)
        mylogger.info("Obtenint perfil...")

        if "username" in kwargs:
            try:
                aux_user = self.db_session.query(User).filter(User.username == kwargs["username"]).one()
                resp.media = aux_user.public_profile
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.user_not_found)


class ResourceRegisterUser(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceRegisterUser, self).on_post(req, resp, *args, **kwargs)
        mylogger.info("Creating default users...")
        user = User()
        try:
            try:
                aux_genere = GenereEnum(req.media["genere"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            user.username = req.media["username"]
            user.set_password(req.media["password"])
            user.email = req.media["email"]
            user.name = req.media["name"]
            user.surname = req.media["surname"]
            date = datetime.strptime(req.media["birthdate"], '%Y-%m-%d')
            user.birthdate = date
            user.genere = aux_genere
            user.rank_id = 1
            user.phone = req.media["phone"]
            user.photo = req.media["photo"]
            user.status = "active"
            self.db_session.add(user)
            try:
                self.db_session.commit()
                current_user = self.db_session.query(User).filter(User.username == req.media["username"]).one()
                createDeck(current_user.id)
                createStats(current_user.id)
                try:
                    self.db_session.commit()
                except IntegrityError:
                    raise falcon.HTTPBadRequest(description=messages.database_error)
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.database_error)
        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)
        resp.status = falcon.HTTP_200


''' Funció auxiliar per a crear la baralla'''
def createDeck(self, user_id):
    mylogger.info("Creating user decks...")
    deck = Deck()
    try:
        deck.user_id = user_id
        self.db_session.add(deck)
    except KeyError:
        raise falcon.HTTPBadRequest(description=messages.parameters_invalid)


''' Funció auxiliar per a crear els Stats'''
def createStats(self, user_id):
    mylogger.info("Creating user stats...")
    stats = Stats()
    try:
        stats.user_id = user_id
        self.db_session.add(stats)
    except KeyError:
        raise falcon.HTTPBadRequest(description=messages.parameters_invalid)


class ResourceUpdateUserProfile(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUpdateUserProfile, self).on_put(req, resp, *args, **kwargs)
        mylogger.info("Updating user ")
        current_user = self.db_session.query(User).filter(User.id == kwargs["user_id"]).one()
        try:
            try:
                aux_genere = GenereEnum(req.media["genere"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            current_user.username = req.media["username"]
            current_user.set_password(req.media["password"])
            current_user.email = req.media["email"]
            current_user.name = req.media["name"]
            current_user.surname = req.media["surname"]
            current_user.birthdate = req.media["birthdate"]
            current_user.genere = aux_genere
            current_user.phone = req.media["phone"]
            current_user.photo = req.media["photo"]
            self.db_session.add(current_user)
            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.database_error)
            resp.status = falcon.HTTP_200
        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)



class ResourceUserUnsubscribe(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUserUnsubscribe, self).on_put(req, resp, *args, **kwargs)
        mylogger.info("Unsubscribing user...")
        try:
            aux_user = self.db_session.query(User).filter(User.id == kwargs["user_id"]).one()
            aux_user.status = "inactive"
            self.db_session.add(aux_user)
            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.database_error)
            resp.status = falcon.HTTP_200
        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.user_status_invalid)


class ResourceUserDelete(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUserDelete, self).on_put(req, resp, *args, **kwargs)
        mylogger.info("Deleting user ")
        try:
            aux_user = self.db_session.query(User).filter(User.id == kwargs["user_id"]).one()
        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.user_status_invalid)