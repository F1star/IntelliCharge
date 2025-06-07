__all__ = ['blueprint']
from flask import Blueprint, request, jsonify
import pymysql
from ...dataStructure.User import *
from flask_cors import CORS

blueprint = Blueprint('server', __name__)

@blueprint.route('/', methods=['POST', 'GET'])
async def index():
    return "welcome to use server system"

