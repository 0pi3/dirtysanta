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
            code = request.POST['join'].upper()
            # check if code entered is correct
            game_exists = GameSession.objects.filter(code=code)
            if game_exists.exists():
                player = request.POST['name']
                # create session for player
                request.session['game'] = code
                request.session['player_name'] = player
                # add player to DB
                game = GameSession.objects.get(code=code)
                new_game_player = GamePlayer.objects.create(session_id=game, name=player, phone=True)
                request.session['player_id'] = new_game_player.id

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
        request.session['player_name'] = player.name
        request.session['player_id'] = player.id

    # set new_game_player & new_game_player_outcome variable in case nothing posted
    new_game_player = None
    new_game_player_message = None
    new_game_player_outcome = None

    if request.method == "POST":
        if 'action' in request.POST:
            if request.POST['action'] == "setup":
                game = game_setup(game)
            elif request.POST['action'] == "ready":
                game_session = GameSession.objects.get(code=game)
                game_session.ready = True
                game_session.save()
                game = game_session
                return redirect('core:active_game', game.code)
            elif request.POST['action'] == "add_player":
                # add new player - not using phone
                game = GameSession.objects.get(code=game)
                if GamePlayer.objects.filter(session_id=game, name=request.POST['new_name']).exists():
                    new_game_player = request.POST['new_name']
                    new_game_player_message = "already exists."
                    new_game_player_outcome = "warning"
                else:
                    new_game_player = GamePlayer.objects.create(session_id=game, name=request.POST['new_name'])
                    new_game_player = new_game_player.name
                    new_game_player_message = "has been added."
                    new_game_player_outcome = "success"


    players = GamePlayer.objects.filter(session_id=game.id)
    player_count = players.count()

    context = {
        "game": game,
        "players": players,
        "player_count": player_count,
        "new_player": new_game_player,
        "new_player_message": new_game_player_message,
        "new_player_outcome": new_game_player_outcome,
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
        try:
            del request.session['game']
            del request.session['player_name']
            del request.session['player_id']
            del request.session['current_player']
            return redirect("core:index")
        except:
            return redirect("core:index")

    context = {
        "game": game,
        "session_id": request.session['player_id'],
    }


    if game.ready == True:
        players = GamePlayer.objects.filter(session_id=game)
        current_player = players.get(turn=game.current_turn)
        player_gifts = players.filter(possession=True)
        player_with_gifts = {}
        for player in player_gifts:
            player_with_gifts.update({player.id:player.name})

        if game.theif:
            theif = game.theif.id
        else:
            theif = None
        context.update({
            "current_player": {'id':current_player.id, 'name':current_player.name, 'phone':current_player.phone},
            "players_with_gifts": player_with_gifts,
            "theif": theif,
        })
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
            get_current_turn(status)
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

            get_current_turn(status)
            status.theif = game_player
            status.save()
            return redirect('core:active_game', code)

    response = {
        'ready': status.ready,
        'setup': status.setup,
    }
    if status.setup == True:
        player = GamePlayer.objects.get(id=request.session['player_id'])
        response.update({
            'player_turn': player.turn,
        })
    if status.ready == True:
        players = GamePlayer.objects.filter(session_id=status)
        current_player = players.get(turn=status.current_turn)
        player_gifts = players.filter(possession=True)
        player_with_gifts = {}
        for player in player_gifts:
            player_with_gifts.update({player.id:player.name})

        if status.theif:
            theif = status.theif.id
        else:
            theif = None

        if 'current_player' not in request.session or request.session['current_player'] != current_player.name:
            request.session['current_player'] = current_player.name
            reload_page = True
        else:
            reload_page = False

        if status.complete == True:
            reload_page = True

        response.update({
            'session_player': request.session['player_id'],
            'current_turn': status.current_turn,
            'theif': theif,
            'current_player_name': current_player.name,
            'current_player_id': current_player.id,
            'players_with_gifts': player_with_gifts,
            'players_with_gifts_len': len(player_gifts),
            'reload_page': reload_page,
        })
    return JsonResponse(response)

def get_current_turn(status):
    next_player = GamePlayer.objects.filter(session_id=status, possession=False).order_by('turn').first()
    if (next_player == None):
        status.complete = True
        status.save()
        return 'redirect'
    print(next_player)
    print('current turn')
    print(next_player.turn)
    status.current_turn = next_player.turn
    status.save()
