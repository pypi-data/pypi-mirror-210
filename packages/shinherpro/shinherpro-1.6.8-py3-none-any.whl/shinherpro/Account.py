
class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.grades = None
        self.credit = None
        self.userphoto = None

    def setGrades(self, grades):
        self.grades = grades

    def setUsername(self, username):
        self.username = username

    def setPassword(self, password):
        self.password = password

    def setCredit(self, credit):
        self.credit = credit

    def setUserPhoto(self, userphoto):
        self.userphoto = userphoto

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getGrades(self):
        return self.grades

    def getCredit(self):
        return self.credit

    def getUserPhoto(self):
        return self.userphoto
