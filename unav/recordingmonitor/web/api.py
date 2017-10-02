# -*- coding: utf-8 -*-

# from flask import Flask
from flask import Blueprint
from flask_restful import Resource, Api


api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


class JobsListResource(Resource):
	def get(self):
		return [
			{'hello': 'world'}
		]


class JobsResource(Resource):
	def get(self, id):
		return {
			'id': id,
			'name': 'horse',
		}

	def patch(self, name):
		return {
			'id': 100,
			'name': name,
		}


api.add_resource(JobsListResource, '/jobs/')
api.add_resource(JobsResource, '/jobs/<int:id>')
