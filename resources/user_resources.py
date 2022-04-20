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

            date = datetime.strptime(req.media["birthdate"], '%Y-%m-%d')
            user.birthdate = date

            user.genere = aux_genere

            user.rank_id = 1

            user.phone = req.media["phone"]
            user.photo = req.media["photo"]

            # mylogger.info(user.username)
            self.db_session.add(user)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.database_error)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200

''' Preguntar com podem actualitzar un usuari agafant aquest amb el req.context["auth_user"] '''
class ResourceUpdateUserProfile(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUpdateUserProfile, self).on_put(req, resp, *args, **kwargs)
        mylogger.info("Updating user ")
        current_user = req.context["auth_user"]

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
        mylogger.info("Unsubscribing user ")
        user = User()

class ResourceUserDelete(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceUserDelete, self).on_put(req, resp, *args, **kwargs)
        mylogger.info("Deleting user ")
        user = User()