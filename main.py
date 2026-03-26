from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import db
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId

app = FastAPI(title="Smart Appointment & Queue Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_TIME = 5   # each token takes 5 minutes

class User(BaseModel):
    email: str
    password: str
    role: str = "user"

class Token(BaseModel):
    user_email: str
    service: str


@app.get("/")
def root():
    return {"message": "Backend Running Successfully"}


@app.post("/register")
def register(user: User):
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    db.users.insert_one(user.dict())

    return {"message": "User Registered Successfully"}


@app.post("/login")
def login(user: User):
    existing_user = db.users.find_one({"email": user.email})

    if not existing_user or existing_user["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    return {
        "message": "Login Successful",
        "role": existing_user["role"]
    }


# TOKEN BOOKING WITH ESTIMATED TIME
@app.post("/book")
def book_token(token: Token):

    SERVICE_TIME = 5

    count = db.tokens.count_documents({})

    waiting = db.tokens.count_documents({
        "service": token.service,
        "status": "waiting"
    })

    token_number = count + 1

    estimated_time = waiting * SERVICE_TIME

    token_data = {
        "user_email": token.user_email,
        "service": token.service,
        "token_number": token_number,
        "status": "waiting",
        "estimated_time": estimated_time,
        "created_at": datetime.utcnow().isoformat()
    }

    db.tokens.insert_one(token_data)

    return {
        "message": "Token booked successfully",
        "token_number": token_number,
        "service": token.service,
        "estimated_time": estimated_time
    }

@app.get("/tokens")
def get_tokens():

    tokens = list(db.tokens.find({}))

    for token in tokens:
        token["_id"] = str(token["_id"])

    return tokens


@app.put("/update/{token_number}")
def update_token(token_number: int, status: str):

    db.tokens.update_one(
        {"token_number": token_number},
        {"$set": {"status": status}}
    )

    return {"message": "Token Updated Successfully"}

@app.get("/now-serving")
def now_serving():

    token = db.tokens.find_one(
        {"status": "served"},
        sort=[("token_number", -1)]
    )

    if token:
        return {"now_serving": token["token_number"]}
    
    return {"now_serving": 0}

@app.get("/queue-display")
def queue_display():

    served = db.tokens.find_one(
        {"status":"served"},
        sort=[("token_number",-1)]
    )

    next_token = db.tokens.find_one(
        {"status":"waiting"},
        sort=[("token_number",1)]
    )

    return {
        "now_serving": served["token_number"] if served else 0,
        "next_token": next_token["token_number"] if next_token else 0
    }


