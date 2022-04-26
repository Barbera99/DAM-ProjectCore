#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import User, Achievement, User_Achievement
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetUserAchievements(DAMCoreResource):
 def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserAchievements, self).on_get(req, resp, *args, **kwargs)

        try:
            achievements_json = []
            achievements_ids = self.db_session.query(User_Achievement).filter(User_Achievement.columns.user_id == kwargs["user_id"]).all()
            for a in achievements_ids:
                achievement = self.db_session.query(Achievement).filter(Achievement.id == a.achievement_id).one()
                achievements_json.append(achievement.json_model)
            resp.media = achievements_json
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)

class ResourceUnlock(DAMCoreResource):
 def on_post(self, req, resp, *args, **kwargs):
        super(ResourceUnlock, self).on_post(req, resp, *args, **kwargs)

        try:
            resp.media
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)
