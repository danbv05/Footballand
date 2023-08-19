from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from footballand.models import Match, Bet, Prize
from django.utils import timezone
from datetime import datetime, timedelta
import random
import math

User = get_user_model()

# def update_image(request, flight_id):
#     match = Match.objects.get(id=flight_id)
#     # img = request.FILES.get('image')
#     # flight.image = img
#     # match.save()
#     return redirect("single_flight", flight_id)

def index(request):
    context ={}
    if request.user.is_authenticated:
        print("logged in - reading context")
        update_match_status()
        context = update_results(request)
        print("context updated")
        # usertime = timezone.now()
        # one_sec = timedelta(seconds=1)
        # print(f"{request.user.last_login.strftime('%D')}")
        # print(f"{usertime.strftime('%D')}")
        # print(f"{usertime}")
        # print(f"{usertime - one_sec}")
        # print(f"{(usertime - one_sec).date()}")
        # print(f"{(request.user.last_login - one_sec).date()}")
        # print(f"{(usertime - one_sec).date() == (request.user.last_login - one_sec).date() }")
        # print(f"{request.user.last_login.strftime('%D') == usertime.strftime('%D')}")
    print(f"context is:{context}")
    return render(request, 'index.html', context)

@login_required
def daily_tokens(request):
    # def is_day_passed(time):
    #     now = timezone.now()
    #     one_sec = timedelta(seconds=1)
    #     if((now - one_sec).date() == now.date()):
    #         return False
    #     else:
    #         print("a day has passed in the last second!")
    if (request.user.daily_token_used == False):
        request.user.bet_tokens_amount += 10
        request.user.daily_token_used = True
        request.user.save()
    else:
        pass
    print(f"{request.user.daily_token_used}")
    # context ={
    #     'status': request.user.daily_token_used
    # }
    return render(request, 'index.html')

@login_required
def footballand_logout(request):
    print("logout function entered !!!!!!!!!!!!")
    request.user.previous_login = request.user.last_login
    request.user.save()
    logout(request)
    return redirect('index')
    
def footballand_register(request):
    print("register function entered !!!!!!!!!!!!")
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f"username={username}. passowrd={password}")    
            user = User.objects.create_user(username, "", password)
            user.save()
    except Exception as e:
        print(f"*** Error occured:{e}")
        messages.error(request, f"*** Error occured while registering user:{e}")
        
    return redirect('index')

def footballand_login(request):
    def set_up(request):
        if request.user.last_login is not None:
            if  request.user.last_login.date() != request.user.previous_login.date():
                print(f"{request.user.last_login.date()}")
                print(f"{request.user.previous_login.date()}")
                print("different day - daily token refreshed")
                request.user.daily_token_used = False
                request.user.save()
        else:
            print("SAME day")
        return redirect('index')
    print("login function entered !!!!!!!!!!!!")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"username={username}. passowrd={password}")

        # Authenticate the user - validating user password. return user object if valid
        user = authenticate(request, username=username, password=password)
        print(f"authenticate passed. user is:{user}")

        if user is not None:
            # If the credentials are correct, log in the user
            login(request, user)
            print(f"** login passed. user is:{user}")
            return set_up(request)
        else:
            print(f"!! error login. user is:{user}")
            # If authentication fails, show an error message or redirect back to the login page
            error_message = "Invalid credentials. Please try again."
            return render(request, 'index.html', {'error_message': error_message})

    return redirect('index')
def update_match_status():
    all_active_matches = Match.objects.filter(active = True)
    for match in all_active_matches:
        print(f"{datetime.now().replace(tzinfo=timezone.utc)}")
        print(f"{match.date}")
        print(f"***match {match.id} date has passed: {datetime.now().replace(tzinfo=timezone.utc) >= match.date}****")
        if((datetime.now().replace(tzinfo=timezone.utc) >= match.date) and match.active == True):
            choices = ["team 1 wins", "team 2 wins", "draw"]
            team_1_factor = 1 / match.win_ratio_team_1
            team_2_factor = 1 / match.win_ratio_team_2
            draw_factor = 1 / match.draw_ratio
            normalized_factor = team_1_factor + team_2_factor + draw_factor
            prob_1_win = team_1_factor/normalized_factor
            prob_2_win = team_2_factor/normalized_factor
            prob_draw = draw_factor/normalized_factor
            weights = [prob_1_win,prob_2_win,prob_draw]
            random_result = random.choices(choices, weights=weights)[0]
            if (random_result == "draw"):
                goals = random.randint(0, 4)
                match.result_team_1 = goals
                match.result_team_2 = goals
            elif(random_result == "team 1 wins"):
                winners_goals = random.randint(1, 5)
                gap = random.randint(1, winners_goals)
                match.result_team_1 = winners_goals
                match.result_team_2 = winners_goals - gap
            elif(random_result == "team 2 wins"):
                winners_goals = random.randint(1, 5)
                gap = random.randint(1, winners_goals)
                match.result_team_2 = winners_goals
                match.result_team_1 = winners_goals - gap
            match.active = False
            match.save()
    return

