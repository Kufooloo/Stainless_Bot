class Server:
    """Module handles scores and information for the NYT crossword"""
    def __init__(self) -> None:
        self.users = {}#dict of all the users
        self.days = {}#dict of all the days
    def add_score(self, userid: int, date: str, time: int) -> str:
        """Adds a score to the user"""
        if self.users.get(userid) is None:#create new user
            user = User(userid, 0, 0, {})
            self.users.update({userid:user})
        user = self.users.get(userid)
        prev_score = user.add_day(date, time)
        #portion of code that handles days
        if self.days.get(date) is None:
            day = Day()
            self.days.update({date:day})
            print("added date")
        day = self.days.get(date)
        day.add_user(userid, time)
        print(self.days)
        if prev_score == 0:
            return f"Score: {time} Date: {date}"
        return f"Previous Score: {prev_score} New Score: {time} Date: {date}"
    def get_scoreboard(self) -> dict:
        """Returns a dict with the score and then the user ID"""
        score_sort = {}
        for user_id, user in self.users.items():
            print(self.days)
            output = user.get_total_time()
            print(output)
            total_score = self.get_score(user_id)
            days_participated = int(user.get_num_days())
            avg_score = int(total_score) / int(days_participated)
            print(total_score)
            score_sort.update({avg_score:user_id})
        return score_sort
    def user_score(self, userid: int) -> str:
        """Returns an individual users score"""
        user = self.users.get(userid)
        if user is None:
            return "No User with that name"
        day_dict = user.get_days_participated()
        message = f"User's ranked score is {self.get_score(userid)}\n"
        for day, score in day_dict.items():
            message += f"User scored {score} on {day}\n"
        return message
    def get_score(self, userid: int) -> int:
        """Returns the ranked score of the User"""
        total_score = 0
        day_list = []
        user = self.users.get(userid)
        day_list = user.get_days_participated_list()
        for day in day_list:
            total_score += self.days[day].get_score(userid)
        return total_score
    def get_avg_time(self, userid: int) -> int:
        """Returns the avg time of given user"""
        user = self.users.get(userid)
        if user is None:
            return 0
        return user.get_avg_time()
    def dump(self) -> list:
        """Returns all the vars of all objects in server as a string"""
        message = []
        message.append("Users: \n")
        for key, contents in self.users.items():
            message.append(f"key: {key} with contents: \n")
            message.append(f"{vars(contents)}\n")
        message.append("Days: \n")
        for key, contents in self.days.items():
            message.append(f"key: {key} with contents: \n")
            message.append(f"{vars(contents)}\n")
        return message
    def remove_score(self, userid: int, date: str) -> str:
        """Removes score from given day and user"""
        user = self.users.get(userid)
        if user is None:
            return "This user does not exist"
        error_user = user.remove_day(date)
        if error_user == 0:
            return "This user did not participate on given day"
        day = self.days.get(date)
        day.remove_score(userid)
        return f"Success! Removed {date} with time {error_user}"
    def recalc_score(self):
        """Recalculates the score for all users from data in user class"""
        for userid, content in self.users.items():
            days = content.get_days_participated()
            for day, score in days.items():
                temp = self.days.get(day)
                temp.add_user(int(userid), int(score))
        return
                





class User:
    """Contains information on the user and their score"""
    def __init__(self, userid, num_days, total_time, days_participated) -> None:
        self.userid = userid #userid of the userclass
        self.num_days = num_days #num of days the user has participated in total
        self.total_time = total_time #the total amount of time the user has participated in
        self.days_participated = days_participated #a dictionary with all the dates with a score
    def add_day(self, date: str, time: int) -> int:
        """Adds a day to the user"""
        previous_time = self.days_participated.get(date, 0)
        total = self.total_time - previous_time
        self.days_participated.update({date:time})
        self.num_days = len(self.days_participated)
        total += int(time)
        self.total_time = total
        if previous_time != 0:
            return previous_time
        return 0



    def remove_day(self, date: str) -> int:
        """Removes given date from the user"""
        contents = self.days_participated.get(date)
        if contents is None:
            return 0
        self.num_days -= 1
        self.total_time -= int(contents)
        self.days_participated.pop(date)
        return contents
    def get_num_days(self) -> int:
        return self.num_days
    def get_total_time(self) -> int:
        return self.total_time
    def get_days_participated(self) -> int:
        return self.days_participated
    def get_days_participated_list(self) -> list:
        return list(self.days_participated.keys())
    def get_avg_time(self) -> int:
        return self.total_time / self.num_days

class Day:
    """Contains information on all users who submitted a score on a day"""
    def __init__(self) -> None:
        self.users = {}
        self.scores = {}
    def add_user(self, userid: int, time: int) -> None:
        """Adds a user and their score to the day"""
        self.users.update({userid:int(time)})
        self.update()
        return
    def update(self) -> None:
        """Updates the rankings for the day"""
        temp = list(self.users.keys())
        lowest = temp[0]
        lowest_time = self.users.get(lowest)
        print(f"first lowest time {lowest_time}")
        for i in self.users:
            test = self.users.get(i)
            if int(lowest_time) > int(test):
                lowest = i
                lowest_time = test
                print(f"New lowest time {lowest_time}")
        for i in self.users:
            score = (int(lowest_time)/int(self.users.get(i)))  * 100
            self.scores.update({i:score})
        return
    def get_score(self, userid: int) -> int:
        """Returns the ranked score of the given user"""
        return self.scores.get(userid)
    def remove_score(self, userid: int) -> None:
        self.users.pop(userid)
        self.scores.pop(userid)
        return
