# Flask related
from flask import Flask, request, render_template
from flask import jsonify
from flask_pymongo import PyMongo
import json
from bson import ObjectId
import datetime as dt
import joblib
from process_modelling import feat_split

class JSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, ObjectId):
			return(str(o))
		return(json.JSONEncoder.default(self, o))

db_credentials = {
	"DB_USERNAME": "feather_huzzah",
	"DB_PASSWORD": "ESP8266_micropython", 
	"DB_HOST": "localhost",
	"DB_PORT": "27017",
	"DB_NAME": "iot_lab5"
}

app = Flask(__name__)

app.config['MONGO_DBNAME']= db_credentials["DB_NAME"]
app.config['MONGO_URI']= "mongodb://{}:{}@{}:{}/{}".format(
	db_credentials["DB_USERNAME"],
	db_credentials["DB_PASSWORD"],
	db_credentials["DB_HOST"],
	db_credentials["DB_PORT"],
	db_credentials["DB_NAME"]
)

mongo = PyMongo(app)
coll = mongo.db.accel_data

@app.route('/')
def hello_world():
	#response_json = {}
	#for elmt in list(coll.find()):
	#	print(JSONEncoder().encode(elmt))
	response_json = {"current_document": list(coll.find())}
	return(JSONEncoder().encode(response_json))

@app.route('/submit', methods=['POST'])
def submit():
	input_json = request.json
	input_json["time_stamp"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	coll.insert_one(input_json)
	return(JSONEncoder().encode(input_json))

@app.route('/predict', methods=['POST'])
def predict():
	input_json = request.json
	input_json["time_stamp"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	input_feature = feat_split(input_json)
	prediction = clf.predict(input_feature)
	return(jsonify({'prediction': list(prediction)}))


if __name__== '__main__':
	clf = joblib.load('random_forest.joblib')
	app.run(debug=True, host="0.0.0.0", port=5000)

