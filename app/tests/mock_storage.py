import logging
import flask

from abc import abstractmethod


# Session handle represents endpoint for mock session calls
# add, remove, execute, etc.
class ISessionHandle:

    # handle request from session
    @abstractmethod
    def handle_transaction(**args: dict[str, str]) -> int:
        pass


# Mock storage is used to fill absence of real
# database connection, all calls to its API are logged
# and provide data as set
class MockStorage(ISessionHandle):

    class MockSession:

        def __init__(self, handle: ISessionHandle) -> None:
            self.objects = []
            self.handle = handle
        
        def add(self, instance: object, _warn: bool = True) -> None:
            logging.debug(f'adding object: {repr(object)}')
            self.objects.append(object)

        def expunge(self, instance: object) -> None:
            logging.debug(f'removing object: {repr(object)}')
            self.objects.remove(object)

        def commit(self) -> None:
            payload = self._make_payload()
            logging.debug(f'committing transaction with payload: {payload}')
            self.handle.handle_transaction()

        def _make_payload(self):
            payload = {}
            for i in range(len(self.objects)):
                payload[str(i)] = repr(self.objects[i])

    def handle_transaction(**args: dict[str, str]) -> int:
        logging.debug('received transaction')
    
    def __init__(self) -> None:
        self.session = self._make_mock_session()

    def _make_mock_session(self) -> MockSession:
        return MockStorage.MockSession(self)
    
    def __repr__(self):
        return '<InPlaceStorage class>'