@login_required
def update_results(request):
    updated_bets = Bet.objects.filter(player=request.user).filter(active=True).filter(match__active=False)
    win_bets = []
    lost_bets = []
    for updated_bet in updated_bets:
        print(f"{updated_bet.prediction}")
        if(updated_bet.match.result_team_1 > updated_bet.match.result_team_2):
            print(f"team 1 wins")
            if(updated_bet.prediction == "team_1"):
                profit = math.floor(updated_bet.match.win_ratio_team_1 * updated_bet.tokens)
                print(f"profit is {profit}")
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        elif(updated_bet.match.result_team_1 < updated_bet.match.result_team_2):
            print(f"team 2 wins")
            if(updated_bet.prediction == "team_2"):
                profit = math.floor(updated_bet.match.win_ratio_team_2 * updated_bet.tokens)
                print(f"profit is {profit}")
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                print(f"updated tokens are {request.user.bet_tokens_amount}")
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        else:
            if(updated_bet.prediction == "draw"):
                profit = math.floor(updated_bet.match.draw_ratio * updated_bet.tokens)
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        print(f"wins bet: {win_bets}")
        print(f"lost bet: {lost_bets}")
        updated_bet.active=False
        updated_bet.save()
    request.user.save()
    context ={
        'updated_wins': win_bets,
        'updated_losses': lost_bets
    }
    return context
####### MATCHES FUNCTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# @login_required
# def matches(request):
#     ## filter by tickets number - get tickets number from GET request
#     # search_team = request.GET.get('search_team')
#     all_active_matches = Match.objects.all().filter(active = True)
#     # if search_team:
#     #     all_matches = all_matches.filter(team1__lt=search_team)
#     context = {
#         'matches': all_active_matches  # Replace 'data' with the data you want to pass to the template
#     }
#     return render(request, 'matches.html', context)

@login_required
def matches(request):
    ## filter by tickets number - get tickets number from GET request
    update_match_status()
    shown_matches = Match.objects.filter(active = True)
    search_str = request.GET.get('search')
    # start_date = request.GET.get('start_date')
    # end_date = request.GET.get('end_date')
    if search_str:
        print(f"*****{search_str}#######")
        shown_matches = shown_matches.filter(Q(team_1__name__contains=search_str)|Q(team_2__name__contains=search_str))
        print(shown_matches)
    # if search_team:
    #     all_matches = all_matches.filter(team1__lt=search_team)
    context = {
        'matches': shown_matches,  # Replace 'data' with the data you want to pass to the template
        'search': search_str
    }
    return render(request, 'matches.html', context)

@login_required
def bet_match(request, match_id):
    print("********ENTERED BET MATCH******")
    curr_match = Match.objects.get(id=match_id)
    print(curr_match)
    player_bets = Bet.objects.filter(player=request.user)
    if(player_bets.filter(match=curr_match)):
        error_message = f"You have already made a bet on this match: {curr_match}. You can't make another bet"
        return render(request, 'index.html', {'message': error_message})
    if request.method == 'POST':
        bet_tokens = int(request.POST.get('token'))
        if (bet_tokens > request.user.bet_tokens_amount):
            print(f"!! error betting. entered {bet_tokens} while maximum amount is:{request.user.bet_tokens_amount}")
            # maximum token amount exceeds
            error_message = f"you entered {bet_tokens} tokens while your current maximum amount is: {request.user.bet_tokens_amount}\n Please try again"
            return render(request, 'index.html', {'message': error_message})
        else:
            print("NUMBER IS", bet_tokens)
            request.user.bet_tokens_amount = request.user.bet_tokens_amount - bet_tokens
            request.user.save()
            print(f"current number of tokens for {request.user.username} is: {request.user.bet_tokens_amount}") 
            player_predict = request.POST.get('Predict_result')
            print("PREDICTION IS", player_predict)
    Bet.objects.create(player=request.user, match=curr_match,tokens=bet_tokens, prediction=player_predict)
    success_message = f"your bet of {bet_tokens} tokens was completed successfully!"
    # bet = Bet.objects.get(match = curr_match)
    # bet.player = request.user
    # bet.tokens = bet_tokens
    # bet.prediction = player_predict
    # bet.save()
    return render(request, 'index.html', {'message': success_message})

