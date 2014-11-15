# -*- coding: utf-8 -*-
import os
import sys

try:
    from rov.database import db
except:
    from database import db

def prefsRootPath():
    if sys.platform == "darwin":
            return os.path.expanduser("~/Library/Application Support/rov")
    elif sys.platform.startswith("win"):
            return os.path.join(os.environ['APPDATA'], "rov")
    else:
            return os.path.expanduser("~/.rov")


class Prefs():

    def __init__(self):
        # Check for ~/.rov
        if not os.path.isdir(prefsRootPath()):
                os.mkdir(prefsRootPath())
        if not os.path.isdir(prefsRootPath() + "/photos"):
                os.mkdir(prefsRootPath() + "/photos")

        self.db = db.Db(os.path.join(prefsRootPath(), "prefs.db"))
        #self.configDb = db.Db(os.path.join(prefsRootPath(), "config.db"))
        #query = self.configDb.query("SELECT name FROM sqlite_master")
        #query = query.fetchall()
        #print query

        self.db.beginTransaction()

        self.db.checkTable("rov_server_settings", [
            {"name": "name", "type": "text"},
            {"name": "value", "type": "text"}])

        self.db.checkTable("rov_misc_settings", [
            {"name": "key", "type": "int"},
            {"name": "value", "type": "text"},
            {"name": "description", "type": "text"},
            {"name": "type", "type": "text"},
            {"name": "options", "type": "text"}])

        self.db.checkTable("rov_plugin_settings", [
            {"name": "key", "type": "text"},
            {"name": "value", "type": "text"},
            {"name": "description", "type": "text"},
            {"name": "type", "type": "text"},
            {"name": "options", "type": "text"}])

        self.db.checkTable("rov", [
            {"name": "name", "type": "text"},
            {"name": "value", "type": "text"}])

        self.db.checkTable("sensor", [
            {"name": "name", "type": "text"},
            {"name": "value", "type": "text"}])

        self.db.checkTable("rovStreams", [
            {"name": "name", "type": "text"},
            {"name": "value", "type": "text"}])

        self.db.commitTransaction()

        # Check rov server defaults
        self.checkDefaults("rov_server_settings", {"name": "timesRun", "value": "0"})
        self.checkDefaults("rov_server_settings", {"name": "daemon", "value": "False"})
        self.checkDefaults("rov_server_settings", {"name": "pidfile", "value": "False"})
        self.checkDefaults("rov_server_settings", {"name": "pidFileName", "value": ""})
        self.checkDefaults("rov_server_settings", {"name": "port", "value": 7000})
        self.checkDefaults("rov_server_settings", {"name": "verbose", "value": "True"})
        self.checkDefaults("rov_server_settings", {"name": "development", "value": "True"})
        self.checkDefaults("rov_server_settings", {"name": "kiosk", "value": "False"})
        self.checkDefaults("rov_server_settings", {"name": "noupdate", "value": "True"})
        self.checkDefaults("rov_server_settings", {"name": "webroot", "value": ""})

        # Check rov misc defaults
        self.checkDefaults("rov_misc_settings", data={'key': 'lights_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of lights.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_misc_settings", data={'key': 'calibration_lasers_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of lasers.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_misc_settings", data={'key': 'camera_mount_axis_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of camera pan/tilt.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_misc_settings", data={'key': 'compass_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of compass.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_misc_settings", data={'key': 'orientation_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of accellorometer.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_misc_settings", data={'key': 'depth_capable',
                                                     'value': '0',
                                                     'description': 'Enable use of pressure transducer.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})

        # Check rov plugin defaults
        self.checkDefaults("rov_plugin_settings", data={'key': 'arduinofirmwareupload',
                                                     'value': '0',
                                                     'description': 'Enables remote arduino programming.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'blackbox',
                                                     'value': '0',
                                                     'description': 'Enables datalogging.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'capestatus',
                                                     'value': '0',
                                                     'description': 'Feedback for beaglebone cape.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'compass',
                                                     'value': '0',
                                                     'description': 'Enables compass use.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'diveprofile',
                                                     'value': '0',
                                                     'description': 'Enables depth tracking.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'flybywire',
                                                     'value': '0',
                                                     'description': 'Enables fly-by-wire.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'fpscounter',
                                                     'value': '0',
                                                     'description': 'Enables rate of travel tracking.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'headsupmenu',
                                                     'value': '0',
                                                     'description': 'Enables heads-up menu.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'horizon',
                                                     'value': '0',
                                                     'description': 'Enables artificial horizon.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'motor_diags',
                                                     'value': '0',
                                                     'description': 'Enables motor diagnostics.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})
        self.checkDefaults("rov_plugin_settings", data={'key': 'photocapture',
                                                     'value': '0',
                                                     'description': 'Enables capture of stills.',
                                                     'type': 'select',
                                                     'options': "{'1': 'Yes', '0': 'No'}"})

        #Check rov defaults
        self.checkDefaults("rov", {"name": "deadzone_pos", "value": 50})
        self.checkDefaults("rov", {"name": "deadzone_neg", "value": 50})
        self.checkDefaults("rov", {"name": "smoothingIncriment", "value": 40})
        self.checkDefaults("rov", {"name": "photoDirectory", "value": "~/.rov/photos"})
        self.checkDefaults("rov", {"name": "water_type", "value": "Fresh Water"})
        self.checkDefaults("rov", {"name": "thrust_modifier_port", "value": 1})
        self.checkDefaults("rov", {"name": "thrust_modifier_starboard", "value": 1})
        self.checkDefaults("rov", {"name": "thrust_modifier_vertical", "value": -1})
        self.checkDefaults("rov", {"name": "thrust_modifier_nport", "value": 2})
        self.checkDefaults("rov", {"name": "thrust_modifier_nstarboard", "value": 2})
        self.checkDefaults("rov", {"name": "thrust_modifier_nvertical", "value": -2})
        self.checkDefaults("rov", {"name": "debug", "value": "False"})
        self.checkDefaults("rov", {"name": "debug_commands", "value": "False"})
        self.checkDefaults("rov", {"name": "production", "value": "True"})
        self.checkDefaults("rov", {"name": "dead_zone", "value": 10})
        self.checkDefaults("rov", {"name": "video_device", "value": "/dev/video0"})
        self.checkDefaults("rov", {"name": "serial_baud", "value": 115200})
        self.checkDefaults("rov", {"name": "USE_MOCK", "value": "False"})
        self.checkDefaults("rov", {"name": "title", "value": "BCC - ROV"})
        self.checkDefaults("rov", {"name": "water_types", "value": "[\"Fresh Water\", \"Salt Water\"]"})
        self.checkDefaults("rov", {"name": "joystick_name", "value": ""})
        self.checkDefaults("rov", {"name": "CONTROL_UDP_IPSend", "value": "192.168.1.10"})
        self.checkDefaults("rov", {"name": "CONTROL_UDP_IPReceive", "value": ""})
        self.checkDefaults("rov", {"name": "CONTROL_UDP_PORT_SEND", "value": 5005})
        self.checkDefaults("rov", {"name": "CONTROL_UDP_PORT_RECV", "value": 5006})
        self.checkDefaults("rov", {"name": "ROV_UDP_IPSend", "value": "192.168.1.19"})
        self.checkDefaults("rov", {"name": "ROV_UDP_IPReceive", "value": ""})
        self.checkDefaults("rov", {"name": "ROV_UDP_PORT_SEND", "value": 5006})
        self.checkDefaults("rov", {"name": "ROV_UDP_PORT_RECV", "value": 5005})

        #Sensor Calibration Settings
        self.checkDefaults("sensor", {"name": "ACCEL_X_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "ACCEL_X_MAX", "value": 0.0})
        self.checkDefaults("sensor", {"name": "ACCEL_Y_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "ACCEL_Y_MAX", "value": 0.0})
        self.checkDefaults("sensor", {"name": "ACCEL_Z_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "ACCEL_Z_MAX", "value": 0.0})

        self.checkDefaults("sensor", {"name": "MAGN_X_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "MAGN_X_MAX", "value": 0.0})
        self.checkDefaults("sensor", {"name": "MAGN_Y_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "MAGN_Y_MAX", "value": 0.0})
        self.checkDefaults("sensor", {"name": "MAGN_Z_MIN", "value": 0.0})
        self.checkDefaults("sensor", {"name": "MAGN_Z_MAX", "value": 0.0})

        self.checkDefaults("sensor", {"name": "magn_ellipsoid_center", "value": "[0, 0, 0]"})
        self.checkDefaults("sensor", {"name": "magn_ellipsoid_transform", "value": "[[0, 0, 0], [0, 0, 0], [0, 0, 0]]"})

        self.checkDefaults("sensor", {"name": "GYRO_AVERAGE_OFFSET_X", "value": 0.0})
        self.checkDefaults("sensor", {"name": "GYRO_AVERAGE_OFFSET_Y", "value": 0.0})
        self.checkDefaults("sensor", {"name": "GYRO_AVERAGE_OFFSET_Z", "value": 0.0})
        self.checkDefaults("sensor", {"name": "GYRO_GAIN", "value": 0.06957})

        self.checkDefaults("sensor", {"name": "GRAVITY", "value": 256.0})

        self.checkDefaults("sensor", {"name": "Kp_ROLLPITCH", "value": 0.02})
        self.checkDefaults("sensor", {"name": "Ki_ROLLPITCH", "value": 0.00002})
        self.checkDefaults("sensor", {"name": "Kp_YAW", "value": 1.2})
        self.checkDefaults("sensor", {"name": "Ki_YAW", "value": 0.00002})

        self.checkDefaults("sensor", {"name": "ACCEL_X_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "ACCEL_Y_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "ACCEL_Z_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "ACCEL_X_SCALE", "value": 1})
        self.checkDefaults("sensor", {"name": "ACCEL_Y_SCALE", "value": 1})
        self.checkDefaults("sensor", {"name": "ACCEL_Z_SCALE", "value": 1})

        self.checkDefaults("sensor", {"name": "MAGN_X_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "MAGN_Y_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "MAGN_Z_OFFSET", "value": 0})
        self.checkDefaults("sensor", {"name": "MAGN_X_SCALE", "value": 1})
        self.checkDefaults("sensor", {"name": "MAGN_Y_SCALE", "value": 1})
        self.checkDefaults("sensor", {"name": "MAGN_Z_SCALE", "value": 1})

        #Check video stream defaults
        self.checkDefaults("rovStreams", {"name": "videoURL", "value": "http://"})
        self.checkDefaults("rovStreams", {"name": "video_port", "value": 8080})

    def getDb(self):
        return self.db

    def checkDefaults(self, table, data):
        cursor = self.db.select(table, where=data)
        if not cursor.fetchone():
            self.db.beginTransaction()
            self.db.insert(table, data)
            self.db.commitTransaction()

    def getPreference(self, table, name):
        cursor = self.db.select(table, where={"name": name})
        row = cursor.fetchone()
        if not row:
            raise Exception("No preference " + name)
        return row["value"]

    def getrovSettingValue(self, key, default=None):
        try:
            data = self.db.select("rov_server_settings", where={"key": key}, what="value")
            value = data.fetchone()

            if value == '':
                return None

            return value

        except:
            return default

    def getRov(self, name):
        cursor = self.db.select("rov", where={"name": name})
        row = cursor.fetchone()
        if not row:
            raise Exception("No rov property named: " + name)
        return row["value"]

    def getSensor(self, name):
        cursor = self.db.select("sensor", where={"name": name})
        row = cursor.fetchone()
        if not row:
            raise Exception("No sensor property named: " + name)
        return row["value"]

    def getRovPlugin(self, key):
        cursor = self.db.select("rov_plugin_settings", where={"key": key})
        row = cursor.fetchone()
        if not row:
            raise Exception("No rov plugin named: " + key)
        return row["value"]

    def getRovMisc(self, key):
        cursor = self.db.select("rov_misc_settings", where={"key": key})
        row = cursor.fetchone()
        if not row:
            raise Exception("No rov option named: " + key)
        return row["value"]

    def getRovStreams(self):
        cursor = self.db.select("rovStreams")
        row = cursor.fetchall()
        return row

    def getRovPlugins(self):
        cursor = self.db.select("rov_plugin_settings")
        row = cursor.fetchall()
        return row

    def getAllRovMisc(self):
        cursor = self.db.select("rov_misc_settings")
        row = cursor.fetchall()
        return row

    def getTimesRun(self):
        return int(self.getPreference("rov_server_settings", "timesRun"))

    def getDaemon(self):
        return self.getPreference("rov_server_settings", "daemon")

    def getPidFile(self):
        return self.getPreference("rov_server_settings", "pidfile")

    def getPidFileName(self):
        return self.getPreference("rov_server_settings", "pidFileName")

    def getPort(self):
        return int(self.getPreference("rov_server_settings", "port"))

    def getVerbose(self):
        return self.getPreference("rov_server_settings", "verbose")

    def getDevelopment(self):
        return self.getPreference("rov_server_settings", "development")

    def getKiosk(self):
        return self.getPreference("rov_server_settings", "kiosk")

    def getNoUpdate(self):
        return self.getPreference("rov_server_settings", "noupdate")

    def getWebroot(self):
        return self.getPreference("rov_server_settings", "webroot")

    def incTimesRun(self):
        r = int(self.getTimesRun())
        print((r))
        self.db.beginTransaction()
        self.db.update("rov_server_settings", {"value": r + 1}, {"name": "timesRun"})
        r = int(self.getTimesRun())
        print((r))
        self.db.commitTransaction()

    def setDaemon(self, value):
        self.db.beginTransaction()
        self.db.update("rov_server_settings", {"value": value}, {"name": "daemon"})
        self.db.commitTransaction()

    def setPidFile(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "pidfile"})
        self.db.commitTransaction()

    def setPidFileName(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "pidFileName"})
        self.db.commitTransaction()

    def setPort(self, port):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": port}, {"name": "port"})
        self.db.commitTransaction()

    def setVerbose(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "verbose"})
        self.db.commitTransaction()

    def setDevelopment(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "development"})
        self.db.commitTransaction()

    def setKiosk(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "kiosk"})
        self.db.commitTransaction()

    def setNoUpdate(self, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov_server_settings", {"value": value}, {"name": "noupdate"})
        self.db.commitTransaction()

    def setRov(self, name, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("rov", {"value": value}, {"name": name})
        self.db.commitTransaction()

    def setSensor(self, name, value):
        self.db.beginTransaction()
        self.db.insertOrUpdate("sensor", {"value": value}, {"name": name})
        self.db.commitTransaction()

    def addRovPlugin(self, data):
        cursor = self.db.select("rov_plugin_settings", where=data)
        if not cursor.fetchone():
            self.db.beginTransaction()
            self.db.insert("rov_plugin_settings", data)
            self.db.commitTransaction()

    def addRovMiscSetting(self, data):
        cursor = self.db.select("rov_misc_settings", where=data)
        if not cursor.fetchone():
            self.db.beginTransaction()
            self.db.insert("rov_misc_settings", data)
            self.db.commitTransaction()

    def addRovSetting(self, data):
        cursor = self.db.select("rov", where=data)
        if not cursor.fetchone():
            self.db.beginTransaction()
            self.db.insert("rov", data)
            self.db.commitTransaction()

    def getRovServerSettings(self):
        timesRun = self.getTimesRun()
        daemon = self.getDaemon()
        pidFile = self.getPidFile()
        pidFilename = self.getPidFileName()
        port = self.getPort()
        verbose = self.getVerbose()
        dev = self.getDevelopment()
        kiosk = self.getKiosk()
        update = self.getNoUpdate()
        webroot = self.getWebroot()

        data = ({'timesRun': timesRun,
                'daemon': daemon,
                'pidFile': pidFile,
                'pidFilename': pidFilename,
                'port': port,
                'verbose': verbose,
                'dev': dev,
                'kiosk': kiosk,
                'update': update,
                'webroot': webroot})
        return {'success': True, 'data': data}