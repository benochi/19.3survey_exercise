from http.client import responses
from flask import Flask, render_template, request, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey
# surveys = {
#    "satisfaction": satisfaction_survey,
#    "personality": personality_quiz,
# }
#  
#initiate empty CONST list for responses. 
RESPONSES_LIST = "responses" 
#append responses 

app = Flask(__name__)
#secret key for debugtoolbar usage
app.config['SECRET_KEY'] = "hasjhasa"
#don't intercept redirects, let them redirect.
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

@app.route("/")
def survey_select():
    """select a survey"""
    return render_template('survey_select.html', survey=survey)

@app.route("/start", methods=["POST"])
def start_survey():
    """starts new survey, reset reponses"""
    """The session object is NOT a secure way to store data. It's a base64 encoded string and can easily be decoded, 
    thus not making it a secure way to save or access sensitive information"""
    session[RESPONSES_LIST] = []

    #start survey
    return redirect("/questions/0")

#Next, build a route that can handle questions
#— it should handle URLs like /questions/0 (the first question), /questions/1, and so on.
@app.route('/questions/<int:question_id>')
def question(question_id):
    """Displays question based off ID"""
    responses = session.get[RESPONSES_LIST]
    
    if (responses is None):
        return redirect("/")
    """Once they’ve answered all of the questions, trying to access any of the question pages should redirect them to the 
    thank you page."""
    if (len(responses) == len(survey.questions)):
        return redirect("/thanks")

    #for the question show page to look at the number in the URL 
    #and make sure it’s correct. If not, you should redirect the user to the correct URL.
    if (len(responses) != question_id):
    #Using flash, if the user does try to tinker with the URL and visit questions out of order, 
    #flash a message telling them they’re trying to access an invalid question as part of your redirect.
        flash(f"Invalid question: {question_id}.")
        return redirect(f"/questions/{len(responses)}")



    question = survey.questions[question_id]

    return render_template("question.html", question=question, question_num=question_id)

"""When the user submits an answer, you should append this answer to your responses list,
 and then redirect them to the next question.
The Flask Debug Toolbar will be very useful in looking at the submitted form data"""
@app.route("/answer", method=["POST"])
def next_question():
    """Append answer to RESPONSES_LIST and redirect to next question"""
    #get the users answer
    choice = request.form['answer']
    #append users answer
    #However, for a list stored in the session, you’ll need to rebind the name in the session, like so:
    responses = session[RESPONSES_LIST]
    responses.append(choice)
    session[RESPONSES_LIST] = responses

    """ Once the user has answered all questions, 
    rather than trying to send them to /questions/5, redirect them to a simple “Thank You!” page."""

    if (len(responses) == len(survey.questions)):
        return redirect("/thanks")
    else:
        #redirect to /questions/question_id dynamically
        return redirect(f"/questions/{len(responses)}")

@app.route("/thanks")
def complete():
    """Send to thank you page, survey done"""

    return render_template("thanks.html")
