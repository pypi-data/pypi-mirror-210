class Student:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    def __str__(self):
        return f"{self.__name}:{self.age}"