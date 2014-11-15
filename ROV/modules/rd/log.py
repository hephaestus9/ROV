from flask import render_template
from rov import app, LOG_FILE
from rov import rovlogger
from rovLib.pastebin.pastebin import PastebinAPI
import rov


@app.route('/xhr/log')
def xhr_log():
    return render_template('dialogs/log_dialog.html',
        log=rov.LOG_LIST,
    )


@app.route('/xhr/log/pastebin')
def xhr_log_pastebin():
    file = open(LOG_FILE)
    log = []
    log_str = ''

    for line in reversed(file.readlines()):
        log.append(line.rstrip())
        log_str += line.rstrip()
        log_str += '\n'

    file.close()
    x = PastebinAPI()
    try:
        url = x.paste('', log_str)
        rovlogger.log('LOG :: Log successfully uploaded to %s' % url, 'INFO')
    except Exception as e:
        rovlogger.log('LOG :: Log failed to upload - %s' % e, 'INFO')

    return render_template('dialogs/log_dialog.html',
        log=log,
        url=url,
    )
