from flask import Flask, request, jsonify
app = Flask(__name__)


DB = {
    "host": "cis2368fall.ctak0ym0ghom.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "password": "Iamawesome99!",
    "database": "cars"
}

def db_conn():
    return mysql.connector.connect(**DB)

# adds a new car
@app.post("/car")
def add_car():
    data = request.get_json()
    try:
        conn = db_conn()
        cur = conn.cursor()
        sql = """
        INSERT INTO cars (make, model, color, year, costperday, renter)
        VALUES (%s, %s, %s, %s, %s, NULL)
        """
        cur.execute(sql, (
            data["make"], data["model"], data["color"],
            int(data["year"]), float(data["costperday"])
        ))
        conn.commit()
        new_id = cur.lastrowid
        cur.close(); conn.close()
        return jsonify({"message": "car added", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# rent or return a car
@app.put("/car")
def rent_or_return():
    data = request.get_json()
    car_id = int(data["id"])
    renter = data.get("renter", None)  # None means return the car

    try:
        conn = db_conn()
        cur = conn.cursor()
        if renter:  # rent it out
            cur.execute("UPDATE cars SET renter=%s WHERE id=%s", (renter, car_id))
        else:       # return it
            cur.execute("UPDATE cars SET renter=NULL WHERE id=%s", (car_id,))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"message": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# returns available cars and daily revenue from rented cars
@app.get("/cars")
def get_available_and_revenue():
    try:
        conn = db_conn()
        cur = conn.cursor(dictionary=True)

        # available = cars with renter IS NULL
        cur.execute("SELECT id, make, model, color, year, costperday FROM cars WHERE renter IS NULL")
        available = cur.fetchall()

        # revenue = sum of costperday for cars with renter IS NOT NULL
        cur.execute("SELECT COALESCE(SUM(costperday), 0) AS revenue FROM cars WHERE renter IS NOT NULL")
        daily_revenue = float(cur.fetchone()["revenue"])

        cur.close(); conn.close()
        return jsonify({"available_cars": available, "daily_revenue": daily_revenue})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)

