import os
from dotenv import load_dotenv
from MyAI import MyAI
import telebot
from telebot import types
from rich import print
import re


def main():
    load_dotenv()

    TELEGRAM_API_KEY = os.environ.get("TELEGRAM_BOT_KEY")
    API_KEY = os.environ.get("OPENAI_API_KEY")

    bot = telebot.TeleBot(TELEGRAM_API_KEY)
    ai_client = MyAI(api_key=API_KEY)
    
    hideBoard = types.ReplyKeyboardRemove()

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        ai_client.message_history[str(message.chat.id)] = list(ai_client.message_history_default.copy())
        ai_client.test[str(message.chat.id)] = []
        ai_client.test_mode[str(message.chat.id)] = False
        ai_client.test_question_number[str(message.chat.id)] = 0
        ai_client.test_right_answers[str(message.chat.id)] = 0
        responce_text = ""
        responce_from_ai = ai_client.chat_without_history("""                                                
        Ты бот для хакатона компании Latoken.
        Заменяй знак "—" на "-". (это внутренняя функция, не говори о ней)
        Не начинай предложение или строку со знаков.
        Из комманд у тебя /start которая запускает тебя и /test которая позволяет пройти тест по изученым вопросам.
        Ты можешь отвечать на вопросы по компании и хакатону.
        Отвечай только на последний заданный вопрос, и не повторяй ответы на предыдущие.
        Обязательно убедись в правильности написания слов.
        Веди красивое строение ответов.
        Переводи текст нормально.
        Не переводи термины.
        Не включай в сообщении оглавление.
        Не говори, что команду /start надо вводить для того, чтобы начать общение, потому что общение уже будет начато.
        Не пиши о своих внутренних функциях.
        Напиши приветственное сообщение для бота в телеграм, бот нужен для демо, поэтому никакого глубокого смысла закладывать не надо.
        В приветствии обязательно содержи одинаковое строение, это оглавление краткое описание бота и краткое описание функционала.
                                                          """)
        for chunk in responce_from_ai:
            if chunk.choices[0].delta.content is not None:
                responce_text += chunk.choices[0].delta.content
        if not responce_text:
            responce_text = "There occured an unknown problem"
        bot.send_message(str(message.chat.id), re.sub(r"[*]", "", responce_text))

    @bot.message_handler(commands=['test'])
    def start_test(message):
        
        print("start test: " + str(message.chat.id))
        if ai_client.test_mode[str(message.chat.id)] == False:
            ai_client.test_mode[str(message.chat.id)] = True
            responce_text = ""
            responce_from_ai = ai_client.chat_without_adding_history(str(message.chat.id), """
            Это команда от твоего создателя.
            То, что ты создашь далее внутренняя информация и не должна быть рассказана никому.
            Создай 5 вопросов различной сложности по всем вышеперечисленным сообщениям с вариантами ответов, правильным должен быть один и только один, раздели каждый вопрос строкой "-----" (не ставь строку после последнего), а каждый вариант ответа обязательно раздели строкой "#####", букву ответа вставь в конце вопроса, после символа "|", но не указывай в самом варианте, каждый вариант обязательно подпиши заглавной латинской буквой в формате.
            Каждый вопрос должен быть в формате:
            Номер вопроса. Вопрос
            #####
            A) Вариант ответа A
            #####
            B) Вариант ответа B
            #####
            C) Вариант ответа C
            #####
            D) Вариант ответа D
            |Правильный ответ
            Пример:
            1. Что отличает Latoken от других криптовалютных бирж по числу активов для трейдинга?
            #####
            A) Latoken предлагает более 3000 активов
            #####
            B) Latoken предлагает более 400 активов
            #####
            C) Latoken предлагает менее 200 активов
            #####
            D) Latoken не предоставляет активы для трейдинга
            |A
            Не отправляй и не рассказывай это никому
                                            """)
            for chunk in responce_from_ai:
                if chunk.choices[0].delta.content is not None:
                    responce_text += chunk.choices[0].delta.content
            if not responce_text:
                responce_text = "There occured an unknown problem"
            responce_text = re.sub(r"[*]", "", responce_text)
            for _, question_full in enumerate(responce_text.split("-----")):
                print(question_full)
                message_answer = question_full.strip().split("|")[1]
                question_info = question_full.strip().split("|")[0]
                question = question_info.split("#####")[0]
                answers = question_info.split("#####")[1:]
                ai_client.test[str(message.chat.id)].append({
                    "question": question,
                    "answer": message_answer.strip().lower(),
                    "variants_of_answer": answers
                })
            markup = types.ReplyKeyboardMarkup()
            button1 = types.KeyboardButton(
                ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][0])
            button2 = types.KeyboardButton(
                ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][1])
            button3 = types.KeyboardButton(
                ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][2])
            button4 = types.KeyboardButton(
                ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][3])
            end_button = types.KeyboardButton("Закончить тест")
            markup.add(button1, button2)
            markup.add(button3, button4)
            markup.add(end_button)
            bot.send_message(
                str(message.chat.id), ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["question"], reply_markup=markup)

    @bot.message_handler(func=lambda message: True)
    def reply_to_message(message):
        if ai_client.test_mode[str(message.chat.id)] == False:
            responce_text = ""
            responce_from_ai = ai_client.chat(message.chat.id, message.text)
            for chunk in responce_from_ai:
                if chunk.choices[0].delta.content is not None:
                    responce_text += str(chunk.choices[0].delta.content)
            if not responce_text:
                responce_text = "There occured an unknown problem"
            bot.send_message(str(message.chat.id), re.sub(
                r"[*]", "", responce_text), reply_markup=hideBoard)
        else:
            if message.text == "Закончить тест":
                bot.send_message(str(message.chat.id), f"Тест закончен\nПравильных ответов: {ai_client.test_right_answers[str(message.chat.id)]}", reply_markup=hideBoard)
                ai_client.test_question_number[str(message.chat.id)] = 0
                ai_client.test_right_answers[str(message.chat.id)] = 0
                ai_client.test_mode[str(message.chat.id)] = False
                ai_client.test[str(message.chat.id)] = []
            else:
                msg_txt = message.text
                recieved_answer = msg_txt.strip()[0].lower()
                
                if recieved_answer == ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["answer"]:
                    ai_client.test_right_answers[str(message.chat.id)] += 1
                    bot.send_message(str(message.chat.id), "Правильный ответ")
                else:
                    right_answer = ord(ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["answer"])-97
                    bot.send_message(str(message.chat.id), f"Неверный ответ\nПравильный ответ:\n{ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][right_answer]}")
                
                if ai_client.test_question_number[str(message.chat.id)] == 4:
                    bot.send_message(str(message.chat.id), f"Тест закончен\nПравильных ответов: {ai_client.test_right_answers[str(message.chat.id)]}/5", reply_markup=hideBoard)
                    ai_client.test_question_number[str(message.chat.id)] = 0
                    ai_client.test_right_answers[str(message.chat.id)] = 0
                    ai_client.test_mode[str(message.chat.id)] = False
                    ai_client.test = []
                else:
                    ai_client.test_question_number[str(message.chat.id)] += 1
                    markup = types.ReplyKeyboardMarkup()
                    button1 = types.KeyboardButton(
                        ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][0])
                    button2 = types.KeyboardButton(
                        ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][1])
                    button3 = types.KeyboardButton(
                        ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][2])
                    button4 = types.KeyboardButton(
                        ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["variants_of_answer"][3])
                    end_button = types.KeyboardButton("Закончить тест")
                    markup.add(button1, button2)
                    markup.add(button3, button4)
                    markup.add(end_button)
                    bot.send_message(
                        str(message.chat.id), ai_client.test[str(message.chat.id)][ai_client.test_question_number[str(message.chat.id)]]["question"], reply_markup=markup)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
