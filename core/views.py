from django.http import JsonResponse
from django.shortcuts import render, redirect

from core.models import GamePlayer, GameSession
import random

# Create your views here.

def default_context():
    context = {
        'title': 'Dirty Santa',
    }
    return context

def index(request):
    def load_index(request, add_context=None):
        if request.user.is_authenticated:
            game = GameSession.objects.filter(manager=request.user, complete=False)
            if game.exists():
                game = GameSession.objects.get(manager=request.user, complete=False)
                cur_game = game.code
            else:
                cur_game = None
        else:
            cur_game = None

        context = {
            "current_game": cur_game,
        }
        context.update(default_context())
        if add_context != None:
            context.update(add_context)
        return render(request, "core/index.html", context)

    if request.POST:
        if "join" in request.POST:
            code = request.POST['join']
            # check if code entered is correct
            game_exists = GameSession.objects.filter(code=code)
            if game_exists.exists():
                player = request.POST['name']
                # create session for player
                request.session['game'] = code
                request.session['name'] = player
                # add player to DB
                game = GameSession.objects.get(code=code)
                new_game_player = GamePlayer.objects.create(session_id=game, name=player)
                request.session['id'] = new_game_player.id

                return redirect("core:active_game", code)
            else:
                return load_index(request, {'error':'Incorrect Code'})
        elif "continue" in request.POST:
            code = request.POST['continue']
            return redirect("core:active_game", code)
        elif "new" in request.POST:
            return redirect("core:new_game")
        else:
            return load_index(request, {'error':'Error! Not sure what though...'})
    else:
        try:
            if request.session['game']:
                return redirect('core:active_game', request.session['game'])
        except KeyError:
            pass
        return load_index(request)


def new_game(request):
    check_game = GameSession.objects.filter(manager=request.user, complete=False)
    if check_game.exists():
        print("game exists!")
        game = GameSession.objects.get(manager=request.user, complete=False)
    else:
        game = GameSession.objects.create(manager=request.user)
        player = GamePlayer.objects.create(session_id=game, name=request.user.username)
        request.session['game'] = game.code
        request.session['name'] = player.name

    if request.method == "POST":
        if request.POST['action'] == "setup":
            game = game_setup(game)
        elif request.POST['action'] == "ready":
            game_session = GameSession.objects.get(code=game)
            game_session.ready = True
            game_session.save()
            game = game_session

    players = GamePlayer.objects.filter(session_id=game.id)
    player_count = players.count()

    context = {
        "game": game,
        "players": players,
        "player_count": player_count,
    }
    context.update(default_context())
    return render(request, "core/new_game.html", context)

def game_setup(game):
    players = GamePlayer.objects.filter(session_id=game)
    player_list = []
    for player in players:
        player_list.append(player.id)
    items = list(player_list)
    random.shuffle(items)
    random.shuffle(items)
    random.shuffle(items)
    turn = 1
    for value in items:
        player = GamePlayer.objects.get(id=value)
        player.turn = turn
        player.save()
        turn = turn + 1
    game_session = GameSession.objects.get(code=game)
    game_session.setup = True
    game_session.save()
    return game_session


def active_game(request, code):
    game = GameSession.objects.get(code=code)
    if game.complete == True:
        del request.session['id']
        return redirect("core:index")

    players = GamePlayer.objects.all()
    current_player = players.get(turn=game.current_turn)
    player_gifts = players.filter(possession=True)
    player_with_gifts = {}
    for player in player_gifts:
        player_with_gifts.update({player.id:player.name})

    if game.theif:
        theif = game.theif.id
    else:
        theif = None

    context = {
        "game": game,
        "session_id": request.session['id'],
        "current_player": {'id':current_player.id, 'name':current_player.name},
        "players_with_gifts": player_with_gifts,
        "theif": theif,
    }
    context.update(default_context())
    return render(request, "core/active_game.html", context)


def game_details(request, code):
    status = GameSession.objects.get(code=code)
    if request.POST:
        if "open" in request.POST:
            game_player = GamePlayer.objects.get(id=request.POST['open'])
            print(game_player.possession)
            game_player.possession = True
            game_player.save()

            # get current player
            get_current_turn(status, code)
            status.theif = None
            status.save()
            return redirect('core:active_game', code)
        if "steal" in request.POST:
            game_player = GamePlayer.objects.get(id=request.POST['steal'])
            game_player.possession = True
            game_player.save()

            stolen_player = GamePlayer.objects.get(id=request.POST['steal_from'])
            stolen_player.possession = False
            stolen_player.save()

            get_current_turn(status, code)
            status.theif = game_player
            status.save()
            return redirect('core:active_game', code)



    players = GamePlayer.objects.all()
    current_player = players.get(turn=status.current_turn)
    player_gifts = players.filter(possession=True)
    player_with_gifts = {}
    for player in player_gifts:
        player_with_gifts.update({player.id:player.name})

    if status.theif:
        theif = status.theif.id
    else:
        theif = None

    response = {
        'ready': status.ready,
        'session_player': request.session['id'],
        'current_turn': status.current_turn,
        'theif': theif,
        'current_player_name': current_player.name,
        'current_player_id': current_player.id,
        'players_with_gifts': player_with_gifts,
        'players_with_gifts_len': len(player_gifts),
    }
    return JsonResponse(response)

def get_current_turn(status, code):
    current_player = GamePlayer.objects.filter(possession=False).order_by('turn').first()
    if (current_player == None):
        status.complete = True
        status.save()
        return 'redirect'

    status.current_turn = current_player.turn
