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
from resources.schemas import SchemaGameEnd
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
                "date": date.date.strftime("%m/%d/%Y %H:%M:%S"),
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
        if "user_id" in kwargs:
            mylogger.info(" Creant partida... ")
            game = Game()
            ug = User_Game_Association()
            ugia = User_Game_Association()
            try:
                game.date = datetime.now()
                self.db_session.add(game)
                self.db_session.commit()
                self.db_session.refresh(game)
                try:
                    #IA
                    ugia.user_id = req.media["user1_id"]
                    ugia.score = req.media["user1_score"]

                    #Usuari
                    ug.game_id = game.id
                    ug.user_id = kwargs["user2_id"]
                    ug.score = req.media["user2_score"]

                    self.db_session.add(ug)
                    self.db_session.add(ugia)
                    self.db_session.commit()

                    resp.status = falcon.HTTP_200
                except NoResultFound:
                    raise falcon.HTTPBadRequest(description=messages.game_not_found)
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.game_not_found)
        else:
            resp.status = falcon.HTTPBadRequest


#@falcon.before(requires_auth)
class ResourceEndGame(DAMCoreResource):
    @jsonschema.validate(SchemaGameEnd)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceEndGame, self).on_put(req, resp, *args, **kwargs)
        try:
            ug_arr = self.db_session.query(User_Game_Association).filter(User_Game_Association.game_id == kwargs["game_id"]).all()
            ug1 = ug_arr[0]
            ug2 = ug_arr[1]
            if ug1.user_id == req.media["user1_id"]:
                ug1.score = req.media["user1_score"]
                ug2.score = req.media["user2_score"]
            else:
                ug2.score = req.media["user1_score"]
                ug1.score = req.media["user2_score"]

            self.db_session.commit()
            resp.status = falcon.HTTP_200

        except NoResultFound:
            raise falcon.HTTPBadRequest(description=messages.game_not_found)
