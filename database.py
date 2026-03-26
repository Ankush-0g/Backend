
from pymongo import MongoClient

client = MongoClient("mongodb+srv://ankushgupta4747_db_user:m7VD2QjSzpReH1kW@ankush7.o7ginho.mongodb.net/smart_queue_db?retryWrites=true&w=majority&appName=Ankush7")
db = client["smart_queue_db"]
