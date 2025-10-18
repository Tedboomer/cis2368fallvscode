from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# RDS CONFIG
DB_HOST = "cis2368fall.ctak0ym0ghom.us-east-2.rds.amazonaws.com"
DB_PORT = 3306
DB_NAME = "cis2368fall"
DB_USER = "admin"
DB_PASS = "Iamawesome99!"

def conn():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS,
        database=DB_NAME, autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

def q(sql, args=(), one=False):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(sql, args)
            if sql.strip().upper().startswith(("INSERT","UPDATE","DELETE","CREATE","DROP","ALTER")):
                # autocommit=True, nothing to fetch for writes
                if sql.strip().upper().startswith("INSERT"):
                    return {"id": cur.lastrowid}
                return {"ok": True}
            rows = cur.fetchone() if one else cur.fetchall()
            return rows

# BOOTSTRAP: make tables and sample if empty
def bootstrap():
    q("""CREATE TABLE IF NOT EXISTS recipe(
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            instructions TEXT
        )""")
    q("""CREATE TABLE IF NOT EXISTS ingredient(
            id INT PRIMARY KEY AUTO_INCREMENT,
            ingredientname VARCHAR(255) NOT NULL,
            totalamount INT NOT NULL DEFAULT 0
        )""")
    q("""CREATE TABLE IF NOT EXISTS recipeingredient(
            id INT PRIMARY KEY AUTO_INCREMENT,
            recipeid INT NOT NULL,
            ingredientid INT NOT NULL,
            amount INT NOT NULL,
            FOREIGN KEY (recipeid) REFERENCES recipe(id),
            FOREIGN KEY (ingredientid) REFERENCES ingredient(id)
        )""")

    count = q("SELECT COUNT(*) AS n FROM ingredient", one=True)["n"]
    if count == 0:
        egg_id = q("INSERT INTO ingredient(ingredientname,totalamount) VALUES(%s,%s)", ("eggs", 6))["id"]
        flour_id = q("INSERT INTO ingredient(ingredientname,totalamount) VALUES(%s,%s)", ("flour", 100))["id"]
        rid = q("INSERT INTO recipe(name,instructions) VALUES(%s,%s)", ("pancakes", "mix & fry"))["id"]
        q("INSERT INTO recipeingredient(recipeid,ingredientid,amount) VALUES(%s,%s,%s)", (rid, egg_id, 2))
        q("INSERT INTO recipeingredient(recipeid,ingredientid,amount) VALUES(%s,%s,%s)", (rid, flour_id, 20))

bootstrap()

# INGREDIENTS
@app.get("/ingredients")
def ing_list():
    return jsonify(q("SELECT id, ingredientname, totalamount FROM ingredient"))

@app.post("/ingredients")
def ing_add():
    d = request.get_json() or {}
    r = q("INSERT INTO ingredient(ingredientname,totalamount) VALUES(%s,%s)",
          (d.get("ingredientname",""), int(d.get("totalamount",0))))
    return jsonify(r), 201

@app.put("/ingredients/<int:iid>")
def ing_upd(iid):
    d = request.get_json() or {}
    if "ingredientname" in d:
        q("UPDATE ingredient SET ingredientname=%s WHERE id=%s", (d["ingredientname"], iid))
    if "totalamount" in d:
        q("UPDATE ingredient SET totalamount=%s WHERE id=%s", (int(d["totalamount"]), iid))
    return jsonify({"ok": True})

@app.delete("/ingredients/<int:iid>")
def ing_del(iid):
    q("DELETE FROM ingredient WHERE id=%s", (iid,))
    return jsonify({"ok": True})

# RECIPES
@app.get("/recipes")
def rec_list():
    return jsonify(q("SELECT id, name, instructions FROM recipe"))

@app.post("/recipes")
def rec_add():
    d = request.get_json() or {}
    r = q("INSERT INTO recipe(name,instructions) VALUES(%s,%s)",
          (d.get("name",""), d.get("instructions","")))
    return jsonify(r), 201

@app.put("/recipes/<int:rid>")
def rec_upd(rid):
    d = request.get_json() or {}
    if "name" in d:
        q("UPDATE recipe SET name=%s WHERE id=%s", (d["name"], rid))
    if "instructions" in d:
        q("UPDATE recipe SET instructions=%s WHERE id=%s", (d["instructions"], rid))
    return jsonify({"ok": True})

@app.delete("/recipes/<int:rid>")
def rec_del(rid):
    q("DELETE FROM recipeingredient WHERE recipeid=%s", (rid,))
    q("DELETE FROM recipe WHERE id=%s", (rid,))
    return jsonify({"ok": True})

# LINKS BETWEEN RECIPES & INGREDIENTS
@app.get("/recipeingredients")
def link_list():
    return jsonify(q("SELECT id, recipeid, ingredientid, amount FROM recipeingredient"))

@app.post("/recipeingredients")
def link_add():
    d = request.get_json() or {}
    r = q("INSERT INTO recipeingredient(recipeid,ingredientid,amount) VALUES(%s,%s,%s)",
          (int(d["recipeid"]), int(d["ingredientid"]), int(d["amount"])))
    return jsonify(r), 201

@app.put("/recipeingredients/<int:lid>")
def link_upd(lid):
    d = request.get_json() or {}
    if "recipeid" in d:
        q("UPDATE recipeingredient SET recipeid=%s WHERE id=%s", (int(d["recipeid"]), lid))
    if "ingredientid" in d:
        q("UPDATE recipeingredient SET ingredientid=%s WHERE id=%s", (int(d["ingredientid"]), lid))
    if "amount" in d:
        q("UPDATE recipeingredient SET amount=%s WHERE id=%s", (int(d["amount"]), lid))
    return jsonify({"ok": True})

@app.delete("/recipeingredients/<int:lid>")
def link_del(lid):
    q("DELETE FROM recipeingredient WHERE id=%s", (lid,))
    return jsonify({"ok": True})

# CHECK & COOK
@app.get("/recipes/<int:rid>/can_cook")
def can_cook(rid):
    rows = q("""
        SELECT i.ingredientname AS name, i.totalamount AS have, ri.amount AS need
        FROM recipeingredient ri
        JOIN ingredient i ON i.id = ri.ingredientid
        WHERE ri.recipeid = %s
    """, (rid,))
    missing = [dict(ingredient=x["name"], have=x["have"] or 0, need=x["need"])
               for x in rows if (x["have"] or 0) < x["need"]]
    return jsonify({"ok": len(missing) == 0, "missing": missing})

@app.post("/recipes/<int:rid>/cook")
def cook(rid):
    rows = q("""
        SELECT i.id AS iid, i.totalamount AS have, ri.amount AS need
        FROM recipeingredient ri
        JOIN ingredient i ON i.id = ri.ingredientid
        WHERE ri.recipeid = %s
    """, (rid,))
    if any((x["have"] or 0) < x["need"] for x in rows):
        return jsonify({"ok": False, "msg": "not enough ingredients"}), 400
    # deduct
    for x in rows:
        q("UPDATE ingredient SET totalamount=%s WHERE id=%s", (x["have"] - x["need"], x["iid"]))
    return jsonify({"ok": True, "msg": "cooked"})

if __name__ == "__main__":
    
    app.run(host="127.0.0.1", port=5000, debug=True)
