#!/usr/bin/env python3

import os
import sys
import time
import json
import struct
import signal
import socket
import inspect


def init(*args, **kwargs):
    return Murloc(*args, **kwargs)


class Murloc:
    def __init__(
        self,
        version="1.0.0",
        host=socket.inet_ntoa(struct.pack("!L", socket.INADDR_LOOPBACK)),
        port=8048,
        name="murloc",
        mode="default",
        url="Aaaaaughibbrgubugbugrguburgle!",
        methods=dict(),
        logfile=None,
    ):
        self.version = version
        self.host = host
        self.port = port
        self.name = name
        self.mode = mode
        self.url = url
        self.methods = methods
        self.logfile = logfile
        self.pid = os.getpid()
        self.boot = inspect.cleandoc(
            f"""\n
                    
                 ___
                /\  \ 
               /::\  \       {self.name} {self.version}
              /:/\:\  \ 
             /:/  \:\  \ 
            /:/__/ \:\__\    Running in {self.mode} mode
            \:\  \ /:/  /    Port: {self.port:<4}
             \:\  /:/  /     PID:  {self.pid:<4}
              \:\/:/  / 
               \::/  /             {self.url}
                \/__/ 
                    """
        )

    def log(self, s):
        date = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.mode == "debug":
            n = inspect.currentframe().f_back.f_lineno
            msg = f"[{date}] [{__file__}:{n}] [{os.getpid()}] {s}"
        else:
            msg = f"[{date}] [{os.getpid()}] {s}"
        if not self.logfile:
            print(msg)
        else:
            try:
                with open(self.logfile, "a") as f:
                    f.write(f"{msg}\n")
            except:
                print(msg)

    def handle(self, method, params):
        if method not in self.methods:
            return '{"err":1,"data":"method not defined"}'
        return self.methods[method](self, params)

    def parse(self, req):
        try:
            js = json.loads(req)
        except Exception as e:
            if self.mode == "debug":
                self.log(f"json.loads: {req}: {e}")
            return '{"err":1,"data":"invalid json request"}'
        try:
            method = js["method"]
        except:
            return '{"err":1,"data":"request lacks method"}'
        try:
            params = js["params"]
        except:
            return '{"err":1,"data":"request lacks params"}'
        return self.handle(method, params)

    def recvall(self, conn):
        data = b""
        while True:
            packet = conn.recv(1024)
            data += packet
            if len(packet) < 1024:
                break
        return data

    def handle_connection(self, conn, addr):
        while True:
            try:
                data = self.recvall(conn)
            except Exception as e:
                if self.mode == "debug":
                    self.log(f"recv: {e}")
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                break
            if not data:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
                break
            req = data.decode().strip()
            res = f"{self.parse(req)}\n"
            conn.sendall(res.encode())

    def handle_sigint(self, sig, frame):
        print()
        sys.exit(0)

    def handle_sigchild(self, sig, frame):
        os.waitpid(-1, os.WNOHANG)

    def listen(self):
        self.log(self.boot)
        signal.signal(signal.SIGINT, self.handle_sigint)
        signal.signal(signal.SIGCHLD, self.handle_sigchild)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen()
        self.log(f"Listening at {self.host}:{self.port}")
        while True:
            try:
                conn, addr = sock.accept()
            except Exception as e:
                if self.mode == "debug":
                    self.log(f"accept: {e}")
                break
            conn.settimeout(10)
            # Fork to handle the new connection; this allows us to use
            # os.system() etc, which is problematic within a thread.
            pid = os.fork()
            if pid == 0:
                self.log(f"Connection from {addr}")
                self.handle_connection(conn, addr)
                sys.exit(0)
            else:
                continue
