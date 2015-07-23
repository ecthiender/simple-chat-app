#!/usr/bin/python

# -*- coding: utf-8 -*-
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop

import os
import json


connected_clients = []
online_users = []


class WebPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class ChatServer(tornado.websocket.WebSocketHandler):

    # get the current client dict from connected_clients list
    def get_current_client(self):
        return filter(lambda x: x['obj'] is self, connected_clients)[0]

    def open(self):
        print("New client connected")
        # nick = 'new user ' + str(len(connected_clients) + 1)
        connected_clients.append({'nick': None, 'obj': self})
        self.send_online_users()

    def on_close(self):
        print("Client disconnected")
        # client disconnected..remove the client from the existing list of
        # connected clients..
        client = self.get_current_client()
        connected_clients.remove(client)
        self.send_online_users()

    def on_message(self, data):
        print "Message recvd from client : %s" % (data)
        payload = json.loads(data)
        if payload['type'] == 'chat':
            self.broadcast_from_client(payload)
        if payload['type'] == 'nick':
            self.set_client_nick(payload)
            self.send_online_users()

    def set_client_nick(self, data):
        client = self.get_current_client()
        client['nick'] = data['nick']

    def send_online_users(self):
        payload = {'type': 'user-info',
                   'users': [client['nick'] for client in connected_clients]}
        self.broadcast_from_server(payload)

    def broadcast_from_client(self, message):
        for client in connected_clients:
            if client['obj'] is not self:
                client['obj'].write_message(message)

    def broadcast_from_server(self, message):
        for client in connected_clients:
            client['obj'].write_message(message)


if __name__ == "__main__":
    app = tornado.web.Application(
        handlers=[
            (r'/', WebPageHandler),
            (r'/chat', ChatServer)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8080)
    print("Chat server started..")
    tornado.ioloop.IOLoop.instance().start()
