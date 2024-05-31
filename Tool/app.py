'''Author: Aditya Nerpagar, Zhou Xu and ChatGPT'''
from flask import Flask, render_template, request, Response
import time
import json
import requests

app = Flask(__name__)

# This function will generate output on the website
def generate_feedback(topic, text_type, text):
    systems = { ##below system promts are used to generate feedback based on the type of feedback required
        "grammar": (
            "You are a funny English teacher for intermediate learners. You will answer according to level of student. Begin with  \
                1. Check grammar of the given sentence in detail.\
                2. suggest commonly used phrases or good to use phrases \
                3. give tips for improving writing skills"
        ),
        "vocabulary": (
            "You are everyone's favourite teacher with vast knowledge of vocabulary. You will answer according to level of student. Begin with\
                1. you will suggest better vocabulary based on the input wherever necessary.\
                2. you will explain why suggested words are better and also some fun fact related to that word."
        ),
        "feedback": (
            "You are a critic of English language. Your are brutally honest. you will \
                1. Critic the essay.\
                2. explain how the essay could be improved.\
                3. suggest how the essay could get 9 point score on IELTS."
        ),
        "sample": (
            "You are AI IELTS essay checking machine. You will  \
                1. Give an IELTS based sample essay based on given topic "
                # 2. grade the given essay based on IELTS marking scheme."
        )
    }
    
    system = systems.get(text_type, systems["feedback"])  # Default to "feedback" if type not found
    prompt = f"Topic: {topic}\nType: {text_type}\n\n{text}" # Prompt for the model from website
    
    url = "http://localhost:11434/api/generate"  

    #payload for the model
    payload = { 
        "model": "llama3",
        "system": system,
        "prompt": prompt, 
        "stream": True,
        "repeat_penalty": 0.9,
        #temperature if else loop
        "temperature": 0.6
    }

    def event_stream(): #function to stream the output from the model
        for i in range(1, 101): #progress bar
            time.sleep(0.001)
            yield f"data: {json.dumps({'progress': i})}\n\n"
        try: #try block to get the response from the model
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()
            response_content = "" #variable to store the response
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    decoded_chunk = chunk.decode()
                    json_chunk = json.loads(decoded_chunk) #load the response in json format
                    if 'response' in json_chunk:
                        response_content += json_chunk['response']
                        if response_content: 
                            yield f"data: {json.dumps({'response': response_content})}\n\n"
        #except block to handle exceptions
        except requests.exceptions.RequestException as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/') #route to the index page
def index(): #function to render the index.html page
    return render_template('index.html')

#function to process the input from the website
@app.route('/process', methods=['POST']) #route to process the input

#function to process the input from the website
def process():
    topic = request.form['topic']
    text_type = request.form['type']
    text = request.form['text']
    
    return generate_feedback(topic, text_type, text)

if __name__ == '__main__':
    app.run(debug=True)
