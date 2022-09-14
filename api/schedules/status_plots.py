#
# Performs a REST call to controller (possibly localhost) of all plots.
#

import datetime
import json
import os
import re
import traceback

from flask import g

from common.config import globals
from common.models import plots as p
from common.models import workers as w
from api import app, db
from api.commands import mmx_cli, rpc
from api import utils

# Due to database load, only store full plots list every X minutes
FULL_SEND_INTERVAL_MINS = 60

# Holds the cached status of Plotman analyze and Chia plots check
STATUS_FILE = '/root/.chia/plotman/status.json'

# Holds a cache of problematic plots
DUPLICATE_PLOTS_FILE = '/root/.chia/machinaris/cache/plots_duplicate_across_workers_chia.json'

last_full_send_time = None

def get_plot_attrs(plot_id, filename):
    dir,file = os.path.split(filename)
    match = re.match("plot(?:-mmx)?-k(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\w+).plot", file)
    if match:
        short_plot_id = match.group(7)[:8]
        created_at = "{0}-{1}-{2} {3}:{4}".format( match.group(2),match.group(3),match.group(4),match.group(5),match.group(6))
    else:
        short_plot_id = plot_id[2:10]
        created_at = "" 
    return [short_plot_id, dir,file,created_at]

def open_status_json():
    status = {}
    if os.path.exists(STATUS_FILE): 
        with open(STATUS_FILE, 'r+') as fp:
            status = json.load(fp)
    return status

def update():
    global last_full_send_time
    with app.app_context():
        since = (datetime.datetime.now() - datetime.timedelta(minutes=FULL_SEND_INTERVAL_MINS)).strftime("%Y-%m-%d %H:%M")
        if not last_full_send_time or last_full_send_time <= \
            (datetime.datetime.now() - datetime.timedelta(minutes=FULL_SEND_INTERVAL_MINS)):
            since = None  # No since filter sends all plots, not just recent
            last_full_send_time = datetime.datetime.now()
        if 'chia' in globals.enabled_blockchains():
            plots_status = open_status_json()
            update_chia_plots(plots_status, since)
        elif 'chives' in globals.enabled_blockchains():
            update_chives_plots(since)
        elif 'mmx' in globals.enabled_blockchains():
            update_mmx_plots(since)
        else:
            app.logger.debug("Skipping plots update from blockchains other than chia and chives as they all farm same as chia.")

def add_duplicate_plots(duplicated_plots, file, host1, path1, host2, path2):
    if file in duplicated_plots:
        duplications = duplicated_plots[file]
    else:
        duplications = [] 
        duplicated_plots[file] = duplications
    add_first = True
    for duplication in duplications:
        if host1 == duplication['host'] and path1 == duplication['path']:
            add_first = False
    if add_first:
        duplications.append({'host': host1, 'path': path1 })
    add_second = True
    for duplication in duplications:
        if host2 == duplication['host'] and path2 == duplication['path']:
            add_second = False
    if add_second:
        duplications.append({'host': host2, 'path': path2 })

def save_duplicate_plots(duplicated_plots):
    try:
        if not duplicated_plots:
            os.path(DUPLICATE_PLOTS_FILE).delete()
        else:
            with open(DUPLICATE_PLOTS_FILE, 'w') as outfile:
                json.dump(duplicated_plots, outfile)
    except Exception as ex:
        app.logger.error('Failed to store duplicated plots to {0}.'.format(DUPLICATE_PLOTS_FILE) + '\n' + str(ex))

