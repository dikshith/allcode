# save this as app.py
from flask import Flask, request, jsonify, abort
from flask import render_template, request, flash, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import time


app = Flask(__name__, static_url_path = "", static_folder = "images")
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'csv')
IMAGE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'images')
ALLOWED_EXTENSIONS = {'csv', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
db = SQLAlchemy(app)
#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin123@localhost/csvdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



import admin
from models import performance_results, release_version

@app.route("/", methods=["GET", "POST"])
def home():
    filter_data = []
    if request.method == "POST":
        rel_version, label, res_time = request.form.getlist("release_version[]"), request.form.getlist("label[]"), request.form.getlist("response_time[]")
        graphs = []
        for i in range(len(rel_version)):

            record = db.session.query(performance_results).join(release_version).filter(release_version.version == rel_version[i]).all()

            if res_time[i]:
                record = db.session.query(performance_results).join(release_version).filter(performance_results.ninty_percentile_line > int(res_time[i]), release_version.version == rel_version[i]).all()

            if label[i]:
                record = db.session.query(performance_results).join(release_version).filter(performance_results.label == label[i], release_version.version == rel_version[i]).all()
                
            if res_time[i] and label[i]:
                record = db.session.query(performance_results).join(release_version).filter(performance_results.ninty_percentile_line > int(res_time[i]), performance_results.label == label[i], release_version.version == rel_version[i]).all()
            # Create Ggraph
            
            plt.figure(figsize=(13.5, 5))
            x_axis = []
            y_axis = []
            for j in record:
                if j.label != "TOTAL":
                    x_axis.append(j.label)
                    y_axis.append(j.ninty_percentile_line)
            plt.xlabel('Transaction', fontweight="bold", color="green")
            plt.ylabel('Response Time', fontweight="bold", color="green")
            plt.title('Graph-'+str(i+1), fontweight="bold", color="red")
            plt.bar(x_axis, y_axis)

            image_name = '/graph_' + str(i) + ".jpg"
            plt.savefig(IMAGE_UPLOAD_FOLDER + image_name, block=True, bbox_inches='tight')
            graphs.append(image_name)

            # Making filter data response
            filter_data.append({"record": record, "release_version": rel_version[i], "label": label[i], "response_time": res_time[i], "graph": image_name})

        if len(graphs) < 2:
            graphs = []
        return render_template("home/data.html", filter_data=filter_data, graphs=graphs), 404

    versions = db.session.query(release_version.version.distinct().label("version")).all()
    labels = db.session.query(performance_results.label.distinct().label("label")).all()
    response_time = db.session.query(performance_results.ninty_percentile_line.distinct().label("ninty_percentile_line")).all()
    return render_template("home/home.html", data=versions, label=labels, response_time=response_time, filter_data=filter_data), 404


if __name__ == '__main__':
    app.secret_key = 'AS@$##%$^JHGJHGHK&(*&)('
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=5500)
