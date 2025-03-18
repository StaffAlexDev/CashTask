class User:
    def __init__(self):
        self.lang = "ru"


user1 = User()


user2 = User()
user2.lang = "en"

print(user1.lang)
print(user2.lang)


