from specmatic.core.specmatic_stub import SpecmaticStub
from specmatic.core.specmatic_test import SpecmaticTest
from specmatic.generators.pytest_generator import PyTestGenerator
from specmatic.servers.asgi_server import ASGIServer
from specmatic.servers.wsgi_server import WSGIServer
from specmatic.utils import get_junit_report_file_path


class Specmatic:

    @classmethod
    def start_stub(cls, host: str = '127.0.0.1', port: int = 0, project_root: str = '', contract_file_path: str = '',
                   specmatic_json_file_path: str = '',
                   ):
        stub = None
        try:
            stub = SpecmaticStub(host, port, project_root, contract_file_path, specmatic_json_file_path)
            return stub
        except Exception as e:
            if stub is not None:
                stub.stop()
            print(f"Error: {e}")
            raise e

    @classmethod
    def test(cls, test_class, host: str = '127.0.0.1', port: int = 0, project_root: str = '',
             contract_file_path: str = '',
             specmatic_json_file_path: str = ''
             ):
        try:
            SpecmaticTest(host, port, project_root, contract_file_path, specmatic_json_file_path).run()
            PyTestGenerator(test_class, get_junit_report_file_path()).generate()
        except Exception as e:
            print(f"Error: {e}")
            raise e

    @classmethod
    def start_wsgi_app(cls, app, host: str = '127.0.0.1', port: int = 0):
        app_server = None
        try:
            app_server = WSGIServer(app, host, port)
            app_server.start()
            return app_server
        except Exception as e:
            if app_server is not None:
                app_server.stop()
            print(f"Error: {e}")
            raise e

    @classmethod
    def start_asgi_app(cls, app, host: str = '127.0.0.1', port: int = 0):
        app_server = None
        try:
            app_server = ASGIServer(app, host, port)
            app_server.start()
            return app_server
        except Exception as e:
            if app_server is not None:
                app_server.stop()
            print(f"Error: {e}")
            raise e
