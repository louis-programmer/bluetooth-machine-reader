from abc import ABC, abstractmethod


class BluetoothTransport(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass