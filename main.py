from flask import Flask, request, render_template,redirect
from flask_tunnel import FlaskTunnel
from cfg import *
from methods import *
app = Flask(__name__)

def reload():
    with open("cfg.yaml", "r", encoding="utf-8") as f: CFG = safe_load(f)
    EVENTS = CFG["events"]
    TRIGGERS = CFG["triggers"]
    SIMPLE_UTTERANCE = TRIGGERS["SimpleUtterance"]
    
    return (EVENTS, TRIGGERS, SIMPLE_UTTERANCE)

FlaskTunnel(app,"2n1fEInAGQykJ38WNfhFj2eLpYA_5GZFrQ243SMxtzANNxcBC")

def SUfindEvent(trigger):
    reload()
    try:
        max_len = 0
        for key, val in SIMPLE_UTTERANCE.items():
            for sent in val["commands"]:
                l = len(set(trigger["command"].split()).intersection(set(sent.split())))
                if l > max_len:
                    name = key
                    event = EVENTS[name]
                    max_len = l
        if max_len/len(SIMPLE_UTTERANCE[name]["commands"][-1].split())  < 0.7:
            print(1, max_len/len(SIMPLE_UTTERANCE[name]["commands"][-1].split()))
            event = EVENTS["error"]
            name = "error"
    except Exception as ex:
        print(ex)
        event = EVENTS["error"]
        name = "error"
    return (name, event)

@app.route('/', methods=["GET","POST"])
def mainpage():
    if request.method == "GET":
        con = sql.connect(DB)
        dishes = getDishes(con)
        con.close()
        return render_template("index.html", dishes=dishes)
    else:
        dishname, cost = request.form.get("dishname"), request.form.get("cost", type=float)
        con = sql.connect(DB)
        
        try:
            print(dishname)
            cur = con.cursor()
            cur.execute(f"INSERT INTO Menu VALUES (\"{dishname}\", {cost})")
            con.commit()
            cur.close()
            dishes = getDishes(con)
            con.close()
        except Exception as ex:
            dishes = getDishes(con)
            con.close()
            return redirect("/")
        return redirect("/")
    
@app.route('/webhook', methods=['POST',"GET"])
def webhook():
    
    try: 
        con.close()
        con = sql.connect(DB)
    except: pass
    reload()
    if request.method == 'POST':
        response = {
            "version": "1.0",
        }
        session = request.json["session"]
        
        # Приветствующее сообщение
        if session["new"]:
            response["response"] = EVENTS["start"]
            return response, 200
        
        else:
            
            # Проверка на голосовой/текстовый запрос
            if request.json["request"]["type"] == "SimpleUtterance":
                trigger = request.json["request"]
                
                name, event = SUfindEvent(trigger)
                if name in DBMETHODS.keys():
                    try:
                        con = sql.connect(DB)
                        flg = DBMETHODS[name](con,trigger)
                        print(flg)
                        if flg:
                            response["response"] = event
                            
                            if name == "menu":
                                if not(flg in response["response"]["text"]):
                                    response["response"] ={ "text": EVENTS["menu"]["text"] + flg, "tts": EVENTS["menu"]["tts"] + flg}
                                    con.commit()
                                    con.close()
                                    return response, 200
                            
                        else:
                            response["response"] = EVENTS["error"]
                        con.commit()
                        con.close()
                        return response, 200
                        
                    except Exception as ex:
                        print(ex)
                        response["response"] = EVENTS["error"]  
                        con.close()
                        return response, 200
                response["response"] = event
                return response, 200

            
        # Print the received JSON data to the console
        # print(request.json["request"])
        # print(request.json["session"])
        # return 0, 200
        # return request.json["request"]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)