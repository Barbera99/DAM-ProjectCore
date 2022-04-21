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
application.add_route("/users/register", user_resources.ResourceRegisterUser())

# get
application.add_route("/user/{username}", user_resources.ResourceGetUserProfile())

# put
application.add_route("/user/{username}/profile/update", user_resources.ResourceUpdateUserProfile()) ## Preguntar a DIDAC
application.add_route("/user/{username}/unsubscribe", user_resources.ResourceUserUnsubscribe())

# delete
application.add_route("/user/{username}/delete", user_resources.ResourceUserDelete())

#GAME
# post
application.add_route("/game/start", game_resources.ResourceStartGame())

# put
application.add_route("/game/{game_id}/end", game_resources.ResourceEndGame())

# get
application.add_route("/game/{game_id}/show", game_resources.ResourceGetGame())
application.add_route("/game/history", game_resources.ResourceGetUserGames()) ## Preguntar a DIDAC

#CARD
# put
application.add_route("/card/{card_id}/upgrade", card_resources.ResourceUpgradeCard())

# get
application.add_route("/card/{card_id}/stats/{username}", card_resources.ResourceGetCardStats())
application.add_route("/card/{card_id}/image", card_resources.ResourceGetCardImage()) ## Preguntar a DIDAC

#STATS
# post
application.add_route("/stats/create", stats_resources.ResourceCreateUserStats())

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