def update_chia_plots(plots_status, since):
    try:
        if not since:  # If no filter, delete all for this blockchain before storing again
            db.session.query(p.Plot).filter(p.Plot.blockchain=='chia').delete()
            db.session.commit()
        blockchain_rpc = rpc.RPC()
        controller_hostname = utils.get_hostname()
        plots_farming = blockchain_rpc.get_all_plots()
        plots_by_id = {}
        duplicate_plots = {}
        displaynames = {}
        app.logger.info("Chia farmer RPC reports {0} total plots in this farm.".format(len(plots_farming)))
        chunk_size = 100 # Process only 10k plots at a time.
        for i in range(0, len(plots_farming), chunk_size):  # batch-size loop
            payload = []
            for plot in plots_farming[i:i+chunk_size]: # per-plot loop
                if plot['hostname'] in displaynames:
                    displayname = displaynames[plot['hostname']]
                else: # Look up displayname
                    try:
                        hostname = plot['hostname']
                        if plot['hostname'] in ['127.0.0.1']:
                            hostname = controller_hostname
                        #app.logger.info("Found worker with hostname '{0}'".format(hostname))
                        displayname = db.session.query(w.Worker).filter(w.Worker.hostname==hostname, 
                            w.Worker.blockchain=='chia').first().displayname
                    except:
                        app.logger.info("status_plots: Unable to find a worker with hostname '{0}'".format(plot['hostname']))
                        displayname = plot['hostname']
                    displaynames[plot['hostname']] = displayname
                short_plot_id,dir,file,created_at = get_plot_attrs(plot['plot_id'], plot['filename'])
                duplicated_on_same_host = False
                if not since and short_plot_id in plots_by_id:  # Only check for duplicates on full load
                    if plot['hostname'] == plots_by_id[short_plot_id]['hostname']:
                        app.logger.error("DUPLICATE CHIA PLOT FOUND ON SAME WORKER {0} AT BOTH {1}/{2} AND {3}/{4}".format(
                            displayname, plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], dir, file))
                        duplicated_on_same_host = True
                    else:
                        app.logger.error("DUPLICATE CHIA PLOT FOUND ON DIFFERENT WORKERS AT {0}@{1}/{2} AND {3}@{4}/{5}".format(
                            plots_by_id[short_plot_id]['worker'], plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], displayname, dir, file))
                    add_duplicate_plots(duplicate_plots, file, plot['hostname'], dir, plots_by_id[short_plot_id]['hostname'], plots_by_id[short_plot_id]['path'])
                plots_by_id[short_plot_id] = { 'hostname': plot['hostname'], 'worker': displayname, 'path': dir, 'file': file }
            if not duplicated_on_same_host and (not since or created_at > since):
                    payload.append({
                        "plot_id": short_plot_id,
                        "blockchain": 'chia',
                        "hostname": controller_hostname if plot['hostname'] in ['127.0.0.1'] else plot['hostname'],
                        "displayname": displayname,
                        "dir": dir,
                        "file": file,
                        "type": plot['type'],
                        "created_at": created_at,
                        "plot_analyze": analyze_status(plots_status, short_plot_id),
                        "plot_check": check_status(plots_status, short_plot_id),
                        "size": plot['file_size']
                    })
            if len(payload) > 0:
                try:
                    for new_item in payload: # Maximum of chunk_size plots inserted at a time.
                        item = p.Plot(**new_item)
                        db.session.add(item)
                    db.session.commit() # Commit every chunk size
                except Exception as ex:
                    app.logger.error("Failed to store batch of Chia plots being farmed [{0}:{1}] because {2}".format(i, i+chunk_size, str(ex)))
            if not since: # Save current duplicate plots
                save_duplicate_plots(duplicate_plots)
    except Exception as ex:
        app.logger.error("Failed to load Chia plots being farmed because {0}".format(str(ex)))
        traceback.print_exc()

