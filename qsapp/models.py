from flask import current_app as app
import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import pandas as pd
import requests
import myfitnesspal
import os
from dotenv import load_dotenv
import time
import ciso8601
import datetime
import logging.config

load_dotenv()

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
    def load_df(cls):
        logger.debug(f"Table name: {cls.__tablename__} - Started reading")
        df = pd.read_sql_table(cls.__tablename__, con=engine)
        logger.debug(f"Table name: {cls.__tablename__} - Finished reading")
        return df


Base = declarative_base(cls=Base)


# TODO Dodělat enddate jako nepovinný parametr
def withings_daily_summary(startdate):
    headers = {'Authorization': 'Bearer ' + os.environ['TOKEN_WITHINGS']}

    def date_to_unix(date):
        ts = ciso8601.parse_datetime(date)
        return time.mktime(ts.timetuple())

    def unix_to_date(unix):
        unix = int(float(unix))
        return datetime.datetime.utcfromtimestamp(unix).strftime('%Y-%m-%d')

    meastypes = {"1": "weight", "5": "fat_free_mass", "6": "fat_ratio", "8": "fat_mass_weight",
                 "76": "muscle_mass", "77": "hydration", "88": "bone_mass", "71": "body_temperature",
                 "9": "distolic", "10": "systolic", "11": "heart_pulse", "12": "temperature",
                 "73": "skin_temperature", "4": "height"
                 }
    payload = {'action': 'getmeas',
               "category": "1",
               "startdate": date_to_unix(startdate)
               }
    r_getmeas = requests.get('https://wbsapi.withings.net/measure', headers=headers, params=payload).json()

    try:
        status = str("Withings API error: " + r_getmeas["error"])
        return status
    except:
        measures = r_getmeas["body"]["measuregrps"]
        results = []
        for date in measures:
            day = {}
            result_date = date["date"]
            result_date = unix_to_date(result_date)
            day["date"] = result_date

            for result in date["measures"]:
                result_value = result["value"]
                result_type = result["type"]
                result_type = meastypes[str(result_type)]
                result_unit = result["unit"]
                real_value = result_value * (10 ** result_unit)
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
        print("Inserting in table: Body")
        print(f"Attempted insert: {len(import_data)}")
        print(f"Inserted rows: {row_count}")


class Myfitnesspal(Base):
    __tablename__ = "myfitnesspal"
    metadata = metadata

    @classmethod
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
        print(f"Inserting in table: {cls.__tablename__}")
        print(f"Attempted insert: {len(mfp_results)}")
        print(f"Inserted rows: {row_count}")

# Myfitnesspal.myfitnesspal_insert("01-01-2020", "14-12-2020")


class Total_Energy(Base):
    __tablename__ = "total_energy"
    metadata = metadata
    date = Column(primary_key=True)
