#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import User, GenereEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetUserProfile(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserProfile, self).on_get(req, resp, *args, **kwargs)

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

            #Arreglar la data algun dia
            aux = req.media["birthdate"]
            aux.split("-")
            date = datetime(int(aux[0]), int(aux[1]), int(aux[2]))
            #date = datetime.strptime(req.media["birthdate"], '%Y-%m-%d')
            user.birthdate = date

            user.genere = aux_genere

            user.rank_id = 1

            user.phone = req.media["phone"]
            user.photo = req.media["photo"]

            #mylogger.info(user.username)
            self.db_session.add(user)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.database_error)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200