import math
from channels.generic.websocket import WebsocketConsumer
import json


PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]

def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("CONNECT")
        self.accept()

    def disconnect(self, close_code):
        print("DISCONNECT")
        pass

    def receive(self, text_data):
        print("DATA", text_data)
        #text_data_json = json.loads(text_data)
        #message = text_data_json['message']

        #self.send(text_data=json.dumps({
        #    'message': message
        #}))
        #request = self.factory.get("/")
        from django.test.client import RequestFactory

        #import pdb;pdb.set_trace()
        from django import template
        request = RequestFactory().get("/")
        t = template.Template("""{% load mote_tags %}
            {% render "base.browser.atoms.button" %}"""
        )
        result = t.render(template.Context({
            "request": request
        }))
        #self.send(text_data=result)

        for i in range(10):
            for prime in PRIMES:
                result = str(is_prime(prime))
        self.send(text_data=json.dumps({
            'message': result
        }))

