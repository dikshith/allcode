# save this as app.py
from __main__ import app, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import Flask, request, jsonify, abort, render_template, Flask, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import io
import csv
from models import *


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        table = request.form.get("table")
        if 'csv' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['csv']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # import pdb; pdb.set_trace()
            flash('File uploaded Successfully!')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Read csv file
            csv_input = csv.DictReader(open(os.path.join(app.config['UPLOAD_FOLDER'], filename)))

            rel_version = release_version(6)
            db.session.add(rel_version)
            db.session.commit()
            rel_id = rel_version.id

            for row in csv_input:
                print(row)
                performance = performance_results(rel_id, row['Label'], int(row['# Samples']), int(row['Average']), int(row['Median']), int(row['90% Line']), int(row['95% Line']), int(row['99% Line']), int(row['Min']),   int(row['Max']), float(row['Error %']), float(row['Throughput']), float(row['Received KB/sec']), float(row['Sent KB/sec']))
                db.session.add(performance)
                db.session.commit()

            return redirect(request.url)

    return render_template("admin/admin.html"), 404
