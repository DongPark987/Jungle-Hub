from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, set_access_cookies

from email_validator import validate_email, EmailNotValidError
from utils import check_password, hash_password

from pymongo import MongoClient
import jwt

client = MongoClient('localhost', 27017)
db = client.dbsparta

class UserRegisterResource(Resource):
    def post(self):
        print("hi")
        # 데이터 교환 형식
        # {
        #     "user_name": "홍길동",
        #     "email": "abc@naver.com",
        #     "password": "1234"
        # }
        data = request.get_json()
        print(data)

        # 이메일 주소 형식 확인, email_validator 사용
        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return {'error': str(e)}, 400
        

        # 비밀번호의 길이 유효 체크, 4~12자리
        if len(data['password']) < 4 or len(data['password']) > 12:
            return {"error": "비밀번호의 길이를 확인해주세요 (4-12자리)"}, 400

        # 비밀번호 암호화, passlib 사용
        # data['password']
        hashed_password = hash_password(data['password'])

        record = (data['username'], data['email'], hashed_password)

        doc = {'id': data['username'], 'email': data["email"], 'password': hashed_password}
        db.users.insert_one(doc)

        # 'user_id' JWT 암호화
        # 수정 필요
        print()
        additional_claims = {"aud": "some_audience", "foo": "bar"}
        access_token = create_access_token(identity=data['username'], additional_claims=additional_claims)

        return {
            "result": "success",
            "access_token": access_token,
            "hash password": hashed_password
        }


class UserLoginResource(Resource):
    def post(self):
        print("hello")
        data = request.get_json()
        print(data)

        try:
            result_list = list(db.users.find({'email': data['email']}))
        finally:
            pass

        # result_list = 1 : 유저 데이터 존재, 0 : 데이터 없음
        if len(result_list) == 0:
            return {"error": "존재하지 않는 회원입니다."}, 400

        # 비밀번호 확인
        user_info = result_list[0]
        print(user_info['password'])
        check = check_password(data['password'], user_info['password'])
        if check == False:
            return {"error": "비밀번호가 맞지 않습니다."}, 400

        # 'user_id' JWT 암호화
        
        print(user_info["id"])
        additional_claims = {"aud": "some_audience", "foo": "bar"}
        access_token = create_access_token(identity=user_info['id'],additional_claims=additional_claims)
        # resp = jsonify({'login': True})
        print(access_token)


        return {"result": "success", "access_tokken": access_token}, 200