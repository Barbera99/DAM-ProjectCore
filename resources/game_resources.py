#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import json
import messages
from db.models import User, Game, GenereEnum, User_Game_Association
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser
from datetime import datetime

mylogger = logging.getLogger(__name__)


#@falcon.before(requires_auth)
class ResourceGetUserGames(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserGames, self).on_get(req, resp, *args, **kwargs)
        mylogger.info(" Obtenint partides... ")

        try:
            games_json = []
            games_played = self.db_session.query(User_Game_Association).filter(User_Game_Association.user_id == 1)
            for g in games_played:
                games = self.db_session.query(User_Game_Association).filter(User_Game_Association.game_id == g.game_id)
                date = self.db_session.query(Game).filter(Game.id == g.game_id).one()
                user1 = self.db_session.query(User).filter(User.id == games[0].user_id).one()
                user2 = self.db_session.query(User).filter(User.id == games[1].user_id).one()
                game = {
                    "id": g.game_id,
                    "date": date.date.strftime("%m/%d/%Y, %H:%M:%S"),
                    "user1": user1.username,
                    "score1": games[0].score,
                    "user2": user2.username,
                    "score2": games[1].score
                }
                games_json.append(game)
            resp.media = games_json
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.user_not_found)


#@falcon.before(requires_auth)
class ResourceGetGame(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetGame, self).on_get(req, resp, *args, **kwargs)
        try:
            games = self.db_session.query(User_Game_Association).filter(User_Game_Association.game_id == kwargs["game_id"])
            date = self.db_session.query(Game).filter(Game.id == kwargs["game_id"]).one()
            user1 = self.db_session.query(User).filter(User.id == games[0].user_id).one()
            user2 = self.db_session.query(User).filter(User.id == games[1].user_id).one()
            game = {
                "id": kwargs["game_id"],
                "date": date.date.strftime("%m/%d/%Y, %H:%M:%S"),
                "user1": user1.username,
                "score1": games[0].score,
                "user2": user2.username,
                "score2": games[1].score
            }
            resp.media = game
            resp.status = falcon.HTTP_200
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.game_not_found)

#@falcon.before(requires_auth)
class ResourceStartGame(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceStartGame, self).on_post(req, resp, *args, **kwargs)
        game = Game()
        ug = User_Game_Association()
        try:
            game.date = datetime.datetime.now()
            self.db_session.add(game)
            self.db_session.commit()
            game_id = self.db_session.query(Game).filter(Game.id == req.media["id"]).one()
            try:
                ug.user_id = kwargs["user_id"]
                ug.game_id = game_id
                self.db_session.add(ug)
                self.db_session.commit()
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.game_not_found)
        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.game_not_found)


#@falcon.before(requires_auth)
class ResourceEndGame(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceEndGame, self).on_get(req, resp, *args, **kwargs)