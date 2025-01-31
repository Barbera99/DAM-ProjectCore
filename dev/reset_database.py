#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import os

from sqlalchemy.sql import text

import db
import settings
from db.models import SQLAlchemyBase, User, GenereEnum, UserToken, Rank, Stats, Achievement, Deck, Card, Game, Map, CategoryEnum, Games_Map, User_Achievement, User_Game_Association, Deck_Card_Association
from settings import DEFAULT_LANGUAGE

# LOGGING
mylogger = logging.getLogger(__name__)
settings.configure_logging()


def execute_sql_file(sql_file):
    sql_folder_path = os.path.join(os.path.dirname(__file__), "sql")
    sql_file_path = open(os.path.join(sql_folder_path, sql_file), encoding="utf-8")
    sql_command = text(sql_file_path.read())
    db_session.execute(sql_command)
    db_session.commit()
    sql_file_path.close()


if __name__ == "__main__":
    settings.configure_logging()

    db_session = db.create_db_session()

    # -------------------- REMOVE AND CREATE TABLES --------------------
    mylogger.info("Removing database...")
    SQLAlchemyBase.metadata.drop_all(db.DB_ENGINE)
    mylogger.info("Creating database...")
    SQLAlchemyBase.metadata.create_all(db.DB_ENGINE)

# -------------------- CREATE CARDS --------------------
    mylogger.info("Creating default card_1...")
    card_1 = Card(
        name="Ninja",
        strength=35,
        speed=75,
        agility=90,
        endurance=20,
        intelligence=65,
        category=CategoryEnum.epic
    )

    mylogger.info("Creating default card_2...")
    card_2 = Card(
        name="T-Dummy",
        strength=30,
        speed=30,
        agility=10,
        endurance=95,
        intelligence=0,
        category=CategoryEnum.common
    )

    mylogger.info("Creating default card_3...")
    card_3 = Card(
        name="Sonic",
        strength=10,
        speed=99,
        agility=85,
        endurance=95,
        intelligence=20,
        category=CategoryEnum.legendary
    )

    mylogger.info("Creating default card_4...")
    card_4 = Card(
        name="Linda",
        strength=75,
        speed=40,
        agility=40,
        endurance=40,
        intelligence=30,
        category=CategoryEnum.rare
    )

    mylogger.info("Creating default card_5...")
    card_5 = Card(
        name="G2 Paco",
        strength=40,
        speed=60,
        agility=50,
        endurance=10,
        intelligence=10,
        category=CategoryEnum.rare
    )

    mylogger.info("Creating default card_6...")
    card_6 = Card(
        name="Palomo",
        strength=30,
        speed=60,
        agility=30,
        endurance=60,
        intelligence=0,
        category=CategoryEnum.rare
    )
    mylogger.info("Creating default card_7...")
    card_7 = Card(
        name="Paloma",
        strength=0,
        speed=60,
        agility=30,
        endurance=60,
        intelligence=30,
        category=CategoryEnum.rare
    )
    mylogger.info("Creating default card_8...")
    card_8 = Card(
        name="Godzilla",
        strength=99,
        speed=20,
        agility=10,
        endurance=50,
        intelligence=20,
        category=CategoryEnum.legendary
    )

    mylogger.info("Creating default card_9...")
    card_9 = Card(
        name="R0-B0T",
        strength=50,
        speed=30,
        agility=20,
        endurance=50,
        intelligence=95,
        category=CategoryEnum.rare
    )
    mylogger.info("Creating default card_10...")
    card_10 = Card(
        name="Pato",
        strength=20,
        speed=60,
        agility=60,
        endurance=40,
        intelligence=0,
        category=CategoryEnum.common
    )
    mylogger.info("Creating default card_11...")
    card_11 = Card(
        name="Shrek",
        strength=90,
        speed=20,
        agility=20,
        endurance=75,
        intelligence=30,
        category=CategoryEnum.epic
    )
    mylogger.info("Creating default card_12...")
    card_12 = Card(
        name="Flash",
        strength=30,
        speed=80,
        agility=75,
        endurance=30,
        intelligence=30,
        category=CategoryEnum.rare
    )
