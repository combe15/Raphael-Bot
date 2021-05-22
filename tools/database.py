import logging
import os

import dataset

import constants

log = logging.getLogger(__name__)

DB_HOST=constants.Db.host
DB_USER=constants.Db.user
DB_PASSWORD=constants.Db.password

def get_db():
    """ Returns the OS friendly path to the postgresql database. """
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_USER}"


def setup_db():
    """ Sets up the tables needed for Raphael. """
    log.info("Setting up database and tables.")
    with dataset.connect(get_db()) as db:
        # TODO: Add check to see if tables exists before creating.
        # Create mod_logs table and columns to store moderator actions.
        mod_logs = db.create_table("mod_logs")
        mod_logs.create_column("user_id", db.types.bigint)
        mod_logs.create_column("mod_id", db.types.bigint)
        mod_logs.create_column("timestamp", db.types.datetime)
        mod_logs.create_column("reason", db.types.text)
        mod_logs.create_column("type", db.types.text)
        
        # Create mod_logs table and columns to store moderator actions.
        mod_notes = db.create_table("mod_notes")
        mod_notes.create_column("user_id", db.types.bigint)
        mod_notes.create_column("mod_id", db.types.bigint)
        mod_notes.create_column("timestamp", db.types.datetime)
        mod_notes.create_column("note", db.types.text)

        # Create remind_me table and columns to store remind_me messages.
        remind_me = db.create_table("remind_me")
        remind_me.create_column("reminder_location", db.types.bigint)
        remind_me.create_column("author_id", db.types.bigint)
        remind_me.create_column("date_to_remind", db.types.text)
        remind_me.create_column("message", db.types.text)
        remind_me.create_column("sent", db.types.boolean, default=False)

        # Create stonks table and columns to store stonks transactions.
        stonks = db.create_table("stonks")
        stonks.create_column("author_id", db.types.bigint)
        stonks.create_column("stonk", db.types.text)
        stonks.create_column("amount", db.types.integer)
        stonks.create_column("investment_cost", db.types.float)
        stonks.create_column("timestamp", db.types.datetime)

        db.commit()
    # TODO: Retain what tables didn't exist/were created so we can print those to console.
    log.info("Created tables and columns.")