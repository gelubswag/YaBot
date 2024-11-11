import sqlite3 as sql
from typing import Any
from cfg import *



def addDish(cursor:sql.Connection,request):
    params = set(request["command"].replace("рублей","").replace(" р", "").replace(" за", "").split()).difference(set(SIMPLE_UTTERANCE["addDish"]["commands"][-1].split()))
    entities = request["nlu"]["entities"]
    print(entities[0]["type"] == "YANDEX.NUMBER" , len(entities))
    if len(entities) < 1:
        return False
    else:
        for entity in entities: 
        
        
            if entity["type"] == "YANDEX.NUMBER":
                cost = entity
                print(entities)
                break
        cost = cost["value"]
    print(params)
    params.remove(str(cost))
    
    dishname = ""
    for i in request["command"].split():
        if i in params:
            dishname += i + " "
    dishname = dishname[:-1]
    querry = f"INSERT INTO Menu VALUES(\"{dishname}\", {cost})"
    cursor1 = cursor.cursor()
    cursor1.execute(querry)
    cursor1.close()
    return True

def getDishes(cursor:sql.Connection):
    cursor1 = cursor.cursor()
    querry = "SELECT * FROM Menu"
    dishes = cursor1.execute(querry).fetchall()
    cursor1.close()
    return dishes

def menu(cursor:sql.Connection, request):
    dishes = getDishes(cursor)
    st = "\n"
    for dish in dishes:
        st += dish[0].capitalize() + " за " + str(dish[1]) + " руб.\n"
    return st


DBMETHODS = {
    "addDish": addDish,
    "menu" : menu,
    }