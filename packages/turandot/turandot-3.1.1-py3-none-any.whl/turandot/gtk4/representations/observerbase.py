from abc import ABC, abstractmethod


class DataObserver(ABC):

    @abstractmethod
    def update(self, observable: "DataObservable"):
        pass


class DataObservable(ABC):

    def __init__(self):
        self.observers: list[DataObserver] = []

    def attach(self, observer: DataObserver):
        self.observers.append(observer)

    def detach(self, observer: DataObserver):
        self.observers.remove(observer)

    def notify(self):
        for i in self.observers:
            i.update(self)
