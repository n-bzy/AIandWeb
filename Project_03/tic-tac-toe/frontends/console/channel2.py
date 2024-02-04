# tic-tac-toe channel
from flask import Flask, request, jsonify  # render_template
from .cli import main
from .args import parse_args, grid_to_index
from tic_tac_toe.logic.models import GameState, Grid, Mark
# from tic_tac_toe.logic.exceptions import InvalidMove
from .renderers import ConsoleRenderer, print_solid
import json
import requests


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'


# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db

HUB_URL = 'http://localhost:5555'
HUB_AUTHKEY = '1234567890'
CHANNEL_AUTHKEY = '22334455'
CHANNEL_NAME = "The unbeatable TicTacToe Bot"
CHANNEL_ENDPOINT = "http://localhost:5002"
CHANNEL_FILE = 'messages2.json'
p1 = None
p2 = None
gs = None
EMPTY_GRID = print_solid("         ")


def run():
    save_messages([])
    app.run(port=5002, debug=True)


@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels',
                             headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({"name": CHANNEL_NAME,
                                              "endpoint": CHANNEL_ENDPOINT,
                                              "authkey": CHANNEL_AUTHKEY}))

    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        return


def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True


@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name': CHANNEL_NAME}),  200


# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    # fetch channels from server
    return jsonify(read_messages())


# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    global p1, p2, gs
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization", 400
    # check if message is present
    message = request.json
    if not message:
        return "No message", 400
    if 'content' not in message:
        return "No content", 400
    if 'sender' not in message:
        return "No sender", 400
    if 'timestamp' not in message:
        return "No timestamp", 400
    # add message to messages
    inpt = message['content']
    messages = read_messages()
    if not messages:
        p1, p2, gs, grid = start_ttt()
    else:
        if gs.game_over:
            save_messages([])
            p1, p2, gs, grid = start_ttt()
    if check_inpt(inpt, messages):
        return "OK", 200
    grid = play_ttt(inpt)
    messages.append({'sender': message['sender'],
                     'content': grid,
                     })
    if not gs.game_over:
        grid = bot_response()
        messages.append({'sender': 'ttt_bot',
                        'content': grid,
                         })
    save_messages(messages)
    return "OK", 200


def read_messages():
    global CHANNEL_FILE
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return []
    try:
        messages = json.load(f)
    except json.decoder.JSONDecodeError:
        messages = []
    f.close()
    return messages


def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)


def check_inpt(inpt, messages):
    try:
        grid_to_index(inpt)
    except ValueError:
        messages.append({'sender': 'ttt_bot',
                        'content': "Please provide coordinates in the form of A1 or 1A",
                         })
        save_messages(messages)
        return True
    if gs.grid.cells[grid_to_index(inpt)] != " ":
        # raise InvalidMove("Cell is not empty")
        messages.append({'sender': 'ttt_bot',
                        'content': f'Cell {inpt} is not empty, select an empty cell!',
                         })
        save_messages(messages)
        return True


def bot_response():
    global p1, p2, gs
    inpt = None
    gs = main(p1, p2, gs, inpt)
    grid = ConsoleRenderer().render(game_state=gs)
    if gs.game_over:
        if gs.winner:
            st = f"\n {gs.winner} wins"
            return str(grid+st)
        if gs.tie:
            st = "\n No one wins this time"
            return str(grid+st)
    return grid


def start_ttt():
    # global p1, p2, gs
    p1, p2, starting_mark = parse_args()
    starting_mark = Mark("X")
    gs = GameState(Grid(), starting_mark)
    grid = ConsoleRenderer().render(game_state=gs)
    return p1, p2, gs, grid


def play_ttt(inpt):
    global p1, p2, gs
    # print(p1, p2, gs, inpt)
    gs = main(p1, p2, gs, inpt)
    grid = ConsoleRenderer().render(game_state=gs)
    if gs.game_over:
        if gs.winner:
            st = f"\n {gs.winner} wins"
            return str(grid+st)
        if gs.tie:
            st = "\n No one wins this time"
            return str(grid+st)
    return grid


# Start development web server
if __name__ == '__main__':
    save_messages([])
    app.run(port=5002, debug=True)
