from flask import Flask, render_template, request
from newspaper import Article
import random
import string 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import numpy as np
import warnings
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


app = Flask(__name__)
app.static_folder = 'static'

nltk.download('punkt', quiet=True)







def greeting_response(text):
  text = text.lower()
  bot_greetings = ["howdy","hi", "hey", "what's good",  "hello","hey there","Bonjour!","Salut","Allô"]
  #Greeting input from the user
  user_greetings = ["hi", "hello",  "hola", "greetings",  "wassup","hey","Bonjour!","Salut","Allô"] 

  for word in text.split():
    if word in user_greetings:
      return random.choice(bot_greetings)




def index_sort(list_var):
    length = len(list_var)
    list_index = list(range(0, length))
    x  = list_var
    for i in range(length):
        for j in range(length):
            if x[list_index[i]] > x[list_index[j]]:
                temp = list_index[i]
                list_index[i] = list_index[j]
                list_index[j] = temp
    return list_index





# Generate the response
def bot_response(user_input,sentence_list):
    user_input = user_input.lower()
    sentence_list.append(user_input)
    bot_response=''
    cm = CountVectorizer().fit_transform(sentence_list)
    similarity_scores = cosine_similarity(cm[-1], cm)
    flatten = similarity_scores.flatten()
    index = index_sort(flatten)
    index = index[1:]
    response_flag=0

    j = 0
    for i in range(0, len(index)):
      if flatten[index[i]] > 0.0:
        bot_response = bot_response+' '+sentence_list[index[i]]
        response_flag = 1
        j = j+1
      if j > 2:
        break  
    if(response_flag==0):

        return None
    sentence_list.remove(user_input)
    bot_response = GoogleTranslator(source='english', target='french').translate(bot_response)   
    return bot_response



def Search(query):
    search_result_list = list(search(query, tld="co.in", num=10, stop=10, pause=1))
    return search_result_list

def chatbot_query(query, index=0):
    try:
        fallback = 'Sorry, I cannot think of a reply for that.'
        search_result_list = list(search(query, tld="co.in", num=10, stop=3, pause=1))
        
        page = requests.get(search_result_list[index])
        #tree = html.fromstring(page.content)
        #print(tree)
        
        soup = BeautifulSoup(page.content, features="lxml")
        #print(soup)
        #print(page.text)
        article_text = ''
        article = soup.findAll('p')
        #print(article)
        for element in article:
            #print(element)
            article_text += '\n' + ''.join(element.findAll(text = True))
        #article_text = article_text.replace('\n', '')
        if len(article_text) !=0:
            return article_text
        else:
            return chatbot_query(query,index+1)
    except IndexError:
        return fallback
def tokened_text(text):
    #print(link)
    #article = Article(link)
    #article.download() 
    #article.parse() 
    #article.nlp()
    #print(article.text)
    sentence_list = nltk.sent_tokenize(text)
    #print(sentence_list)
    return sentence_list
    






@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    user_input_french = request.args.get('msg')
    bot2 = Bot(user_input_french)
    return bot2
    




def Bot(user_input_french):
    exit_list = ['exit', 'see you later','bye', 'quit', 'break']
    while(True):
        user_input = GoogleTranslator(source='french', target='english').translate(user_input_french)
        if(user_input.lower() in exit_list):
          return "Chat with you later !"
          break
        else:
          if(greeting_response(user_input)!= None):
            return greeting_response(user_input)
          else:              
                i=0
                link=Search(user_input)
                #print(link)
                if 'youtube' in user_input.lower() or 'link' in user_input.lower() or 'video' in user_input.lower():
                    return link[0]
                else:                
                    while True:
                        #print(link[i])
                        lis=tokened_text(link[i])
                        if bot_response(user_input, lis) != None:
                            break
                        i+=1
                    return bot_response(user_input,lis)
                
                
if __name__ == "__main__":
    app.run()


