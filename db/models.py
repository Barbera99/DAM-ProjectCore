#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import enum
import logging
import os
from _operator import and_
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
User_Achievements = Table("User_Achievements", SQLAlchemyBase.metadata,
                          Column("achievement_id", Integer,
                                 ForeignKey("achievements.id", onupdate="CASCADE", ondelete="CASCADE"),
                                 nullable=False),
                          Column("user_id", Integer,
                                 ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
                                 nullable=False),
                          )

Games_Maps = Table("Games_Maps", SQLAlchemyBase.metadata,
                   Column("id_game", Integer,
                          ForeignKey("games.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   Column("id_map", Integer,
                          ForeignKey("maps.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   )

User_Cards = Table("User_Cards", SQLAlchemyBase.metadata,
                   Column("id_user", Integer,
                          ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   Column("id_card", Integer,
                          ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False),
                   )

# Classes i JSON de la nostra BDD.
class UserToken(SQLAlchemyBase):
    __tablename__ = "users_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Unicode(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    tokens_user  = relationship("User", back_populates="user_tokens")

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
    genere = Column(Enum(GenereEnum), nullable=False)
    phone = Column(Unicode(50))
    photo = Column(Unicode(255))
    rank_id = Column(Integer, ForeignKey("ranks.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

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

    # Relació N a N entre User i Card.
    user_card = relationship("Card", secondary=User_Cards)

    @hybrid_property
    def public_profile(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "genere": self.genere.value,
            "photo": self.photo,
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
    name = Column(Integer, nullable=False)
    description = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)

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
    id_card_1 = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)
    id_card_2 = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)
    id_card_3 = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)
    id_card_4 = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)
    id_card_5 = Column(Integer, ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), unique=True, nullable=False)

    # Relació N a 1 entre Deck i User.
    decks_user = relationship("User", back_populates="user_decks")

    # Relació N a 1 entre Deck i Card
    decks_card = relationship("Card", foreign_keys=[id_card_1,id_card_2,id_card_3,id_card_4,id_card_5])

    @hybrid_property
    def json_model(self):
        return {
            "user_id": self.user_id,
            "id_card_1": self.id_card_1,
            "id_card_2": self.id_card_2,
            "id_card_3": self.id_card_3,
            "id_card_4": self.id_card_4,
            "id_card_5": self.id_card_5
        }

class Card(SQLAlchemyBase, JSONModel):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    strength = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    agility = Column(Integer, nullable=False)
    endurance = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)

    # Relació 1 a N entre Card i Deck.
    #card_decks = relationship("Deck", back_populates="deck_cards", cascade="all, delete-orphan")
    
    # Relació N a N entre Card i User.
    card_user = relationship("User", secondary="User_Cards", back_populates="user_card")

    @hybrid_property
    def json_model(self):
        return {
            "name": self.name,
            "strength": self.strength,
            "speed": self.speed,
            "agility": self.agility,
            "endurance": self.endurance,
            "intelligence": self.intelligence,
            "category": self.category
        }

class Game(SQLAlchemyBase, JSONModel):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    player_id_1 = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    player_id_2 = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    score_player_1 = Column(Integer, nullable=False)
    score_player_2 = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)

    # Relació N a N entre Games i Maps.
    games_maps = relationship("Map", secondary=Games_Maps, back_populates="maps_games")

    # Relació 1 a N entre Games i Users
    games_users = relationship("User", back_populates="games", cascade="all,delete-orphan")

    @hybrid_property
    def json_model(self):
        return {
            "player_id_1": self.player_id_1,
            "player_id_2": self.player_id_2,
            "score_player_1": self.score_player_1,
            "score_player_2": self.score_player_2,
            "date": self.date
        }

class Map(SQLAlchemyBase, JSONModel):
    __tablename__ = "maps"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    attribute = Column(Unicode(50), nullable=False)
    extra_attribute = Column(Unicode(50), nullable=True)

    # Relació N a N entre Maps i Games.
    maps_games = relationship("Game", back_populates="games_maps", cascade="all, delete-orphan")

    @hybrid_property
    def json_model(self):
        return {
            "name": self.name,
            "attribute": self.attribute,
            "extra_attribute": self.extra_attribute,
        }