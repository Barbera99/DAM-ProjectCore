#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config

import falcon

import messages
import middlewares
from falcon_multipart.middleware import MultipartMiddleware
from resources import account_resources, common_resources, user_resources, game_resources
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
application.add_route("/{username}", user_resources.ResourceGetUserProfile())
# put
application.add_route("/{username}/profile/update", user_resources.ResourceUpdateUserProfile)
application.add_route("/{username}/unsubscribe", user_resources.ResourceUserUnsubscribe)
# delete
application.add_route("/{username}/delete", user_resources.ResourceUserDelete)

#GAME
# post
application.add_route("/game/start", game_resources.ResourceStartGame)

# put
application.add_route("/{game_id}/end", game_resources.ResourceStartGame)

# get
application.add_route("/{game_id}/show", game_resources.ResourceGetGame())
application.add_route("/{user_id}/games", game_resources.ResourceGetUserGames())

#CARD
# put

# get


#STATS
# post

# put

# get


#MAP
# get

#DECK
# post

# put

#get


#ACHIEVEMENTS
# put

# get

#

application.add_sink(handle_404, "")

