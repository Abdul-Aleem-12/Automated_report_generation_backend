from pymongo import MongoClient
from dotenv import load_dotenv
import os


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["vulns_db"]
collection = db["vulns_col"]

def get_vulnerabilities(selected_vulns):
    return list(collection.find({"vuln_name": {"$in": selected_vulns}}, {"_id": 0}))
