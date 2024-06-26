from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
import threading
import bcrypt
import paho.mqtt.client as mqtt
from mqtt_local import init_mqtt, mqtt_client
import utils

app = Flask(__name__)

# db init
db = yaml.safe_load(open('../db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.secret_key='MKBHD'
mysql = MySQL(app)

# home login page api call
@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and password == user[2]:
            # success
            session['email'] = email
            # publish mqtt msg
            mqtt_client.publish("login", f"User {email} logged in.") ###
            return redirect(url_for('congratulations'))
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

# registration page
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        reenter_password = request.form['reenter_password']

        if password == reenter_password:
            # hashed_password =
            # will go to method call
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            cursor.close()
            #

            session['email'] = email
            # publish mqtt msg
            mqtt_client.publish("register", f"User {email} registered.") ###
            return redirect(url_for('congratulations'))
        else:
            return render_template('register.html', error="Passwords do not match!")

    return render_template('register.html')

# congrats page
@app.route('/congratulations')
def congratulations():
    if 'email' in session:
        message = f"Congratulations! You are logged in as {session['email']}."
        # mqtt_client.publish("congo", f"User {session['email']} at congo page.") ###
        return render_template('congratulations.html', message=message)
    else:
        return redirect(url_for('home'))

# @app.teardown_appcontext
# def shutdown_mqtt(exception=None):
#     mqtt_client.loop_stop()
#     mqtt_client.disconnect()

def main():

    mqtt_thread = threading.Thread(target=init_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

if __name__ == '__main__':
    main()
    app.run(debug=True)
