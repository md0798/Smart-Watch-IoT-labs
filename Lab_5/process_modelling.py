
from pymongo import MongoClient
from pprint import pprint
import pandas as pd

#from sklearn import train_test_split
from sklearn import svm, ensemble
from sklearn.metrics import classification_report
#from sklearn.externals 
import joblib

db_credentials = {
	"DB_USERNAME": "feather_huzzah",
	"DB_PASSWORD": "ESP8266_micropython", 
	"DB_HOST": "localhost",
	"DB_PORT": "27017",
	"DB_NAME": "iot_lab5"
}

def get_df_from_mongo(cred=db_credentials):
	mongo_uri = "mongodb://{}:{}@{}:{}/{}".format(
		cred["DB_USERNAME"],
		cred["DB_PASSWORD"],
		cred["DB_HOST"],
		cred["DB_PORT"],
		cred["DB_NAME"]
	)
	client = MongoClient(mongo_uri)
	db = client[cred["DB_NAME"]]
	coll = db.accel_data
	# query = {}
	df = pd.DataFrame(list(coll.find()))

	return(df)

def feat_split(df):
	df = pd.DataFrame(df)
	feature_set = pd.DataFrame()
	for col in df.columns[df.columns.str.contains('pos', case=False)]:
		temp = df[col].apply(pd.Series)
		col_name = [col+str(i) for i in temp.columns]
		temp.columns = col_name
		feature_set = pd.concat([feature_set, temp], axis=1)

	return(feature_set)


# Main function
def main():
	df = get_df_from_mongo()

	class_label = df["character"]
	feature_set = feat_split(df)

	#clf = svm.SVC(gamma='scale', decision_function_shape='ovo')
	clf = ensemble.RandomForestClassifier()
	clf.fit(feature_set, class_label)

	pred = clf.predict(feature_set)

	print(pd.concat([class_label, pd.Series(pred)], axis=1))
	print(classification_report(class_label, pd.Series(pred)))

	joblib.dump(clf, 'random_forest.joblib')

if __name__ == "__main__":
	main()
