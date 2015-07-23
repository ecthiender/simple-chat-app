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
    def open(self):
        print("Websocket opened")
        nick = 'new user ' + str(len(connected_clients) + 1)
        connected_clients.append({'nick': nick, 'obj': self})
        self.send_online_users()

    def on_close(self):
        print("Websocket closed")
        client = filter(lambda x: x['obj'] is self, connected_clients)[0]
        connected_clients.remove(client)
        self.send_online_users()

    def on_message(self, data):
        print "Message recvd from client : %s" % (data)
        payload = json.loads(data)
        if payload['type'] == 'chat':
            for client in connected_clients:
                if client['obj'] is not self:
                    client['obj'].write_message(data)
        if payload['type'] == 'nick':
            client = filter(lambda x: x['obj'] is self, connected_clients)[0]
            print client
            client['nick'] = payload['nick']
            self.send_online_users()

    def send_online_users(self):
        payload = {'type': 'user-info',
                   'users': [client['nick'] for client in connected_clients]}
        for client in connected_clients:
            client['obj'].write_message(payload)


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
