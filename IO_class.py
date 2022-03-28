import config
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class IO_class:
    #Working with Quizes' Table
    def __init__(self):
        cred = credentials.Certificate(config.base_cred)
        firebase_admin.initialize_app(cred, {
            'databaseURL': config.databaseURL
        })
        self.__ref = db.reference('Quize_project')

    def get_quize_name(self, quize_id):
        return self.__ref.child(f"Quizes/{quize_id}/name/").get()
    
    def get_quize_decstiption(self, quize_id):
        return self.__ref.child(f"Quizes/{quize_id}/description").get()

    def get_question(self, quize_id, question_id):
        question = self.__ref.child(f"Quizes/{quize_id}/Questions/{str(question_id)}/question").get()
        return question

    def get_right_answer(self, quize_id, question_id):
        answer = self.__ref.child(f"Quizes/{quize_id}/Questions/{str(question_id)}/answer").get()
        return answer

    def get_point(self, quize_id, question_id):
        point = self.__ref.child(f"Quizes/{quize_id}/Questions/{str(question_id)}/point").get()
        return point

    def get_number_of_questions(self, quize_id):
        number = len(self.__ref.child(f"Quizes/{quize_id}/Questions").get())-1 #get the number of questions
        return number

    def get_max_mark(self, cuize_id):
        return self.__ref.child(f"Quizes/{cuize_id}/max mark").get()

    #Working with users' table
    def init_users_marks(self, users_id):
        #we create the branch in DB with user's data
        Quizes = self.__ref.child("Quizes").get()#we get the list of all quizes we have in DB
        #if the user is the first time here we make his marks = 0
        for Quize in Quizes:
            data = {
                str(Quize):{
                    "mark": 0,                    
                }
            }
            self.__ref.child(f"users/{str(users_id)}/Marks/").update(data)
        self.__ref.child(f"users/{str(users_id)}").update({"state":"ready to asking"})#swich state to ready to asking
        self.__ref.child(f"users/{str(users_id)}").update({"current points": 0})
    
    def set_users_name(self, users_id, users_name):
        self.__ref.child(f"users/{str(users_id)}").update({"name": users_name})
    
    def set_users_state(self, users_id, state):
        self.__ref.child(f"users/{str(users_id)}").update({"state": state})
    
    def get_users_state(self, users_id):
        users_state = self.__ref.child(f"users/{str(users_id)}/state").get()
        return users_state

    def set_current_test(self, users_id, current_text):
        self.__ref.child(f"users/{str(users_id)}").update({"current test": current_text})
    
    def get_current_test(self, users_id):
        current_test = self.__ref.child(f"users/{str(users_id)}/current test").get()
        return current_test

    def set_current_question(self, users_id, current_question):
        self.__ref.child(f"users/{str(users_id)}").update({"current question": current_question})

    def get_current_question(self, users_id):
        current_question = self.__ref.child(f"users/{str(users_id)}/current question").get()
        return current_question

    def set_mark(self, users_id, quize_id, mark):
        self.__ref.child(f"users/{str(users_id)}/Marks/{quize_id}").update({"mark": mark})
    
    #get mark of concrete test of concrete user
    def get_mark(self, users_id, quize_id, mark):
        return self.__ref.child(f"users/{str(users_id)}/Marks/{quize_id}mark").get()

    #get the sum of points those have the user in this test
    def get_current_points(self, users_id):
        return self.__ref.child(f"users/{str(users_id)}/current points").get()

    #set the cum of points
    def set_current_points(self, users_id, points):
        self.__ref.child(f"users/{str(users_id)}").update({"current points": points})

    def get_list_of_tests(self, users_id):
        #список результатов пользователя
        Quizes_results = self.__ref.child(f"users/{str(users_id)}").get()
        #сами тесты
        Quizes = self.__ref.child("Quizes").get()
        message = dict()
        #бежим по тестам и извлекаем для каждого оценку пользователя
        for Quize in Quizes:       
            answer_text=""#this var will contain the full name of the test and the mark of it
            name = Quizes[Quize]["name"]            
            if Quize in Quizes_results["Marks"]:#is there this text in the user's mark
                mark = str(Quizes_results["Marks"][Quize]["mark"])
                answer_text=f"Тест на тему: {name}. Ваша предыдущая оценка: {mark}%."
            else:#if this quis is new in list and the user's mark list doesn't contein it we create the item
                data = {
                    str(Quize):{
                        "mark": 0,                    
                    }
                }
                self.__ref.child(f"users/{str(users_id)}/Marks/").update(data)                
                answer_text=f"Тест на тему: {name}:. Ваша оценка: "
            message.update({Quize:answer_text})
        return message