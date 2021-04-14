

from flask import Flask, request, render_template , flash, redirect, url_for
import tkinter
from tkinter.ttk import *
from tkinter.filedialog import asksaveasfile 
from tkinter.filedialog import askopenfile 
from nlp import ocr,nlp
from mongo import insert , present_or_not , get_field , get_employer_view
from send_mail import send_mail

app = Flask(__name__)   




@app.route('/', methods =["GET", "POST"])
def home_page():
    if request.method == "POST":
        if request.form["submit_button"] == "sign_up":            
        
            return redirect(url_for('sign_up'))
        elif request.form["submit_button"] == "login":
            post = {}
            post['email'] = request.form.get('email')       
            post['password'] = request.form.get('password') 
            if present_or_not(post,'employee') == 1:
                user_name = get_field(post,'first_name','employee')
                _id = get_field(post,'_id','employee')
                email = get_field(post,'email','employee')
                return redirect(url_for('employee',user_name =user_name , _id = _id,email = email))
        elif request.form["submit_button"] == "employer":
            return redirect(url_for('employer'))

        
    return render_template("home.html")

@app.route('/sign_up', methods =["GET", "POST"])
def sign_up():
    if request.method == "POST":
        post = {}
        post['email'] = request.form.get('email')
        post['first_name'] = request.form.get('firstName')
        post['password'] = request.form.get('password')    

        if present_or_not({'email':post['email'],'first_name':post['first_name']},'employee')==0:
            insert(post,'employee')
            return redirect(url_for('home_page' ))

            
    return render_template("sign_up.html")    

@app.route('/employee', methods =["GET", "POST"])
def employee():
    user_name=request.args.get('user_name')
    emp_id=request.args.get('_id')
    email=request.args.get('email')
    output = {}
    if request.method == "POST":
       
    
        if request.form["submit_button"] == "upload":
            file_path = askopenfile(mode ='r', filetypes =[('PDF Files', '*.pdf')]) 
            text = ocr(file_path.name)
            output = nlp(text)
            post = {}
            post['_id'] = emp_id
            post['emp_name'] = user_name
            post['emp_email'] = email
            post.update(output)
            insert(post,"resume")
            # return render_template("employee.html",user_name = user_name )
        
            

        
    return render_template("employee.html",user_name = user_name , output = output)

@app.route('/employer', methods =["GET", "POST"])
def employer():
    employer_view = {}
    total_records = 0    
    employer_view = get_employer_view()
    total_records = len(employer_view['_id'])
    #print(employer_view,total_records)
    if request.method == "POST":
        # if request.form["submit_button"].count("select")>0:
        post = {}
        post['_id'] = request.form["submit_button"]
        email_id = get_field(post,"emp_email","resume")
        name = get_field(post,"emp_name","resume")
        send_mail(email_id,name)
       


    return render_template("employer.html",output = employer_view , total_records = total_records )

        
  
if __name__=='__main__':
   app.run()