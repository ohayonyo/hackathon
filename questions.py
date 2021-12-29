import random


def switch_questions(argument):
    switcher = {
        1: "How many zeros there are in the number google?\n1. 10\n2. 100\n3. 20\n4. 50",
        2: "How many olympic gold medals did Michael Phelps win?\n1. 28\n2. 25\n3. 23\n4. 21",
        3: "What is the last digit of the number 2 power of 10?",
        4: "Who is the richest man in the world?\n1. Jeff Bezos\n2. Elon Musk\n3. Bill Gates\n4. Jack Ma",
        5: "In what year did Apple start selling the Iphone 4?\n1. 2008\n2. 2009\n3. 2012\n4. 2010",
        6: "How many years has Benjamin Netanyahu been prime minister?\n1. 11\n2. 12\n3. 13\n4. 14",
        7: "Which country does not belong to the \"Abraham Accords\"?\n1. Bahrain\n2. United Arab Emirates\n3. Saudi Arabia\n4. Sudan"
    }
    return switcher.get(argument)

def switch_answers(argument):
    switcher = {
        1: "2",
        2: "3",
        3: "4",
        4: "2",
        5: "4",
        6: "2",
        7: "3"
    }
    return switcher.get(argument)

def generate_question():
    r=random.randint(1, 7)
    output=switch_questions(r)
    return (output,r)

def check_question(ans, r):
    if ans!=switch_answers(r) :
        print("wrong answer the right answer is:"+str(switch_answers(r)))
        return 0
    else:
        print("you are right!")
        return 1