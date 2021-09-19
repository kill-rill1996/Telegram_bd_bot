import config


class Singleton(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Session(metaclass=Singleton):

    def __init__(self):
        self.next_number = [1]
        self.points = 0
        self.quest_number = 0
        self.question = None
        self.cart = []
        self.sold_products = []

    def get_next_number_of_photo(self):
        number = self.next_number[-1]
        self.next_number.append(number + 1)
        return number

    def add_points(self):
        self.points += 10

    def get_next_question(self):
        question = config.QUESTIONS[self.quest_number]
        self.quest_number += 1
        return question

    def add_to_cart(self, prod):
        if self.points >= prod['price']:
            self.points -= prod['price']
            self.cart.append(prod)
            return True


# class CommandInvoker:
#
#     def __init__(self):
#         self._commands_list = []
#
#     def store_command(self, command):
#         self._commands_list.append(command)
#
#     def execute_commands(self):
#         for command in self._commands_list:
#             command()
#
# class ParamClass:
#
#     def __init__(self, param):
#         self.param = param
#
#     def __call__(self, *args, **kwargs):
#         print(f'console {self.param}')
#
#
# def sone_commad():
#     param = input('Input the param:')
#     print(param)
#
#
# commands_invoker = CommandInvoker()
#
# commands_invoker.store_command(sone_commad)
# commands_invoker.store_command(sone_commad)
# commands_invoker.store_command(sone_commad)
# commands_invoker.execute_commands()
