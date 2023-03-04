#type: ignore

import flask
""" used to globally share variables without redefining/re-instancing"""
web_application : flask.Flask = None