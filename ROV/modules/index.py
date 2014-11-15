from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
import ast

from flask import render_template, session, request, redirect, url_for, jsonify
from flask.ext.socketio import emit, join_room, leave_room
from rov import app, socketio, Joystick, Comms
from rov.config import preferences

thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    comms = Comms.Comms()
    comms.receiverSetup()
    comms.receive()
    while True:
        time.sleep(0.25)
        ypr = comms.getYPR()
        socketio.emit('navdata', {'data': ypr}, namespace='/test')


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

    prefs = preferences.Prefs()
    title = prefs.getRov("title")
    styles = []
    scripts = []
    stylesLen = len(styles)
    scriptsLen = len(scripts)

    return render_template('index.html',
                            title=title,
                            styles=styles,
                            scripts=scripts,
                            stylesLen=stylesLen,
                            scriptsLen=scriptsLen)


@app.route('/cockpit')
def cockpit():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

    prefs = preferences.Prefs()
    title = prefs.getRov("title")
    styles = []
    scripts = []
    stylesLen = len(styles)
    scriptsLen = len(scripts)

    return render_template('index.html',
                            title=title,
                            styles=styles,
                            scripts=scripts,
                            stylesLen=stylesLen,
                            scriptsLen=scriptsLen)


@app.route('/rovPreferences')
def rovPreferences():
    prefs = preferences.Prefs()

    #ROV Settings
    title = prefs.getRov("title")
    styles = []
    scripts = []
    stylesLen = len(styles)
    scriptsLen = len(scripts)
    rovSettings = prefs.getAllRovMisc()
    plugins = prefs.getRovPlugins()

    joystickName = prefs.getRov("joystick_name")
    waterTypes = ast.literal_eval(prefs.getRov("water_types"))
    waterType = prefs.getRov("water_type")

    ControlUDPIPSend = prefs.getRov("CONTROL_UDP_IPSend")
    ControlUDPIPReceive = prefs.getRov("CONTROL_UDP_IPReceive")
    ControlUDPPortSend = prefs.getRov("CONTROL_UDP_PORT_SEND")
    ControlUDPPortRecv = prefs.getRov("CONTROL_UDP_PORT_RECV")

    #ROV-Sensor Settings

    # Server Settings
    serverSettings = prefs.getRovServerSettings()['data']
    timesRun = serverSettings['timesRun']
    daemon = serverSettings['daemon']
    pidFile = serverSettings['pidFile']
    pidFilename = serverSettings['pidFilename']
    port = serverSettings['port']
    verbose = serverSettings['verbose']
    development = serverSettings['dev']
    kiosk = serverSettings['kiosk']
    update = serverSettings['update']
    webroot = serverSettings['webroot']

    return render_template('rovPreferences.html',
                            title=title,
                            styles=styles,
                            scripts=scripts,
                            stylesLen=stylesLen,
                            scriptsLen=scriptsLen,
                            rovSettings=rovSettings,
                            plugins=plugins,
                            timesRun=timesRun,
                            daemon=daemon,
                            pidFile=pidFile,
                            pidFilename=pidFilename,
                            port=port,
                            verbose=verbose,
                            development=development,
                            kiosk=kiosk,
                            update=update,
                            webroot=webroot,
                            waterTypes=waterTypes,
                            waterType=waterType)


@app.route('/save_settings', methods=['GET', 'POST'])
def save_settings():
    if request.method == 'POST':
        values = request.values
        prefs = preferences.Prefs()
        # TODO: fix this for first run
        try:
            audioQuality = values["audioQuality"]
            password = values["password"]
            username = values["user"]
            proxyURL = values["proxyURL"]
            controlProxyURL = values["controlProxyURL"]
            try:
                screensaver = values["screensaver"]
            except:
                screensaver = "off"

            try:
                icon = values["icon"]
            except:
                icon = "off"

            try:
                songsUpdate = values["songsUpdate"]
            except:
                songsUpdate = "off"

            try:
                pandoraOne = values["pandoraOne"]
            except:
                pandoraOne = "off"

            prefs.setPandoraUsername(username)
            prefs.setPandoraPassword(password)
            prefs.setPandoraAudioQuality(audioQuality)
            prefs.setPandoraProxy(proxyURL)
            prefs.setPandoraControlProxy(controlProxyURL)
            prefs.setScreensaverPause(screensaver)
            prefs.setIcon(icon)
            prefs.setNotify(songsUpdate)
            prefs.setPandoraOne(pandoraOne)

        except:
            print(("request error: save_settings"))

    return redirect(url_for('pandoraPreferences'))


@app.route('/save_plugin_settings', methods=['GET', 'POST'])
def save_plugin_settings():
    pass


@app.route('/save_rov_settings', methods=['GET', 'POST'])
def save_rov_settings():
    pass

@app.route('/changeWaterType', methods=['GET', 'POST'])
def changeWaterType():
    pass


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(request.namespace.rooms),
          'count': session['receive_count']})


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         room=message['room'])


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
