import os
from tkinter.tix import Tree
from flask import Flask
from flask.cli import FlaskGroup

from project import create_app, db

app = create_app("project.config.Config")

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.create_all()
    db.session.commit() 

if __name__ == "__main__":
    cli()