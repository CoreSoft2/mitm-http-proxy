import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

import threading
import SimpleHTTPServer
import SocketServer

from selenium import webdriver

import MitmHttpProxy

global more_requests
more_requests = True


def keep_running():
    global more_requests
    print "keep running", more_requests
    return more_requests


class RunRequests:
    def run_while_true(self):
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        server = SocketServer.TCPServer(('127.0.0.1', 8000), Handler)

        while keep_running():
            server.handle_request()
        print "Done Handling"


def run_server():
    print "Starting server"
    server = RunRequests()
    thread = threading.Thread(target=server.run_while_true)
    thread.deamon = True
    thread.start()
    print "Server running"
    return thread


def kill_server(server):
    if server is None:
        return
    print "Shuting down server"
    print server.isAlive()
    print "Done shutting down server"


def run_proxy():
    ip = MitmHttpProxy.InjectionProxy(
        '127.0.0.1', 8877,
        '127.0.0.1', 8000)
    thread = threading.Thread(target=ip.run_loop)
    thread.deamon = True
    thread.start()
    print "Running Proxy"
    return ip


def kill_proxy(proxy):
    print "Killing Proxy"


def run_selenium():
    proxy_addr = '127.0.0.1'
    proxy_port = '8877'

    profile = webdriver.FirefoxProfile()
    # manual proxy
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", proxy_addr)
    profile.set_preference("network.proxy.http_port", int(proxy_port))
    profile.set_preference("network.proxy.no_proxies_on", "")
    driver = webdriver.Firefox(firefox_profile=profile)
    kill_server(None)

    error = 0
    try:
        driver.get('http://127.0.0.1:8000/tests/test-pages/hello-world.html')
        elm = driver.find_element_by_id('injected')
        assert elm.text == 'injected'
    except Exception, e:
        print e
        error = 1
    finally:
        driver.get('http://127.0.0.1:8000/tests/test-pages/hello-world.html')
        driver.quit()

    return error


if __name__ == '__main__':
    test_result = 1
    server = None
    proxy = None
    try:
        server = run_server()
        proxy = run_proxy()
        test_result = run_selenium()
    except Exception, e:
        print e
    finally:

        kill_server(server)
        kill_proxy(proxy)

    exit(test_result)