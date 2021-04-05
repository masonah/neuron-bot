import os
from os.path import join, dirname
from dotenv import load_dotenv
# from mysql.connector import connect, Error
from application.routes import app
from flask_sqlalchemy import SQLAlchemy
from .models import db, User

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    # username=os.environ.get("SECRET_KEY"),
    username=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    hostname=os.environ.get("DB_HOST"),
    databasename=os.environ.get("DB_NAME"),
)

# DB_USER = os.environ.get("SECRET_KEY")
# DB_PASSWORD = os.environ.get("DATABASE_PASSWORD")

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class DBInterface(object):

    def __init__(self):
        super(DBInterface, self).__init__()
        # self.connection = self.create_server_connection()

    @staticmethod
    def create_user(user_data):
        user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            # joined_date=datetime.now()
            slack_user_id=user_data['slack_user_id']
        )

        # db.query("INSERT INTO users ...")

        db.session.add(user)
        db.session.commit() #commits changes

        return user

    # def create_server_connection(self):
    #     try:
    #         with connect(
    #                 host=os.environ.get("DB_HOST"),
    #                 user=os.environ.get("DB_USER"),
    #                 password=os.environ.get("DB_PASSWORD"),
    #                 database=os.environ.get("DB_NAME"),
    #         ) as connection:
    #             print("Database connection successful")
    #             return connection
    #     except Error as err:
    #         print(f"Error connecting to database: '{err}'")
    #         return None

    @staticmethod
    def get_user_by_slack_user_id(slack_user_id):
        # IF RETURN NULL, THAT MEANS USER DOES NOT EXIST AND THUS SHOULD BE ONBOARDED
        # IF USER EXISTS, ASSUME THEY HAVE BEEN ONBOARDED
        # USE ONBOARDING TO GATHER USER INFORMATION
        user = User.query.filter_by(slack_user_id=slack_user_id).first()
        return user

    # def create_user(self, user):
    #     # connection = self.create_server_connection()
    #     cursor = self.connection.cursor()
    #
    #     query = (
    #         "INSERT INTO user (email, first_name, last_name, organization, slack_user_id)"
    #         "VALUES (%s, %s, %s, %s, %s);"
    #     )
    #
    #     data = (user['email'], user['first_name'], user['last_name'], user['organization'], user['slack_user_id'])
    #
    #     try:
    #         cursor.execute(query)
    #         result = self.connection.execute(query, data)
    #         print("User successfully created")
    #     except Error as err:
    #         print(f"Error: '{err}'")
    #
    #     cursor.close()
    #     return result

    # def update_user_by_user_id(self, user):
    #     # connection = self.create_server_connection()
    #     cursor = self.connection.cursor()
    #
    #     # NEED TO VALIDATE TEXT FOR SECURITY
    #
    #     query = (
    #         "UPDATE user"
    #         "SET email = %s, first_name = %s, last_name = %s, organization = %s, slack_user_id = %s"
    #         "WHERE id == %s;"
    #     )
    #
    #     try:
    #         result = cursor.execute(query, user['email'], user['first_name'], user['last_name'], user['organization'],
    #                                 user['slack_user_id'], user['id'])
    #         self.connection.commit()
    #         print("User successfully updated")
    #     except Error as err:
    #         print(f"Error: '{err}'")
    #
    #     cursor.close()
    #     return result

    # def update_user_key_value_by_slack_id(self, user_id, key, value):
    #     # connection = self.create_server_connection()
    #     cursor = self.connection.cursor()
    #
    #     # NEED TO VALIDATE TEXT FOR SECURITY
    #
    #     query = (
    #         "UPDATE user"
    #         "SET %s = %s"
    #         "WHERE slack_user_id == %s"
    #     )
    #
    #     try:
    #         result = cursor.execute(query, key, value, user_id)
    #         self.connection.commit()
    #         print("User successfully retrieved")
    #     except Error as err:
    #         print(f"Error: '{err}'")
    #
    #     cursor.close()
    #     return result

    def close(self):
        """call when done with this class to clean up DB connection"""
        self.connection.close()
