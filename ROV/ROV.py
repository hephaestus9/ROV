#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is the main executable of ROV. It parses the command line arguments, does init and calls the start function of ROV."""
import sys
import os
from flask import Flask
from flask.ext.socketio import SocketIO


# Check if frozen by py2exe
def check_frozen():
    return hasattr(sys, 'frozen')


def get_rundir():
    if check_frozen():
        return os.path.abspath(str(sys.executable, sys.getfilesystemencoding()))

    return os.path.abspath(__file__)[:-13]


def rovRootPath():
    if sys.platform == "darwin":
            return os.path.expanduser("~/Library/Application Support/rov")
    elif sys.platform.startswith("win"):
            return os.path.join(os.environ['APPDATA'], "rov")
    else:
            return os.path.expanduser("~/.rov")


# Set the rundir
dataDir = rovRootPath()
if not os.path.isdir(rovRootPath()):
                os.mkdir(rovRootPath())
rundir = get_rundir()

# Include paths
sys.path.insert(0, rundir)
sys.path.insert(0, os.path.join(rundir, 'rovLib'))

# Create Flask instance
app = Flask(__name__)
app.secret_key = '\xc8/x\xa4\x9f\xfaQw\xe5\xfe\xdd:\x0eq\xdai_\n\xedZ\x02\xf5\xbb\xb9'
socketio = SocketIO(app)

# If frozen, we need define static and template paths
if check_frozen():
    app.root_path = rundir
    app.static_path = '/static'
    app.add_url_rule(
        app.static_path + '/<path:filename>',
        endpoint='static',
        view_func=app.send_static_file
    )

    from jinja2 import FileSystemLoader
    app.jinja_loader = FileSystemLoader(os.path.join(rundir, 'templates'))


def import_modules():
    import modules.index
    from modules.rd import log


@app.teardown_request
def shutdown_session(exception=None):
    """This function is called as soon as a session is shutdown and makes sure, that the db session is also removed."""
    pass

import rov
from rov.config import preferences


class rovMain():
    def __init__(self):
        """Main function that is called at the startup of ROV."""
        self.started = False
        self.prefs = preferences.Prefs()

        from optparse import OptionParser

        p = OptionParser()

        # define command line options
        p.add_option('-p', '--port',
                     dest='port',
                     default=None,
                     help="Force webinterface to listen on this port")
        p.add_option('-d', '--daemon',
                     dest='daemon',
                     action='store_true',
                     help='Run as a daemon')
        p.add_option('--pidfile',
                     dest='pidfile',
                     help='Create a pid file (only relevant when running as a daemon)')
        p.add_option('--log',
                     dest='log',
                     help='Create a log file at a desired location')
        p.add_option('-v', '--verbose',
                     dest='verbose',
                     action='store_true',
                     help='Silence the logger')
        p.add_option('--develop',
                     action="store_true",
                     dest='develop',
                     help="Start instance of development server")
        p.add_option('--database',
                     dest='database',
                     help='Custom database file location')
        p.add_option('--webroot',
                     dest='webroot',
                     help='Web root for rov')
        p.add_option('--host',
                     dest='host',
                     help='Web host for rov')
        p.add_option('--kiosk',
                     dest='kiosk',
                     action='store_true',
                     help='Disable settings in the UI')
        p.add_option('--datadir',
                     dest='datadir',
                     help='Write program data to custom location')
        p.add_option('--noupdate',
                     action="store_true",
                     dest='noupdate',
                     help='Disable the internal updater')

        # parse command line for defined options
        options, args = p.parse_args()

        if options.datadir:
            data_dir = options.datadir
        else:
            data_dir = dataDir

        if options.daemon:
            rov.DAEMON = True
            rov.VERBOSE = False
        else:
            val = self.prefs.getDaemon()
            if val == "True":
                rov.DAEMON = True
                rov.VERBOSE = False

        if options.pidfile:
            rov.PIDFILE = options.pidfile
            rov.VERBOSE = False
        else:
            val = self.prefs.getPidFile()
            if val == "True":
                rov.PIDFILE = self.prefs.getPidFilName()
                rov.VERBOSE = False

        if options.port:
            PORT = int(options.port)
        else:
            PORT = self.prefs.getPort()  # 7000

        if options.log:
            rov.LOG_FILE = options.log

        if options.verbose:
            rov.VERBOSE = True
        else:
            val = self.prefs.getVerbose()
            if val == "True":
                rov.VERBOSE = True

        if options.develop:
            rov.DEVELOPMENT = True
        else:
            val = self.prefs.getDevelopment()
            if val == "True":
                rov.DEVELOPMENT = True

        if options.database:
            DATABASE = options.database
        else:
            DATABASE = os.path.join(dataDir, 'prefs.db')

        if options.webroot:
            rov.WEBROOT = options.webroot

        if options.host:
            rov.HOST = options.host

        if options.kiosk:
            rov.KIOSK = True
        else:
            val = self.prefs.getKiosk()
            if val == "True":
                rov.KIOSK = True

        if options.noupdate:
            rov.UPDATER = False
        else:
            val = self.prefs.getNoUpdate()
            if val == "True":
                rov.UPDATER = False

        rov.RUNDIR = rundir
        rov.DATA_DIR = data_dir
        rov.FULL_PATH = os.path.join(rundir, 'rov.py')
        rov.ARGS = sys.argv[1:]
        rov.PORT = PORT
        rov.DATABASE = DATABASE
        rov.VERBOSE = True
        rov.DEVELOPMENT = False

        rov.initialize()

        if rov.PIDFILE or rov.DAEMON:
            rov.daemonize()

        import_modules()
        rov.init_updater()

        rov.start()


if __name__ == '__main__':
    rovApp = rovMain()
