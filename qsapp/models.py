from flask import current_app as app
from flask_caching import Cache
import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import pandas as pd
import requests
import myfitnesspal
import os
from dotenv import load_dotenv
import datetime
import logging.config

load_dotenv()
cache = Cache(app)

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module models.py loaded")

# SQLAlchemy connection & Base
mysql_login = app.config["MYSQL_LOGIN"]
mysql_password = app.config["MYSQL_PASSWORD"]
mysql_url = app.config["MYSQL_URL"]
url = f"mysql+pymysql://{mysql_login}:{mysql_password}@{mysql_url}"
engine = db.create_engine(url, echo=False)
connection = engine.connect()
metadata = db.MetaData(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    __table_args__ = {'autoload': True}

    @classmethod
    @cache.memoize(3600)
    def load_df(cls):
        logger.debug(f"Table name: {cls.__tablename__} - Started reading")
        df = pd.read_sql_table(cls.__tablename__, con=engine)
        logger.debug(f"Table name: {cls.__tablename__} - Finished reading")
        return df

    @classmethod
    def get_last_date(cls):
        logger.debug(f"Table name: {cls.__tablename__} - Started reading 'get_last_date'")
        q = session.query(func.max(cls.date)).scalar()
        logger.debug(f"Table name: {cls.__tablename__} - Finished reading 'get_last_date'")
        return q

Base = declarative_base(cls=Base)


# TODO Dodělat enddate jako nepovinný parametr
def withings_daily_summary(startdate):
    headers = {'Authorization': 'Bearer ' + os.environ['TOKEN_WITHINGS']}

    meastypes = {"1": "weight", "5": "fat_free_mass", "6": "fat_ratio", "8": "fat_mass_weight",
                 "76": "muscle_mass", "77": "hydration", "88": "bone_mass", "71": "body_temperature",
                 "9": "distolic", "10": "systolic", "11": "heart_pulse", "12": "temperature",
                 "73": "skin_temperature", "4": "height"
                 }
    payload = {'action': 'getmeas',
               "category": "1",
               # From date to unix format
               "startdate": datetime.datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S").timestamp()
               }
    r_getmeas = requests.get('https://wbsapi.withings.net/measure', headers=headers, params=payload).json()

    if "error" in r_getmeas:
        status = str("Withings API error: " + r_getmeas["error"])
        return status
    else:
        measures = r_getmeas["body"]["measuregrps"]
        results = []
        for record in measures:
            day = {}
            result_date = record["date"]
            # From unix to date format
            result_date = datetime.datetime.fromtimestamp(int(result_date)).strftime("%Y-%m-%d")
            day["date"] = result_date

            for result in record["measures"]:
                result_type = meastypes[str(result["type"])]
                real_value = result["value"] * (10 ** result["unit"])
                day[result_type] = round(real_value, 4)

            results.append(day)
        results.reverse()
        return results


class Body(Base):
    __tablename__ = "body"
    metadata = metadata

    @classmethod
    def body_insert(cls, date):
        import_data = withings_daily_summary(date)
        row_count = 0
        for i in import_data:
            if "weight" in i:  # assert that those are only scale measurements
                q = session.execute(db.insert(cls, values=i, prefixes=["IGNORE"]))
                row_count = row_count + q.rowcount
                session.commit()
            else:
                pass
        logger.info("Inserting in table: Body")
        logger.info(f"Attempted insert: {len(import_data)}")
        logger.info(f"Inserted rows: {row_count}")


class Myfitnesspal(Base):
    __tablename__ = "myfitnesspal"
    metadata = metadata

    @classmethod
    # TODO - split to two functions - download data & insert to db
    def myfitnesspal_insert(cls, startdate, enddate):
        mfp_user = os.getenv("MYFITNESSPAL_USER")
        mfp_pass = os.getenv("MYFITNESSPAL_PASS")
        client = myfitnesspal.Client(mfp_user, password=mfp_pass)
        startdate = datetime.datetime.strptime(startdate, "%d-%m-%Y")
        enddate = datetime.datetime.strptime(enddate, "%d-%m-%Y")
        date_generated = [startdate + datetime.timedelta(days=x) for x in range(0, (enddate - startdate).days + 1)]
        mfp_results = []
        for date in date_generated:
            day = client.get_date(date)
            for x in day.meals:
                for i in x.entries:
                    entry = i.name.replace("\xa0", " ")
                    totals = i.totals
                    totals["entry"] = entry
                    totals["meal"] = x.name
                    totals["date"] = datetime.datetime.strftime(date, "%Y-%m-%d")
                    mfp_results.append(totals)
        row_count = 0
        for i in mfp_results:
            q = session.execute(db.insert(cls, values=i, prefixes=["IGNORE"]))
            row_count = row_count + q.rowcount
            session.flush()
        session.commit()
        logger.info(f"Inserting in table: {cls.__tablename__}")
        logger.info(f"Attempted insert: {len(mfp_results)}")
        logger.info(f"Inserted rows: {row_count}")

# Myfitnesspal.myfitnesspal_insert("01-01-2020", "14-12-2020")


class Total_Energy(Base):
    __tablename__ = "total_energy"
    metadata = metadata
    date = Column(primary_key=True)