import re
import csv
import discord


class Trivia:
    def __init__(self, question, answers=[], correct_answer=None):
        self.question = question
        self.answers = [''] + answers
        self.correct_answer = correct_answer
    
    def as_row(self):
        return [self.question, self.correct_answer]
    
    def __str__(self):
        output = '[Trivia] ' + self.question
        if self.correct_answer:
            output += ' ' + self.correct_answer
        elif self.answers:
            output += '\n> '.join(self.answers)
        return output

UTF8 = 'utf-8'
FILE = 'trivia.csv'

def read_answer(a):
    return re.findall('\*([^*]+)\*', a)[0]

def read(qa):
    lines = qa.split('\n')
    question = lines[0].replace('*', '')
    answers = map(read_answer, lines[3:])
    return Trivia(question, list(answers))

def load_trivias():
    global trivias
    trivias = []
    with open(FILE, 'r', encoding=UTF8) as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            question, answer = row
            trivia = Trivia(question, correct_answer=answer)
            trivias.append(trivia)

def save_trivias():
    with open(FILE, 'w', newline='', encoding=UTF8) as f:
        writer = csv.writer(f, delimiter='|')
        for trivia in trivias:
            writer.writerow(trivia.as_row())

def try_answer(new_trivia):
    trivia = discord.utils.get(trivias, question=new_trivia.question)
    if trivia:
        return trivia.correct_answer

def log_new(trivia):
    trivias.append(trivia)
    save_trivias()

trivias = []
load_trivias()
save_trivias()