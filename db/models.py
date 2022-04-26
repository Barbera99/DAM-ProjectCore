#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import enum
import logging
import os
from builtins import getattr
from urllib.parse import urljoin

import falcon
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Unicode, \
    UnicodeText, Table, type_coerce, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable

import messages
from db.json_model import JSONModel
import settings

mylogger = logging.getLogger(__name__)

SQLAlchemyBase = declarative_base()
make_translatable(options={"locales": settings.get_accepted_languages()})


def _generate_media_url(class_instance, class_attibute_name, default_image=False):
    class_base_url = urljoin(urljoin(urljoin("http://{}".format(settings.STATIC_HOSTNAME), settings.STATIC_URL),
                                     settings.MEDIA_PREFIX),
                             class_instance.__tablename__ + "/")
    class_attribute = getattr(class_instance, class_attibute_name)
    if class_attribute is not None:
        return urljoin(urljoin(urljoin(urljoin(class_base_url, class_attribute), str(class_instance.id) + "/"),
                               class_attibute_name + "/"), class_attribute)
    else:
        if default_image:
            return urljoin(urljoin(class_base_url, class_attibute_name + "/"), settings.DEFAULT_IMAGE_NAME)
        else:
            return class_attribute


def _generate_media_path(class_instance, class_attibute_name):
    class_path = "/{0}{1}{2}/{3}/{4}/".format(settings.STATIC_URL, settings.MEDIA_PREFIX, class_instance.__tablename__,
                                              str(class_instance.id), class_attibute_name)
    return class_path


# Enums
class GenereEnum(enum.Enum):
    male = "M"
    female = "F"


class CategoryEnum(enum.Enum):
    legendary = "L"
    epic = "E"
    rare = "R"
    common = "C"

# Taules intermèdies de les relacions N a N.
User_Achievement = Table("User_Achievements", SQLAlchemyBase.metadata,
                          Column("achievement_id", Integer,
                                 ForeignKey("achievements.id", onupdate="CASCADE", ondelete="CASCADE"),
                                 nullable=False),
                          Column("user_id", Integer,
                                 ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
                                 nullable=False),
                          )

