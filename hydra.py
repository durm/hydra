# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for, redirect
import os

application = Flask(__name__)

def get_items_list():
    ENABLED = os.listdir(application.config["ENABLED"])
    AVAILABLE = os.listdir(application.config["AVAILABLE"])
    return [(item, item in ENABLED) for item in AVAILABLE]

def enable(item):
    os.symlink(os.path.join(application.config["AVAILABLE"], item), os.path.join(application.config["ENABLED"], item))

def disable(item):
    os.unlink(os.path.join(application.config["ENABLED"], item))

@application.route("/")
@application.route("/items/")
def items_list():
    return render_template("items_list.html", vhosts=get_items_list())

@application.route("/items/save/", methods=["post"])
def save_items_status():
     ACTIVE = request.form.getlist("items")
     ENABLED = os.listdir(application.config["ENABLED"])
     AVAILABLE = os.listdir(application.config["AVAILABLE"])
     for item in AVAILABLE:
          if item in ACTIVE:
              if item not in ENABLED:
                  enable(item)
          else:
              if item in ENABLED:
                  disable(item)
     return redirect(url_for("items_list"))
     
if __name__ == "__main__":
     application.run()