# Sent from a separate fullnode container
def update_chives_plots(since):
    try:
        blockchain = 'chives'
        blockchain_rpc = rpc.RPC()
        hostname = utils.get_hostname()
        plots_farming = blockchain_rpc.get_all_plots()
        payload = []
        plots_by_id = {}
        for plot in plots_farming:
            short_plot_id,dir,file,created_at = get_plot_attrs(plot['plot_id'], plot['filename'])
            duplicated_on_same_host = False
            if not since and short_plot_id in plots_by_id:  # Only check for duplicates on full load
                if plot['hostname'] == plots_by_id[short_plot_id]['hostname']:
                    app.logger.error("DUPLICATE CHIVES PLOT FOUND ON SAME WORKER {0} AT BOTH {1}/{2} AND {3}/{4}".format(
                        plot['hostname'], plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], dir, file))
                    duplicated_on_same_host = True
                else:
                    app.logger.error("DUPLICATE CHIVES PLOT FOUND ON DIFFERENT WORKERS AT {0}@{1}/{2} AND {3}@{4}/{5}".format(
                        plots_by_id[short_plot_id]['worker'], plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], plot['hostname'], dir, file))
            plots_by_id[short_plot_id] = { 'hostname': plot['hostname'], 'worker': plot['hostname'], 'path': dir, 'file': file }
            if not duplicated_on_same_host and not since or created_at > since:
                payload.append({
                    "plot_id": short_plot_id,
                    "blockchain": blockchain,
                    "hostname": hostname if plot['hostname'] in ['127.0.0.1'] else plot['hostname'],
                    "displayname": None,  # Can't know all Chives workers' displaynames here, done in API receiver
                    "dir": dir,
                    "file": file,
                    "type": plot['type'],
                    "created_at": created_at,
                    "plot_analyze": None, # Handled in receiver
                    "plot_check": None, # Handled in receiver
                    "size": plot['file_size']
                })
        if not since:  # If no filter, delete all before sending all current again
            utils.send_delete('/plots/{0}/{1}'.format(hostname, blockchain), debug=False)
        if len(payload) > 0:
            utils.send_post('/plots/', payload, debug=False)
    except Exception as ex:
        app.logger.error("Failed to load and send Chives plots farming because {0}".format(str(ex)))

# Sent from a separate fullnode container
def update_mmx_plots(since):
    try:
        blockchain = 'mmx'
        hostname = utils.get_hostname()
        plots_farming = mmx_cli.list_plots()
        payload = []
        plots_by_id = {}
        for plot in plots_farming.rows:
            short_plot_id,dir,file,created_at = get_plot_attrs(plot['plot_id'], plot['filename'])
            duplicated_on_same_host = False
            if not since and short_plot_id in plots_by_id:  # Only check for duplicates on full load
                if plot['hostname'] == plots_by_id[short_plot_id]['hostname']:
                    app.logger.error("DUPLICATE MMX PLOT FOUND ON SAME WORKER {0} AT BOTH {1}/{2} AND {3}/{4}".format(
                        plot['hostname'], plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], dir, file))
                    duplicated_on_same_host = True
                else:
                    app.logger.error("DUPLICATE MMX PLOT FOUND ON DIFFERENT WORKERS AT {0}@{1}/{2} AND {3}@{4}/{5}".format(
                        plots_by_id[short_plot_id]['worker'], plots_by_id[short_plot_id]['path'], plots_by_id[short_plot_id]['file'], plot['hostname'], dir, file))
            plots_by_id[short_plot_id] = { 'hostname': plot['hostname'], 'worker': plot['hostname'], 'path': dir, 'file': file }
            if not duplicated_on_same_host and not since or created_at > since:
                payload.append({
                    "plot_id": short_plot_id,
                    "blockchain": blockchain,
                    "hostname": hostname if plot['hostname'] in ['127.0.0.1'] else plot['hostname'],
                    "displayname": None,  # Can't know all Chives workers' displaynames here, done in API receiver
                    "dir": dir,
                    "file": file,
                    "type": plot['type'],
                    "created_at": created_at,
                    "plot_analyze": None, # Handled in receiver
                    "plot_check": None, # Handled in receiver
                    "size": plot['file_size']
                })
        if not since:  # If no filter, delete all before sending all current again
            utils.send_delete('/plots/{0}/{1}'.format(hostname, blockchain), debug=False)
        if len(payload) > 0:
            utils.send_post('/plots/', payload, debug=False)
    except Exception as ex:
        app.logger.error("Failed to load and send MMX plots farming because {0}".format(str(ex)))

def analyze_status(plots_status, short_plot_id):
    if short_plot_id in plots_status:
        if "analyze" in plots_status[short_plot_id]:
            if plots_status[short_plot_id]['analyze'] and 'seconds' in plots_status[short_plot_id]['analyze']:
                return plots_status[short_plot_id]['analyze']['seconds']
            else:
                return "-"
    return None

def check_status(plots_status, short_plot_id):
    if short_plot_id in plots_status:
        if "check" in plots_status[short_plot_id]:
            if plots_status[short_plot_id]['check'] and 'status' in plots_status[short_plot_id]['check']:
                return plots_status[short_plot_id]['check']['status']
            else:
                return "-"
    return None
