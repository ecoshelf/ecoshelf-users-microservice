from bson import ObjectId
from fastapi import FastAPI, Path, Response, HTTPException
from mongo_db_atlas_adaptor import MongoAdaptor
from helpers import convert_mongo_results_to_dict
from models import Users
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Para executar:
# uvicorn api:app --reload

# Serviço disponível em:
# https://i5ujqdu2eokjdwvlrzztnvss5y0zcilo.lambda-url.us-east-1.on.aws/docs

app = FastAPI()
mongo = MongoAdaptor()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/users", status_code=200)
def get_all_users(response: Response):
    """get all users"""
    results = mongo.find_all()
    results_len = len([results].copy())
    response.headers['X-Total-Count'] = str(results_len)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers["Content-Range"] = "bytes: 0-9/*"
    results_dict = convert_mongo_results_to_dict(results)
    if results_dict:
        return results_dict
    else:
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/users/phone_number/{phone_number}", status_code=200)
def get_user_by_phone_number(response: Response, phone_number: str = Path(description="Insira o número de whatsapp do usuário")):
    """get user by phone number"""
    results = mongo.find({'phone_number': phone_number})
    results_len = len([results].copy())
    response.headers['X-Total-Count'] = str(results_len)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers["Content-Range"] = "bytes: 0-9/*"
    results_dict = convert_mongo_results_to_dict(results)
    if results_dict:
        return results_dict
    else:
        raise HTTPException(status_code=404, detail="Not found")

@app.get("/users/{id}", status_code=200)
def get_user_by_object_id(response: Response, id: str = Path(description="User ID")):
    """get user by id"""
    results = mongo.find({'_id': ObjectId(id)})
    results_len = len([results].copy())
    response.headers['X-Total-Count'] = str(results_len)
    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers["Content-Range"] = "bytes: 0-9/*"
    return {'id': id}


@app.post("/users", status_code=201)
def create_user(user: dict):
    try:
        user_obj = Users(phone_number=user.get('phone_number'),
                        first_name=user.get('first_name'),
                        last_name=user.get('last_name'),
                        ads_enabled=user.get('ads_enabled'),
                        is_active=user.get('is_active'),
                        updated_at=user.get('updated_at')
                        )
        results = mongo.upsert_one(user_obj)
        return {'id': str(results.id)}
    except Exception as e:
        return {"error": str(e)}

@app.put("/users/{id}", status_code=200)
def update_user(user: dict):
        user_obj = Users(phone_number=user.get('phone_number'),
                        first_name=user.get('first_name'),
                        last_name=user.get('last_name'),
                        ads_enabled=user.get('ads_enabled'),
                        is_active=user.get('is_active'),
                        updated_at=user.get('updated_at')
                        )
        results = mongo.upsert_one(user_obj)
        return {'id': str(results.id)}
        

@app.delete("/users/phone_number/{phone_number}", status_code=200)
def delete_user_by_phone_number(phone_number: str = Path(description="Phone Number")):
    """delete user by phone number"""
    results = mongo.delete_one_by_phone_number(phone_number)
    return convert_mongo_results_to_dict(results)

@app.delete("/users/{id}", status_code=200)
def delete_user_by_object_id(id: str = Path(description="Mongo Object ID as string")):
    """delete user by object ID"""
    results = mongo.delete_one_by_object_id(id)
    return {'id': results}

handler = Mangum(app)