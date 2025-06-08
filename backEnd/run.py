from flask import Flask,jsonify
from flask_cors import CORS
from src.component import User, Server
from init_db import check_and_create_database

# 检查并初始化数据库
check_and_create_database()

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.register_blueprint(User.blueprint,url_prefix='/user')
app.register_blueprint(Server.blueprint,url_prefix='/server')

@app.route("/")
async def index():
  return "Welcome"
if __name__ == '__main__':
  app.run(debug=True, port=3000,host='0.0.0.0')