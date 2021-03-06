"""Web interface to SLURM."""

import logging
import threading
import time
import webbrowser
import shlex

import flask
import markdown2

import run_utils
import web_utils

app = flask.Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


@app.context_processor
def inject_globals():
    """Make some functions available in the templates."""
    return {"icon": web_utils.icon}


@app.route("/")
def myapp():
    """App page."""
    manual_html = markdown2.markdown(
        open("MANUAL.md").read(), extras=["header-ids", "toc"]
    )

    return flask.render_template(
        "app.jinja2",
        title="SLURM dashboard",
        manual_html=manual_html,
    )


@app.route("/api/watch_queue", methods=["POST"])
def term_watch_queue():
    """Watch queue api endpoint."""
    hostname = flask.request.form.get("hostname")
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    ssh_cmd = "watch squeue -u $(whoami)"
    run_utils.run_term_ssh_cmd(hostname, username, password, ssh_cmd)
    return "OK"


@app.route("/api/remote_shell", methods=["POST"])
def term_remote_shell():
    """Remote shell api endpoint."""
    hostname = flask.request.form.get("hostname")
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    remote_path = flask.request.form.get("remote_path")
    run_utils.run_term_ssh(hostname, username, password, remote_path)
    return "OK"


@app.route("/api/run", methods=["POST"])
def term_run():
    """Terminal run api endpoint."""
    hostname = flask.request.form.get("hostname")
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    remote_path = flask.request.form.get("remote_path")
    ssh_cmd = f"cd {shlex.quote(remote_path)} ; sbatch $(find . -name '*.job')"
    run_utils.run_term_ssh_cmd(hostname, username, password, ssh_cmd)
    return "OK"


@app.route("/api/rsync_up", methods=["POST"])
def term_rsync_up():
    """Rsync from local to remote api endpoint."""
    hostname = flask.request.form.get("hostname")
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    local_path = flask.request.form.get("local_path").strip().rstrip("/")
    remote_path = flask.request.form.get("remote_path").strip().rstrip("/")
    run_utils.run_term_rsync_up(hostname, username, password, local_path, remote_path)
    return "OK"


@app.route("/api/rsync_down", methods=["POST"])
def term_rsync_down():
    """Rsync from remote to local api endpoint."""
    hostname = flask.request.form.get("hostname")
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    local_path = flask.request.form.get("local_path").strip().rstrip("/")
    remote_path = flask.request.form.get("remote_path").strip().rstrip("/")
    run_utils.run_term_rsync_down(hostname, username, password, local_path, remote_path)
    return "OK"


@app.route("/api/filebrowser", methods=["POST"])
def filebrowser():
    """Launch filebrowser api endpoint."""
    local_path = flask.request.form.get("local_path")
    run_utils.run_filebrowser(local_path)
    return "OK"


def main():
    """Run flask server."""
    debug = False
    web_url = "http://127.0.0.1:7322"

    def open_shawl():
        """Open the web browser to the shawl url after 3 seconds."""
        time.sleep(3)
        webbrowser.open_new(web_url)

    if not debug:
        threading.Thread(target=open_shawl).start()
    app.run(port=7322, debug=debug)


if __name__ == "__main__":
    main()
