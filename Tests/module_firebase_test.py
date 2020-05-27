import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://fir-test-python-44730.firebaseio.com/"
})
ref = db.reference("/")

ref.set({
    "Users": {
        "user1": {
            "name": "willem michielssen",
            "age": 15
        },
        "user2": {
            "name": "john doe",
            "age": 24
        },
    },
})

print(ref.get())

