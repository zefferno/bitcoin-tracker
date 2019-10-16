import json
import logging
import os
import sqlite3

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from flask import Flask, render_template, g
from waitress import serve


application = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format="[%(asctime)s]: {} %(levelname)s %(message)s".format(os.getpid()),
    datefmt="%Y-%d-%m %H:%M:%S",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()
count = 0
avg = -1
curr = -1
curr_dt = None


def db_collection_task():
    global count
    global avg
    global curr
    global curr_dt

    logging.debug("Collecting BC currency value from API")

    try:
        response = requests.get(Config.BC_TRACKER_URL)
    except requests.exceptions.Timeout:
        logging.error("Timeout reached while trying to fetch data from remote API")
        return
    except requests.exceptions.RequestException as ex:
        logging.error(f"Caught requests exception: {ex}")
        return
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        logging.error("Failed to parse API response")
        return

    try:
        data = data[0]["price_usd"]
        value = float(data)
    except Exception:
        logging.error("Failed to get BC value from JSON response")
        return

    logging.debug(f"BC value: {value}")
    db_store_bc_value(value)

    curr_dt, curr = db_get_bc_values()

    count += 1
    if count >= Config.DB_BC_AVERAGE_TIME:
        avg = db_get_avg(Config.DB_BC_AVERAGE_TIME)

        logging.debug(f"Keeping last {Config.DB_BC_CLEANUP_KEEP_ITEMS} values")
        db_cleanup(Config.DB_BC_CLEANUP_KEEP_ITEMS)
        count = 0
    else:
        avg = -1


def db_cleanup(n):
    with application.app_context():
        db = db_get()
        db.execute(f"DELETE FROM bc WHERE id NOT IN (SELECT id FROM bc ORDER BY datetime DESC LIMIT {n})")
        db.commit()


def db_get():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DB)
    return db


def db_init():
    with application.app_context():
        db = db_get()
        with application.open_resource(Config.DB_SCHEMA, "r") as f:
            db.cursor().executescript(f.read())
        db.commit()


@application.teardown_appcontext
def db_close(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def db_store_bc_value(value):
    with application.app_context():
        db = db_get()
        db.execute("INSERT INTO bc (val) VALUES (?)", [value])
        db.commit()


def db_get_bc_values():
    with application.app_context():
        db = db_get()
        values = db.execute("SELECT datetime, val from bc ORDER BY id DESC LIMIT 1").fetchall()
        if not values:
            logging.debug("Recent values not exist in database")
            return "", ""
        values = values[0]
        return values[0], values[1]


def db_get_avg(n):
    with application.app_context():
        db = db_get()
        db.row_factory = lambda cursor, row: row[0]
        values = db.execute(f"SELECT val from bc ORDER BY id DESC LIMIT {n}").fetchall()
        if not values or len(values) < n:
            logging.debug("Not enough values available to calculate average")
            return -1
        return sum(values) / len(values)


@application.route('/', methods=["GET"])
def index():
    return render_template(
        "index.html",
        bc_value=f"Current BC value: {curr}" if curr != -1 else "",
        bc_average=f"Last {Config.DB_BC_AVERAGE_TIME} minutes average BC value: {avg}" if avg != -1 else "",
        last_refresh=str(curr_dt) if curr_dt else "",
        page_refresh=Config.PAGE_REFRESH, title=Config.APP_NAME
    )


def main():
    global avg
    global curr
    global curr_dt

    logger.info("Initializing configuration")
    application.config.from_object(Config())

    logger.info("Initializing DB")
    db_init()

    logger.info("Initializing job scheduler")
    sched = BackgroundScheduler()
    sched.add_job(db_collection_task, "interval", minutes=Config.DB_BC_COLLECTION_TIME)
    sched.start()

    logger.info("Initializing values from DB")
    curr_dt, curr = db_get_bc_values()
    avg = db_get_avg(Config.DB_BC_AVERAGE_TIME)

    logger.info(f"Running application")
    serve(application, listen=f"*:{Config.TCP_PORT}")


if __name__ == "__main__":
    main()
