import datetime as dt
import sqlalchemy as sa

from sqlalchemy.sql import func

from common.extensions.database import db

class StatPlotCount(db.Model):
    __bind_key__ = 'stat_plot_count'
    __tablename__ = "stat_plot_count"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlotsSize(db.Model):
    __bind_key__ = 'stat_plots_size'
    __tablename__ = "stat_plots_size"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatTotalCoins(db.Model):
    __bind_key__ = 'stat_total_coins'
    __tablename__ = "stat_total_coins"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatNetspaceSize(db.Model):
    __bind_key__ = 'stat_netspace_size'
    __tablename__ = "stat_netspace_size"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatTimeToWin(db.Model):
    __bind_key__ = 'stat_time_to_win'
    __tablename__ = "stat_time_to_win"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlotsTotalUsed(db.Model):
    __bind_key__ = 'stat_plots_total_used'
    __tablename__ = "stat_plots_total_used"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlotsDiskUsed(db.Model):
    __bind_key__ = 'stat_plots_disk_used'
    __tablename__ = "stat_plots_disk_used"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    path = db.Column(db.String())
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlotsDiskFree(db.Model):
    __bind_key__ = 'stat_plots_disk_free'
    __tablename__ = "stat_plots_disk_free"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    path = db.Column(db.String())
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlottingTotalUsed(db.Model):
    __bind_key__ = 'stat_plotting_total_used'
    __tablename__ = "stat_plotting_total_used"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    blockchain = sa.Column(sa.String(length=64), nullable=False)
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlottingDiskUsed(db.Model):
    __bind_key__ = 'stat_plotting_disk_used'
    __tablename__ = "stat_plotting_disk_used"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    path = db.Column(db.String())
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())

class StatPlottingDiskFree(db.Model):
    __bind_key__ = 'stat_plotting_disk_free'
    __tablename__ = "stat_plotting_disk_free"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String())
    path = db.Column(db.String())
    value = db.Column(db.REAL)
    created_at = db.Column(db.String())
