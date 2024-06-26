from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
import bcrypt
import paho.mqtt.client as mqtt

app = Flask(__name__)

# flask app configure
db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.secret_key='MKBHD'
mysql = MySQL(app)

# mqtt config
mqtt_broker = 'localhost'
mqtt_port = 1883
mqtt_client=mqtt.Client()

sub_d={
    'login',
    'regis',
    'congo'
}


# mqtt callbacks
def on_connect(client, userdata, flags, rc):
    try:
        print("MQTT connected")
        for topic in sub_d:
            mqtt_client.subscribe(topic)
            # mqtt_client.message_callback_add(topic)
            print(f"Subscribed to topic: {topic}")
    except:
        print("Failed to connect to MQTT broker, return code %d\n", rc)


mqtt_client.on_connect = on_connect

def on_message(client, userdata, msg):
    print(f"Received from {msg.topic}, content: {msg.payload.decode()}")

    # Process MQTT message here

mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_broker,mqtt_port,60)
mqtt_client.loop_start()

'''
flask code below + mqtt implement
'''

# home login page
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
            mqtt_client.publish("login", f"User {email} logged in.")
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
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
            mysql.connection.commit()
            cursor.close()

            session['email'] = email
            # publish mqtt msg
            mqtt_client.publish("regis", f"User {email} registered.")
            return redirect(url_for('congratulations'))
        else:
            return render_template('register.html', error="Passwords do not match!")

    return render_template('register.html')

# congrats page
@app.route('/congratulations')
def congratulations():
    if 'email' in session:
        message = f"Congratulations! You are logged in as {session['email']}."
        # mqtt_client.publish("congo", f"User {session['email']} at congo page.")
        return render_template('congratulations.html', message=message)
    else:
        return redirect(url_for('home'))

# @app.teardown_appcontext
# def shutdown_mqtt(exception=None):
#     mqtt_client.loop_stop()
#     mqtt_client.disconnect()

if __name__ == '__main__':
    app.run(debug=True)
