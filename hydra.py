
from flask import Flask, render_template, request, url_for, redirect
import os

application = Flask(__name__)
application.debug = True

SITES_AVAILABLE = "/etc/nginx/sites-available"
SITES_ENABLED = "/etc/nginx/sites-enabled"

def get_vhosts_list():
    result = []
    sites_enabled = os.listdir(SITES_ENABLED)
    for f in os.listdir(SITES_AVAILABLE):
        result.append((f, f in sites_enabled))
    return result

def enable_site(site):
    os.symlink(os.path.join(SITES_AVAILABLE, site), os.path.join(SITES_ENABLED, site))

def disable_site(site):
    os.unlink(os.path.join(SITES_ENABLED, site))

@application.route("/")
def vhosts():
    return render_template("vhosts.html", vhosts=get_vhosts_list())

@application.route("/hosts/save/", methods=["post"])
def save_vhosts_status():
     active_vhosts = request.args.getlist("vhost")
     sites_enabled = os.listdir(SITES_ENABLED)
     for f in os.listdir(SITES_AVAILABLE):
          if f in active_vhosts:
              if f not in sites_enabled:
                  enable_site(f)
          else:
              if f in sites_enabled:
                  disable_site(f)
     return redirect(url_for("vhosts"))
     
if __name__ == "__main__":
     application.run()