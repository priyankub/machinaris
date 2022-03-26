#
# Details for drives attached to workers
#

import datetime
import os
import psutil
import re
import signal
import shutil
import socket
import time
import traceback
import yaml

from flask import Flask, jsonify, abort, request, flash

from common.models import drives as d
from web import app, db, utils
from web.models import drives

def load_drive_summary():
    drvs = db.session.query(d.Drive).order_by(d.Drive.hostname).all()
    return drives.Drives(drvs)

def load_smartctl_info(hostname, device):
    drv = db.session.query(d.Drive).filter(d.Drive.hostname == hostname, d.Drive.device == device).first()
    return drv.smart_info