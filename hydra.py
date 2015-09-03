# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for, redirect
import os

application = Flask(__name__)

SERVICES = {
    "nginx": {
        "ENABLED": "/etc/nginx/sites-enabled",
        "AVAILABLE": "/etc/nginx/sites-available",
        "RESTART": "service nginx restart"
    }
}

def get_items_list(config):
    ENABLED = os.listdir(config["ENABLED"])
    AVAILABLE = os.listdir(config["AVAILABLE"])
    return [(item, item in ENABLED) for item in AVAILABLE]

def enable(config, item):
    os.symlink(os.path.join(config["AVAILABLE"], item), os.path.join(config["ENABLED"], item))

def disable(config, item):
    os.unlink(os.path.join(config["ENABLED"], item))

def restart(config):
    os.system(config["RESTART"])

@application.route("/<service>/")
def items_list(service):
    return render_template("items_list.html", vhosts=get_items_list(SERVICES[service]), service=service)

@application.route("/<service>/save/", methods=["post"])
def save_items_status(service):
    config = SERVICES[service]
    ACTIVE = request.form.getlist("items")
    ENABLED = os.listdir(config["ENABLED"])
    AVAILABLE = os.listdir(config["AVAILABLE"])
    for item in AVAILABLE:
         if item in ACTIVE:
             if item not in ENABLED:
                 enable(config, item)
         else:
             if item in ENABLED:
                 disable(config, item)
    return redirect(url_for("items_list", service=service))
     
if __name__ == "__main__":
    application.run()
    