Games_Map = Table("Games_Maps", SQLAlchemyBase.metadata,
                   Column("id_game", Integer,
                          ForeignKey("games.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   Column("id_map", Integer,
                          ForeignKey("maps.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   )

class User_Card_Association(SQLAlchemyBase, JSONModel):
    __tablename__ = "user_card_association"
    exp = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key = True)
    user_association_card = relationship("User", back_populates="user_cards")
    card_id = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key = True)
    card_association_user = relationship("Card", back_populates="cards_user")

class User_Game_Association(SQLAlchemyBase, JSONModel):
    __tablename__ = "user_game_association"
    score = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key = True)
    user_association_game = relationship("User", back_populates="user_games")
    game_id = Column(Integer, ForeignKey("games.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, primary_key = True)
    game_association_user = relationship("Game", back_populates="games_user")

    def json_model(self):
        return {
            "score": self.score,
            "user_id": self.user_id,
            "game_id": self.game_id
        }

class Game(SQLAlchemyBase, JSONModel):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)

    # Relacio N a N entre Games i User_Games_Association
    games_user = relationship("User_Game_Association", back_populates="game_association_user", cascade="all, delete-orphan")

    # Relació N a N entre Games i Maps.
    games_maps = relationship("Map", secondary=Games_Map, back_populates="maps_games")

    # TODO: Modifiqueu aquest part amb els nous canvis
    @hybrid_property
    def json_game(self, user1, user2, score1, score2):
        return {
            "id": self.id,
            "date": self.date,
            "user1": user1,
            "score1": score1,
            "user2": user2,
            "score2": score2
        }

class User(SQLAlchemyBase, JSONModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    username = Column(Unicode(50), nullable=False, unique=True)
    password = Column(UnicodeText, nullable=False)
    email = Column(Unicode(255), nullable=False)
    name = Column(Unicode(50), nullable=False)
    surname = Column(Unicode(50), nullable=False)
    birthdate = Column(Date)
    genere = Column(Enum(GenereEnum), nullable=True)
    phone = Column(Unicode(50))
    photo = Column(Unicode(255))
    rank_id = Column(Integer, ForeignKey("ranks.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    status = Column(Unicode(20))

    # Relació 1 a N entre Rank i Users
    users_rank = relationship("Rank", back_populates="rank_users")

    # Relació 1 a N entre User i UserToken.
    user_tokens = relationship("UserToken", back_populates="tokens_user", cascade="all, delete-orphan")
    
    # Relació 1 a 1 entre User i Stats.
    user_stats = relationship("Stats", uselist=False, back_populates="stats_user")

    # Relació N a N entre User i Achievements.
    users_achievements = relationship("Achievement", secondary="User_Achievements", back_populates="achievements_users")

    # Relació 1 a N entre User i Deck.
    user_decks = relationship("Deck", back_populates="decks_user", cascade="all, delete-orphan")

    # Relació N a N entre User i User_Game_Association
    user_games = relationship("User_Game_Association", back_populates="user_association_game", cascade="all, delete-orphan")
    
    # Relació N a N entre User i User_Card_Association
    user_cards = relationship("User_Card_Association", back_populates="user_association_card", cascade="all, delete-orphan")
    
    @hybrid_property
    def public_profile(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "birthdate": self.birthdate.strftime("%Y-%m-%d"),
            "photo": self.photo,
            "rank_id": self.rank_id
        }

    @hybrid_property
    def photo_url(self):
        return _generate_media_url(self, "photo")

    @hybrid_property
    def photo_path(self):
        return _generate_media_path(self, "photo")

    @hybrid_method
    def set_password(self, password_string):
        self.password = pbkdf2_sha256.hash(password_string)

    @hybrid_method
    def check_password(self, password_string):
        return pbkdf2_sha256.verify(password_string, self.password)

    @hybrid_method
    def create_token(self):
        if len(self.tokens) < settings.MAX_USER_TOKENS:
            token_string = binascii.hexlify(os.urandom(25)).decode("utf-8")
            aux_token = UserToken(token=token_string, user=self)
            return aux_token
        else:
            raise falcon.HTTPBadRequest(title=messages.quota_exceded, description=messages.maximum_tokens_exceded)

    @hybrid_property
    def json_model(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "birthdate": self.birthdate.strftime(
                settings.DATE_DEFAULT_FORMAT) if self.birthdate is not None else self.birthdate,
            "genere": self.genere.value,
            "phone": self.phone,
            "photo": self.photo_url
        }

# Classes i JSON de la nostra BDD.
class UserToken(SQLAlchemyBase):
    __tablename__ = "users_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Unicode(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    tokens_user  = relationship("User", back_populates="user_tokens")

class Rank(SQLAlchemyBase, JSONModel):
    __tablename__ = "ranks"
    id = Column(Integer, primary_key=True)
    league = Column(Unicode(50), nullable=False, unique=True)
    min_medals = Column(Integer, nullable=False)
    max_medals = Column(Integer, nullable=False)

    # Relació 1 a N entre Rank i Users 
    rank_users = relationship("User", back_populates="users_rank",cascade="all, delete-orphan")

    @hybrid_property
    def json_model(self):
        return {
            "league": self.league,
            "min_medals": self.min_medals,
            "max_medals": self.max_medals
        }

class Stats(SQLAlchemyBase, JSONModel):
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    games_Played = Column(Integer, nullable=False)
    ranked_Wins = Column(Integer, nullable=False)
    ranked_Defeats = Column(Integer, nullable=False)
    normal_Wins = Column(Integer, nullable=False)
    normal_Defeats = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    medals = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"))

    # Relació 1 a 1 entre User i Stats.
    stats_user = relationship("User", back_populates="user_stats")

    @hybrid_property
    def json_model(self):
        return {
            "games_Played": self.games_Played,
            "ranked_Wins": self.ranked_Wins,
            "normal_Wins": self.normal_Wins,
            "normal_Defeats": self.normal_Defeats,
            "level": self.level,
            "medals": self.medals,
            "user_id": self.user_id
        }

class Achievement(SQLAlchemyBase, JSONModel):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    description = Column(Unicode(250), nullable=False)
    type = Column(Unicode(50), nullable=False)
    difficulty = Column(Unicode(50), nullable=False)

    # Relació N a N entre Users i Achievements.
    achievements_users = relationship("User", secondary="User_Achievements", back_populates="users_achievements")

    @hybrid_property
    def json_model(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "difficulty": self.difficulty,
        }

class Deck(SQLAlchemyBase, JSONModel):
    __tablename__ = "deck"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)

    # Relació N a 1 entre Deck i User.
    decks_user = relationship("User", back_populates="user_decks")

    # Relació N a N entre Deck i Deck_Card_Association
    deck_cards = relationship("Deck_Card_Association", back_populates="deck_association_card", cascade="all, delete-orphan")

    @hybrid_property
    def json_model(self):
        return {
            "id": self.id,
            "user_id": self.user_id
        }

class Deck_Card_Association(SQLAlchemyBase, JSONModel):
    __tablename__ = "deck_card_association"
    deck_id = Column(Integer,ForeignKey("deck.id", onupdate="CASCADE", ondelete="CASCADE"),nullable=False, primary_key = True)
    deck_association_card = relationship("Deck", back_populates="deck_cards")
    card_id = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"),nullable=False, primary_key = True)
    card_association_deck = relationship("Card", back_populates="cards_deck")

class Card(SQLAlchemyBase, JSONModel):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    strength = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    agility = Column(Integer, nullable=False)
    endurance = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    image = Column(Unicode(255))

    # Relació N a N entre Card i User_Card_Association.
    cards_user = relationship("User_Card_Association", back_populates="card_association_user", cascade="all, delete-orphan")

    # Relació N a N entre Deck i Deck_Card_Association
    cards_deck = relationship("Deck_Card_Association", back_populates="card_association_deck", cascade="all, delete-orphan")

    @hybrid_property
    def image_path(self):
        return _generate_media_path(self, "image")

    @hybrid_property
    def image_url(self):
        return _generate_media_url(self, "image")

    @hybrid_property
    def json_model(self):
        return {
            "name": self.name,
            "strength": self.strength,
            "speed": self.speed,
            "agility": self.agility,
            "endurance": self.endurance,
            "intelligence": self.intelligence,
            "category": self.category.value,
            "image": self.image_url
        }

class Map(SQLAlchemyBase, JSONModel):
    __tablename__ = "maps"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    attribute = Column(Unicode(50), nullable=False)
    extra_attribute = Column(Unicode(50), nullable=True)

    # Relació N a N entre Maps i Games.
    maps_games = relationship("Game", secondary=Games_Map, back_populates="games_maps")

    @hybrid_property
    def json_model(self):
        return {
            "name": self.name,
            "attribute": self.attribute,
            "extra_attribute": self.extra_attribute,
        }
