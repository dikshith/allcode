from flask_sqlalchemy import SQLAlchemy
from __main__ import app, db



class performance_results(db.Model):
   id = db.Column('id', db.Integer, primary_key = True)
   release_version_id = db.Column(db.Integer, db.ForeignKey('release_version.id'), nullable = False)
   label = db.Column(db.String(50))
   samples = db.Column(db.Integer)
   average = db.Column(db.Integer)
   median = db.Column(db.Integer)
   ninty_percentile_line = db.Column(db.Integer)
   ninty_five_percentile_line = db.Column(db.Integer)
   ninty_nine_percentile_line = db.Column(db.Integer)
   minor = db.Column(db.Integer)
   maximum = db.Column(db.Integer)
   error = db.Column(db.DECIMAL(10, 6))
   throughput = db.Column(db.DECIMAL(10, 6))
   received = db.Column(db.DECIMAL(10, 6))
   sent = db.Column(db.DECIMAL(10, 6))

   def __init__(self, release_version, label, samples, average,median, ninty_percentile_line, ninty_five_percentile_line, ninty_nine_percentile_line,minor, maximum, error, throughput,received, sent):
        self.release_version_id = release_version
        self.label = label
        self.samples = samples
        self.average = average
        self.median = median
        self.ninty_percentile_line = ninty_percentile_line
        self.ninty_five_percentile_line = ninty_five_percentile_line
        self.ninty_nine_percentile_line = ninty_nine_percentile_line
        self.minor = minor
        self.maximum = maximum
        self.error = error
        self.throughput = throughput
        self.received = received
        self.sent = sent


class release_version(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    version = db.Column(db.DECIMAL(10, 2))
    release_version = db.relationship("performance_results", backref = 'performance_results', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, rel_version):
        self.version = rel_version
