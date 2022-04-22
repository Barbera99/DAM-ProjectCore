#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config

import falcon

import messages
import middlewares
from falcon_multipart.middleware import MultipartMiddleware
from resources import account_resources, common_resources, user_resources, game_resources, card_resources, stats_resources, map_resources, deck_resources, achievement_resources
from settings import configure_logging

#S'inicia amb docker-compose up backend

# LOGGING
mylogger = logging.getLogger(__name__)
configure_logging()


# DEFAULT 404
# noinspection PyUnusedLocal
def handle_404(req, resp):
    resp.media = messages.resource_not_found
    resp.status = falcon.HTTP_404


# FALCON
app = application = falcon.API(
    middleware=[
        middlewares.DBSessionManager(),
        middlewares.Falconi18n(),
        MultipartMiddleware()
    ]
)
application.add_route("/", common_resources.ResourceHome())

application.add_route("/account/profile", account_resources.ResourceAccountUserProfile())
application.add_route("/account/profile/update_profile_image", account_resources.ResourceAccountUpdateProfileImage())
application.add_route("/account/create_token", account_resources.ResourceCreateUserToken())
application.add_route("/account/delete_token", account_resources.ResourceDeleteUserToken())


#USERS
# post
application.add_route("/users/register", user_resources.ResourceRegisterUser()) # fet pero falta inicialitzar stats, baralles, ...

# get
application.add_route("/user/{username}", user_resources.ResourceGetUserProfile()) # FET

# put
application.add_route("/user/profile/update/{user_id}", user_resources.ResourceUpdateUserProfile()) # Pendent de canviar el auth_user
application.add_route("/user/unsuscribe/{user_id}", user_resources.ResourceUserUnsubscribe())

# delete
application.add_route("/user/delete/{username}", user_resources.ResourceUserDelete())

#GAME
# post
application.add_route("/game/start/{user_id}", game_resources.ResourceStartGame())

# put
application.add_route("/game/end/{game_id}", game_resources.ResourceEndGame())

# get
application.add_route("/game/show/{game_id}", game_resources.ResourceGetGame()) # FET
application.add_route("/user/game/history/{user_id}", game_resources.ResourceGetUserGames()) # FET

#CARD
# put
## application.add_route("/card/{card_id}/upgrade", card_resources.ResourceUpgradeCard())

# get
application.add_route("/card/{card_id}", card_resources.ResourceGetCard()) # FET
application.add_route("/card/image/{card_id}", card_resources.ResourceGetCardImage()) # Falta arreglar per retornar la imatge

# post
application.add_route("/card/set_image/{card_id}", card_resources.ResourceSetImage()) # FET

#STATS
# post (Aquesta funcio es crida a l'hora de crear un nou usuari)
## application.add_route("/stats/create", stats_resources.ResourceCreateUserStats())

# put
application.add_route("/stats/update", stats_resources.ResourceUpdateUserStats())

# get
application.add_route("/stats", stats_resources.ResourceGetUserStats())

#MAP
# get
application.add_route("/map/get", map_resources.ResourceGetRandomMap())

#DECK
# post
application.add_route("/deck/create", deck_resources.ResourceCreateDeck())

# put
application.add_route("/deck/{deck_id}/update", deck_resources.ResourceUpdateDeck())

#get
application.add_route("/deck/{deck_id}", deck_resources.ResourceGetDeck())
application.add_route("/decks", deck_resources.ResourceGetUserDecks())

#ACHIEVEMENTS
# put
application.add_route("/achievement/{achievement_id}/unlock", achievement_resources.ResourceUnlock())

# get
application.add_route("/achievements", achievement_resources.ResourceGetUserAchievements())

#
application.add_sink(handle_404, "")

