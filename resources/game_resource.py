#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Game
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser

mylogger = logging.getLogger(__name__)


@falcon.before(requires_auth)
class ResourceGetGame(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetGame, self).on_get(req, resp, *args, **kwargs)

        try:
            game = self.db_session.query(Game)

            resp.media = game.json_model
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.game_not_found)


'''class ResourceRegisterUser(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceRegisterUser, self).on_post(req, resp, *args, **kwargs)

        aux_user = User()

        try:
            try:
                aux_genere = GenereEnum(req.media["genere"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            aux_user.username = req.media["username"]
            aux_user.password = User.set_password(req.media["password"])
            aux_user.email = req.media["email"]
            aux_user.name = req.media["name"]
            aux_user.surname = req.media["surname"]
            aux_user.birthdate = req.media["birthdate"]
            aux_user.genere = aux_genere
            aux_user.rank_id = 1
            aux_user.phone = req.media["phone"]
            aux_user.photo = req.media["photo"]

            self.db_session.add(aux_user)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.user_exists)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200 '''