@login_required
def show_bets(request):
    bet_type = request.GET.get('bets')
    print(f"{bet_type}")
    past = None
    if bet_type == "active":
        shown_bets = Bet.objects.filter(player=request.user).filter(active=True)
    # if search_team:
    #     all_matches = all_matches.filter(team1__lt=search_team)

    elif bet_type =="past":
        past = True
        shown_bets = Bet.objects.filter(player=request.user).filter(active=False)
    context = {
        'player_bet': shown_bets,  # Replace 'data' with the data you want to pass to the template
        'past': past
    }
    print(f"{context}")
    return render(request, 'bets.html', context)  

# @login_required
# def bet_history(request):
#     past_bets = Bet.objects.filter(player=request.user).filter(active=False)
#     context = {
#         'player_past_bet': past_bets  # Replace 'data' with the data you want to pass to the template
#     }
#     print(f"{context}")
#     return render(request, 'past_bets.html', context)   

# def matches_text(request):
#     all_matches = Match.objects.all()
#     mystr = ""
#     for match in all_matches:
#         mystr += str(match)
#         mystr += "<br>"
#     return HttpResponse(f"This is a list of flights!<br>{mystr}")

####### POFILE FUNCTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@login_required
def my_profile(request):
    my_prizes = Prize.objects.filter(owner=request.user)
    context = {
        'prizes': my_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'my_profile.html', context)

###PRIZE FUNCTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@login_required
def prize_shop(request):
    all_prizes = Prize.objects.filter(owner__isnull=True)
    context = {
        'prizes': all_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'prize_shop.html', context)

def sort_results(request):
    sort_type = request.GET.get("sort")
    league_filter = request.GET.get("league")
    # sort_item_status = request.GET.get("status")
    if request.GET.get("view") == "all":
        pass
    else:
        searched_sort = request.GET.get("search")
    all_prizes = Prize.objects.filter(owner__isnull=True)
    # past = False
    # if sort_item_status == "active":
    #     all_matches = Match.objects.filter(active=True)
    # elif sort_item_status == "past":
    #     past = True
    all_matches = Match.objects.filter(active=True)
    if league_filter:
        all_matches = all_matches.filter(team_1__league__name = league_filter)
    if searched_sort:
        all_matches = all_matches.filter(Q(team_1__name__contains=searched_sort)|Q(team_2__name__contains=searched_sort))
    if(sort_type == "lowtohigh"):
        context = {
            'prizes': all_prizes.order_by("price")
        }
        return render(request, 'prize_shop.html', context)
    elif(sort_type == "hightolow"):
        context = {
            'prizes': all_prizes.order_by("-price")
        }
        return render(request, 'prize_shop.html', context)
    elif(sort_type == "soonertolater"):
            all_matches = all_matches.order_by("date")
    elif(sort_type == "latertosooner"):
            all_matches = all_matches.order_by("-date")
    context = {
        'matches':all_matches,
        'searchsort': searched_sort,
        'filter': league_filter
    }
    print(f"{context}")
    return render(request, 'matches.html', context)

def buy_prize(request, prize_id):
    print(f"prize is: {prize_id}")
    prize = Prize.objects.get(id=prize_id)
    print(f"prize is: {prize}")
    if request.method == 'POST':
        if (prize.price > request.user.prize_vouchers_amount):
            print(f"!! error buying. price is {prize.price} while maximum amount you have is: {request.user.prize_vouchers_amount}")
            # maximum token amount exceeds
            error_message = f"price is {prize.price} while maximum amount you have is: {request.user.prize_vouchers_amount}\n Please try again"
            return render(request, 'index.html', {'message': error_message})
        else:
            prize.owner = request.user
            print(f"Owner of {prize.name} is {prize.owner}")
            prize.save()
            request.user.prize_vouchers_amount = request.user.prize_vouchers_amount - prize.price
            request.user.save()
            print(f"current number of price vouchers for {request.user.username} is: {request.user.prize_vouchers_amount}")
            owned_prizes = Prize.objects.filter(owner=request.user) 
    context = {
        'prizes': owned_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'my_profile.html', context)