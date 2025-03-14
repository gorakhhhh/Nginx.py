📌STEP 1: Install Required Packages:-
Run the following commands as the root user to install Nginx, Python, and necessary dependencies.

yum install epel-release -y
yum install nginx python3 python3-pip -y
Start and enable Nginx:

systemctl start nginx
systemctl enable nginx

📌STEP 2: Install Flask and Gunicorn:-
We need Flask (a web framework) and Gunicorn (a WSGI server) to run our application in production mode.

pip3 install flask gunicorn

📌STEP 3:Create a Flask Web App
-Create a project directory:
mkdir -p /var/www/tictactoe
cd /var/www/tictactoe

-Create the Flask application file:
vi app.py


-Paste the following Python code inside app.py:

from flask import Flask, render_template, request

app = Flask(__name__)

xState = [0] * 9
zState = [0] * 9
turn = 1  # 1 for X and 0 for O

def checkWin(xState, zState):
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for win in wins:
        if sum(xState[i] for i in win) == 3:
            return "X Won the match!"
        if sum(zState[i] for i in win) == 3:
            return "O Won the match!"
    return None

@app.route("/", methods=["GET", "POST"])
def tic_tac_toe():
    global xState, zState, turn
    winner = None
    
    if request.method == "POST":
        value = int(request.form.get("cell"))
        if turn == 1:
            xState[value] = 1
        else:
            zState[value] = 1
        winner = checkWin(xState, zState)
        turn = 1 - turn

    return render_template("index.html", xState=xState, zState=zState, winner=winner)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

📌STEP 4: Create the HTML Template
Create a templates/ folder:
-mkdir templates
cd templates
vi index.html


-Paste the following HTML code inside index.html:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tic Tac Toe</title>
</head>
<body>
    <h1>Welcome to Tic Tac Toe</h1>
    {% if winner %}
        <h2>{{ winner }}</h2>
    {% endif %}
    <form method="POST">
        <table border="1">
            {% for row in range(3) %}
                <tr>
                    {% for col in range(3) %}
                        <td>
                            {% set index = row * 3 + col %}
                            <button type="submit" name="cell" value="{{ index }}">
                                {{ 'X' if xState[index] else ('O' if zState[index] else index) }}
                            </button>
                        </td>
                    {% endfor %}
                </tr>
            {% endfor %}
        </table>
    </form>
</body>
</html>

📌STEP 5:Test the Flask App (Optional):
-To check if the application is working before setting up Nginx, run:
cd /var/www/tictactoe
python3 app.py

-Now open a browser and go to:
http://your-server-ip:5000

If the game is working, press CTRL+C to stop the server and continue setting up Gunicorn.

📌STEP 6:Set Up Gunicorn as a WSGI Server:
-Run the Flask app using Gunicorn manually first:
gunicorn --bind 0.0.0.0:5000 app:app
If it works, press CTRL+C to stop and move to the next step.


-Create a systemd service file for Gunicorn:
vi /etc/systemd/system/tictactoe.service

-Paste the following content:

[Unit]
Description=Tic Tac Toe Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/tictactoe
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target

-Start and enable the service:

systemctl daemon-reload
systemctl enable tictactoe
systemctl start tictactoe

📌STEP 7:Configure Nginx as a Reverse Proxy:-
1:Create an Nginx configuration file for your Flask app:

vi /etc/nginx/conf.d/tictactoe.conf

2.Paste the following configuration:

server {
    listen 80;
    server_name your-server-ip;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

3:Restart Nginx to apply changes:
systemctl restart nginx

📌STEP 8: Configure Firewall
To allow HTTP traffic, run:

firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload

📌STEP 9:Test the Deployment
1:Open your browser and go to:
http://your-server-ip

2:You should now see the Tic Tac Toe game running on Nginx.
Ensure Everything Runs on Boot

3:To make sure the services start automatically on system reboot:

systemctl enable nginx
systemctl enable tictactoe


🎉 Done! Your Tic Tac Toe Game is Live on an Nginx Server! 🚀
Now your Flask application is running with Gunicorn behind Nginx. 