# -------------------- CREATE ACHIEVEMENTS --------------------
    mylogger.info("Creating default achievements...")
    achievement_1 = Achievement(
        name="Welcome",
        description="Entrar al joc per primer cop.",
        type="",
        difficulty=5
    )


 # -------------------- CREATE USERS --------------------
    mylogger.info("Creating default users...")

    # noinspection PyArgumentList
    ia = User(
        # created_at=datetime.datetime.now(),
        username="IA Bot",
        email="iabot@gmail.com",
        name="IABot",
        surname="Bot",
        birthdate=datetime.datetime(1789, 1, 1),
        genere=GenereEnum.male,
        phone='678954327',
        photo="foto_perfil_1.png",
        rank_id=1,
        users_achievements=[achievement_1],
        status="active"
    )
    ia.set_password("a1s2d3f4")
    # ia.tokens.append(UserToken(token="656e50e154865a5dc469b80437ed2f963b8f58c8857b66c9bf"))


    # noinspection PyArgumentList
    user_1= User(
        #created_at=datetime.datetime.now(),
        username="usuari1",
        email="usuari1@gmail.com",
        name="usuari",
        surname="1",
        birthdate=datetime.datetime(1989, 1, 1),
        genere=GenereEnum.male,
        phone='678954327',
        photo="foto_perfil_1.png",
        rank_id=1,
        users_achievements = [achievement_1],
        status = "active"

    )
    user_1.set_password("1234")
    #user_1.tokens.append(UserToken(token="656e50e154865a5dc469b80437ed2f963b8f58c8857b66c9bf"))

    # noinspection PyArgumentList
    user_2 = User(
        #created_at=datetime.datetime.now(),
        username="usuari2",
        email="user2@gmail.com",
        name="user",
        surname="2",
        birthdate=datetime.datetime(2017, 1, 1),
        genere=GenereEnum.male,
        phone='687324521',
        photo="foto_perfil_2.png",
        rank_id=1,
        users_achievements=[achievement_1],
        status = "active"

    )
    user_2.set_password("r45tgt")
    #user_2.tokens.append(UserToken(token="0a821f8ce58965eadc5ef884cf6f7ad99e0e7f58f429f584b2"))

    # -------------------- CREATE RANKS --------------------
    mylogger.info("Creating default ranks...")
    rank = Rank(
        league="Silver",
        min_medals=300,
        max_medals=500
    )

    # -------------------- CREATE MAP --------------------
    map1 = Map(
        name="Mapa1",
        attribute='atrr2',
        extra_attribute='extra_atrtr',

    )

    # -------------------- CREATE GAME --------------------
    mylogger.info("Creating default game...")
    game1 = Game(
        id = 1,
        date = datetime.datetime.now(),
        games_maps = [map1]
    )

    # -------------------- CREATE GAME --------------------
    mylogger.info("Creating default game...")
    game2 = Game(
        id = 2,
        date = datetime.datetime.now(),
        games_maps = [map1]
    )

    # Partida entre user 1 i 2 en un game 1
    game_user_association1 = User_Game_Association(
        user_association_game = user_1,
        game_association_user = game1,
        score = 90
    )

    game_user_association2 = User_Game_Association(
        user_association_game = user_2,
        game_association_user = game1,
        score = 110
    )

    # Partida entre user 1 i 2 en un game 2
    game_user_association3 = User_Game_Association(
        user_association_game = user_1,
        game_association_user = game2,
        score = 90
    )

    game_user_association4 = User_Game_Association(
        user_association_game = user_2,
        game_association_user = game2,
        score = 110
    )



    # -------------------- CREATE DECK --------------------
    mylogger.info("Creating default deck...")
    deck = Deck(
        user_id=1,
        created_at = datetime.datetime.now(),
    )

    # -------------------- CREATE Deck_Card_Association --------------------
    mylogger.info("Creating default Deck_Card_Association...")
    deck_card_Association_1 = Deck_Card_Association(
        deck_id = 1,
        card_id = 1
    )

    deck_card_Association_2 = Deck_Card_Association(
        deck_id=1,
        card_id=2
    )

    deck_card_Association_3 = Deck_Card_Association(
        deck_id=1,
        card_id=3
    )

    deck_card_Association_4 = Deck_Card_Association(
        deck_id=1,
        card_id=4
    )

    deck_card_Association_5 = Deck_Card_Association(
        deck_id=1,
        card_id=5
    )
    # -------------------- CREATE STATS --------------------
    mylogger.info("Creating default stats...")
    stats = Stats(
        games_Played=25,
        ranked_Wins=10,
        ranked_Defeats=5,
        normal_Wins=5,
        normal_Defeats=5,
        level=5,
        medals=400,
        stats_user=user_1
    )


    # -------------------- CREATE MAP --------------------
    mylogger.info("Creating default map...")
    map = Map(
        name = "Marathon",
        attribute ="speed" ,
        extra_attribute = "endurance"
    )


    # ---------------- AFEGIR LES DADES EN ORDRE DEGUT A LES RELACIONS -------------- #
    mylogger.info("Inserint dades")
    db_session.add(ia)
    db_session.add(user_1)
    db_session.add(user_2)
    db_session.add(rank)
    db_session.add(map1)
    db_session.add(game1)
    db_session.add(game2)
    db_session.add(game_user_association1)
    db_session.add(game_user_association2)
    db_session.add(game_user_association3)
    db_session.add(game_user_association4)
    db_session.add(card_1)
    db_session.add(card_2)
    db_session.add(card_3)
    db_session.add(card_4)
    db_session.add(card_5)
    db_session.add(deck)
    db_session.add(deck_card_Association_1)
    db_session.add(deck_card_Association_2)
    db_session.add(deck_card_Association_3)
    db_session.add(deck_card_Association_4)
    db_session.add(deck_card_Association_5)
    db_session.add(stats)
    db_session.commit()
    db_session.close()
