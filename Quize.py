#looks like govnocode, it needs git to be redone
from logging.handlers import QueueListener
import telebot
import config
from firebase_admin import credentials
from firebase_admin import db
import IO_class

bot = telebot.TeleBot(config.token, parse_mode=None)
base = IO_class.IO_class()

#start method
@bot.message_handler(commands = ['start'])
def send_welcome(message):
    #set the state as "waiting for name"
    base.set_users_state(message.chat.id, "waiting for name")
    bot.send_message(message.chat.id, "Как тебя зовут?")

#function giving the list of quizes
def send_list_of_quizes (chat_id):
    Quizes = base.get_list_of_tests(chat_id)#we get the fill list of all quizes that we have in DB
    keyboard = telebot.types.InlineKeyboardMarkup() #make keyboard
    #go through the quizes and get mark for each user
    for Quize in Quizes:#Quize if the "id of consrete quize"       
        #we create new button with test
        button_start_text = telebot.types.InlineKeyboardButton(text=Quizes[Quize], callback_data=Quize)#we send name of the quize as callback data
        keyboard.add(button_start_text)#we add this button to the pannel
    #the keyboard send the id of the quize
    bot.send_message(chat_id, "Какой тест будете решать?", reply_markup=keyboard)

#this method is called when the user choice the test he's doing to do
@bot.callback_query_handler(func=lambda call: True) 
def callback_worker(call):
    #we ask the user if he really dicided to do the test
    bot.send_message(call.message.chat.id, f"Тест на тему: {base.get_quize_name(call.data)}")
    bot.send_message(call.message.chat.id, base.get_quize_decstiption(call.data))
    bot.send_message(call.message.chat.id, "Чтобы начать нажмите /begin, если не хотите решать этот тест нажмите /cancel")
    base.set_current_test(call.message.chat.id, call.data)#make note about the test the user is doing
    base.set_users_state(call.message.chat.id,"doing test")#switch the state        

#The user agrees to do the text
@bot.message_handler(commands = ['begin'])
def send_welcome(message):
    #send the first question, call.data is the id of quize. We start from the first question
    send_new_question(message.chat.id, base.get_current_test(message.chat.id))

#The user don't want to do the test
@bot.message_handler(commands = ['cancel'])
def send_welcome(message):
    base.set_users_state(message.chat.id,"ready to asking")#switch the state
    send_list_of_quizes(message.chat.id)#send the list of question again 

#processing of text messages
@bot.message_handler(content_types=['text'])
def got_text(message):
    #are we waiting for the name of the user
    if (base.get_users_state(message.chat.id) == "waiting for name"):#is the state is waiting for name
        base.set_users_name(message.chat.id,message.text)#message_text is user's name
        bot.send_message(message.chat.id, f"Приятно познаковиться, {message.text}! В нашей базе есть следующие тесты.")
        base.init_users_marks(message.chat.id)
        #вызываем функцию выдающую список тестов
        send_list_of_quizes(message.chat.id)
    #are we waiting for answer
    elif(base.get_users_state(message.chat.id) == "doing test"): 
        answer_processing(message.chat.id, message.text)

#this method send new question to the chat
def send_new_question(users_id, test_id, question_id=1):
    base.set_current_question(users_id,question_id)
    bot.send_message(users_id, base.get_question(test_id, question_id))

#this methos is processing user's answer
def answer_processing(users_id, users_answer):
    #that is current test and current question    
    current_test = base.get_current_test(users_id)
    current_question = base.get_current_question(users_id)
    #that is right answer for question
    right_answer=base.get_right_answer(current_test,current_question)
    #the total number of question
    number_of_questions = base.get_number_of_questions(current_test)
    current_points = base.get_current_points (users_id)
    #the +1 for points        
    if (str(right_answer)==str(users_answer)):#means that the answer is correct
        bot.send_message(users_id, "Ты прав!")
        #we give points for the right answer
        current_points = base.get_current_points(users_id)+1
        base.set_current_points(users_id, current_points)            
    else:
        bot.send_message(users_id, "Ты не прав!")
    #if this is the last question in this quize
    if(current_question==number_of_questions):
        base.set_users_state(users_id,"ready to asking")
        final_mark = current_points/base.get_max_mark(current_test)*100
        base.set_mark(users_id, current_test, final_mark)
        bot.send_message(users_id, f"все, ваша оценка: {str(final_mark)}%")
        base.set_current_points(users_id, 0)
        send_list_of_quizes(users_id)#we send the total number of questions here
    else:#if this isn't the last question
        #send new question
        send_new_question(users_id,current_test,current_question+1)
      
bot.polling()