# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for, redirect
import os

application = Flask(__name__)
application.debug = True

SERVICES = {
    "nginx": {
        "ENABLED": "/etc/nginx/sites-enabled",
        "AVAILABLE": "/etc/nginx/sites-available",
        "RESTART": "sleep 3 && service nginx reload &",
        "TPL":"nginx_tpl.conf",
        "PARAMS": ["server_name", "root", "proxy_pass"]
    },
    "uwsgi": {
        "ENABLED": "/etc/uwsgi/apps-enabled",
        "AVAILABLE": "/etc/uwsgi/apps-available",
        "RESTART": "sleep 3 && service uwsgi reload &",
        "TPL":"uwsgi_tpl.conf",
        "PARAMS": ["virtualenv", "plugin", "chdir", "env", "module", "processes", "threads", "http", "uid", "gid"]
    }
}

def get_items_list(config):
    ENABLED = os.listdir(config["ENABLED"])
    AVAILABLE = os.listdir(config["AVAILABLE"])
    return [(item, item in ENABLED) for item in AVAILABLE]

def enable(config, item):
    os.symlink(os.path.join(config["AVAILABLE"], item), os.path.join(config["ENABLED"], item))
    restart(config)

def disable(config, item):
    os.unlink(os.path.join(config["ENABLED"], item))
    restart(config)

def restart(config):
    os.system(config["RESTART"])

def is_active(config, item):
    return item in os.listdir(config["ENABLED"])

def store(config, name, content):
    with open(os.path.join(config["AVAILABLE"], name), "w") as item:
        item.write(content)
        
def get_content(config, name):
    with open(os.path.join(config["AVAILABLE"], name)) as item:
        return item.read()

@application.route("/")
def service_list():
    return render_template("service_list.html", services=SERVICES.keys())

@application.route("/<service>/")
def items_list(service):
    return render_template("items_list.html", items=get_items_list(SERVICES[service]), service=service)

@application.route("/<service>/save/", methods=["post"])
def save_items_status(service):
    config = SERVICES[service]
    ACTIVE = request.form.getlist("item")
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

@application.route("/<service>/create/")
def item_create(service):
    return render_template("item_create.html", service=service, config=SERVICES[service])

@application.route("/<service>/create/save/", methods=["post"])
def item_create_save(service):
    
    config = SERVICES[service]
    content = render_template(config["TPL"], **request.form.to_dict())
    
    item = request.form.get("item", "")
    active = request.form.get("active", "0") == 1
    
    store(config, item, content)
    
    return redirect(url_for("items_list", service=service))


@application.route("/<service>/update/<item>/")
def item_update(service, item):
    config = SERVICES[service]
    active = is_active(config, item)
    content = get_content(config, item)
    return render_template("item_update.html", service=service, item=item, content=content)

@application.route("/<service>/update/save/", methods=["post"])
def item_update_save(service):
    
    config = SERVICES[service]
    
    item = request.form.get("item")
    content = request.form.get("content")
    active = request.form.get("active", "0") == 1
    
    store(config, item, content)
    
    return redirect(url_for("items_list", service=service))

if __name__ == "__main__":
    application.run()
    