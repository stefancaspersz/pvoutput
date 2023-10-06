import hmac
from os import environ
from flask import Flask,request,json,redirect,url_for,abort,jsonify,render_template,make_response,after_this_request
from hashlib import sha1

app = Flask(__name__)

@app.route('/app',methods=['GET'])
def hello():
    try:
        # this only works when a reverse proxy like nginx provides the headers
        response = jsonify({'True-Client-IP': request.headers['True-Client-IP'],'X-Forwarded-For': request.headers['X-Forwarded-For']})
    except:
        # looks like we have not recieved the correct headers
        response = jsonify({'ip': request.remote_addr})
    print(request.headers)
    return response

@app.route('/app/pvoutput',methods=['GET'])
def pvoutput():
    @after_this_request
    def add_security_headers(resp):
        resp.headers['Content-Security-Policy']='default-src \'none\'; script-src \'self\' \'sha256-5fiuyxJBttX1doE3sqLbxkJmLMvgMwpWNzj0neND83M=\' pvoutput.org; connect-src \'self\'; img-src \'self\'; style-src \'self\';base-uri \'self\';form-action \'self\''
        return resp
    # check if cookie is present
    # if not abort
    args = request.args
    query = args.get("query")
    cookie = request.cookies.get('ctkn')
    if cookie == environ['COOKIE_TOKEN']:
        return render_template('static.html',sid=environ['PVOUTPUT_SID'])
    else:
        if query == environ['QUERY_TOKEN']:
            resp = make_response(redirect(url_for('pvoutput')))
            resp.set_cookie(key='ctkn', value=environ['COOKIE_TOKEN'], path='/app/pvoutput')
            return resp
        else:
            print("no query param")
            return redirect(url_for('hello'), code=302)
        
if __name__ == '__main__':
    app.run()
