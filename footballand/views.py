from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from footballand.models import Match, Bet, Prize
from django.utils import timezone
from datetime import datetime
import random
import math

#requiered for absract user model 
User = get_user_model()

#####Register, login, logout

##### register
def footballand_register(request):
    try:
        #ensuring registration only for post methods
        if request.method == 'POST':
            username = request.POST.get('username')
            #vailidate username lenght
            if len(username) < 1:
                error_message = f"No username entered - enter a username of 1 character at least"
                return render(request, 'index.html', {'message': error_message})
            password = request.POST.get('password')
            #vailidate password lenght
            if len(password) < 1:
                error_message = f"No password entered - enter a password of 1 character at least"
                return render(request, 'index.html', {'message': error_message})
            print(f"username={username}. passowrd={password}")    
            user = User.objects.create_user(username, "", password)
            user.save()
            success_message = f"The user {username} has been created successfully!"
            return render(request, 'index.html', {'message': success_message})
    except Exception as e:
        print(f"*** Error occured:{e}")
        exception_str = str(e)
        #catching the exception of unique username failure (register a username which is already taken) and display it
        if exception_str == "UNIQUE constraint failed: footballand_player.username":
            error_message = f"The username {username} has already been taken, try another username instead"
    return render(request, 'index.html', {'message': error_message})

##### login
def footballand_login(request):
    #set up - function for log in - sets up free token option if player hasn't logged before in the current day (once a day player recieves tokens)
    def set_up(request):
        #ensuring the player hasn't just registerd (in that case he hasn't logged before at all)
        if request.user.previous_login is not None:
            #checks if previous login date is different than current login date (built in user model has this attribute - called last_login)
            #if so - free daily tokens where not used yet
            if  request.user.last_login.date() != request.user.previous_login.date():
                print(f"{request.user.last_login.date()}")
                print(f"{request.user.previous_login.date()}")
                print("different day - daily token refreshed")
                request.user.daily_token_used = False
                request.user.save()
        else:
            print("SAME day")
        #redirect to index page after log in set-up
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
            #while logging in - initiate set up proccess for user
            return set_up(request)
        else:
            print(f"!! error login. user is:{user}")
            # If authentication fails, show an error message or redirect back to the login page
            error_message = "Invalid credentials. Please try again."
            return render(request, 'index.html', {'message': error_message})

    return redirect('index')

##### logout
@login_required
def footballand_logout(request):
    print("logout function entered !!!!!!!!!!!!")
    #saves the logged out session start date (the log in date) for next log in 
    request.user.previous_login = request.user.last_login
    request.user.save()
    logout(request)
    return redirect('index')

#### index function - 
def index(request):
    context ={}
    #shows content only if for authenticated player (logged in)
    if request.user.is_authenticated:
        print("logged in - reading context")
        #update match status for active matches which reached the game date 
        update_match_status(request)
        #update resulted matches relevant to current player (update player if he won or lost his bets for matches that ended)
        context = update_results(request)
        print("context updated")
    print(f"context is:{context}")
    return render(request, 'index.html', context)

##### daily token - update token amount for player (once a day -accessed from home page)
@login_required
def daily_tokens(request):
    if (request.user.daily_token_used == False):
        request.user.bet_tokens_amount += 10
        request.user.daily_token_used = True
        request.user.save()
    else:
        pass
    print(f"{request.user.daily_token_used}")
    return render(request, 'index.html')

##### update_match_status - update match resulted for active matches which reached the game date 
#request is an reqiured argument because it is login required
@login_required
def update_match_status(request):
    #get all active matches
    all_active_matches = Match.objects.filter(active = True)
    for match in all_active_matches:
        print(f"{datetime.now().replace(tzinfo=timezone.utc)}")
        print(f"{match.date}")
        print(f"***match {match.id} date has passed: {datetime.now().replace(tzinfo=timezone.utc) >= match.date}****")
        #checks if match date has passed - if so randomize result according to result likelyhood (the less the profit is, the more likely the outcome will happen)
        if((datetime.now().replace(tzinfo=timezone.utc) >= match.date) and match.active == True):
            choices = ["team 1 wins", "team 2 wins", "draw"]
            #set weight factors to outcomes in reverse correlation to to "win ratio" profit
            # e.g. team 1 winning outcome has a profit of X2, team 2 X4 profit, draw X3 - so factors will be 1/2 for team 1, 1/4 for team 2, 1/3 for draw
            team_1_factor = 1 / match.profit_ratio_team_1_win
            team_2_factor = 1 / match.profit_ratio_team_2_win
            draw_factor = 1 / match.profit_ratio_draw
            #normalize factors so their sum will be 1 (for vaild probability calculation - total probability must be 1)
            normalized_factor = team_1_factor + team_2_factor + draw_factor
            prob_1_win = team_1_factor/normalized_factor
            prob_2_win = team_2_factor/normalized_factor
            prob_draw = draw_factor/normalized_factor
            weights = [prob_1_win,prob_2_win,prob_draw]
            #randomize an outcome using random.choices and probability weights setted up for match
            #for to simplify the proccess, I decided that a draw will be no more than 4-4, and a winning team won't score more than 5 goals in a match
            random_outcome = random.choices(choices, weights=weights)[0]
            if (random_outcome == "draw"):
                goals = random.randint(0, 4)
                match.result_team_1 = goals
                match.result_team_2 = goals
            elif(random_outcome == "team 1 wins"):
                winners_goals = random.randint(1, 5)
                gap = random.randint(1, winners_goals)
                match.result_team_1 = winners_goals
                match.result_team_2 = winners_goals - gap
            elif(random_outcome == "team 2 wins"):
                winners_goals = random.randint(1, 5)
                gap = random.randint(1, winners_goals)
                match.result_team_2 = winners_goals
                match.result_team_1 = winners_goals - gap
            #after updating the results - make the match itself inactive
            match.active = False
            match.save()
    return

###### update_results - update relevant resulted matches to current player's active bet and conclude if bet was won or lost
#for each match result, checks if match prediction in the player's bet was right or wrong - if won update users tokens and prize vouchers
#creates a list of won bets and lost bets, return the lists with the recent bets status
@login_required
def update_results(request):
    updated_bets = Bet.objects.filter(player=request.user).filter(active=True).filter(match__active=False)
    win_bets = []
    lost_bets = []
    for updated_bet in updated_bets:
        print(f"{updated_bet.prediction}")
        #team 1 won outcome
        if(updated_bet.match.result_team_1 > updated_bet.match.result_team_2):
            print(f"team 1 wins")
            if(updated_bet.prediction == "team_1"):
                profit = math.floor(updated_bet.match.profit_ratio_team_1_win * updated_bet.tokens)
                print(f"profit is {profit}")
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        #team 2 won outcome
        elif(updated_bet.match.result_team_1 < updated_bet.match.result_team_2):
            print(f"team 2 wins")
            if(updated_bet.prediction == "team_2"):
                profit = math.floor(updated_bet.match.profit_ratio_team_2_win * updated_bet.tokens)
                print(f"profit is {profit}")
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                print(f"updated tokens are {request.user.bet_tokens_amount}")
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        #only option left is a draw
        else:
            if(updated_bet.prediction == "draw"):
                profit = math.floor(updated_bet.match.profit_ratio_draw * updated_bet.tokens)
                updated_bet.profit = profit
                request.user.bet_tokens_amount += profit
                request.user.prize_vouchers_amount += profit
                win_bets.append(updated_bet)
            else:
                lost_bets.append(updated_bet)
        print(f"wins bet: {win_bets}")
        print(f"lost bet: {lost_bets}")
        #make bet incative after concluding it
        updated_bet.active=False
        updated_bet.save()
    #save players data (tokens, prize vouchers) after concluding a match
    request.user.save()
    context ={
        'updated_wins': win_bets,
        'updated_losses': lost_bets
    }
    return context

###### matches - returns template showing active matches for all matches/ matches affected by search (if theres any search string inserted by user)
@login_required
def matches(request):
    ## upon entering matches view, update match status to so only matches with a date that hasn't passed yet will remain
    update_match_status(request)
    shown_matches = Match.objects.filter(active = True)
    #get search string 
    search_str = request.GET.get('search')
    #if theres search string - filter matches that contains the search (contained in team 1's name or team 2's name)
    if search_str:
        print(f"*****{search_str}#######")
        shown_matches = shown_matches.filter(Q(team_1__name__contains=search_str)|Q(team_2__name__contains=search_str))
        print(shown_matches)
    context = {
        'matches': shown_matches,  # Replace 'data' with the data you want to pass to the template
        'search': search_str
    }
    return render(request, 'matches.html', context)

##### bet_match - upon a bet made by player - creates a bet object for the player in app's database containning amount of bet tokens and bet prediction
#update player's tokens amount and saves database
@login_required
def bet_match(request, match_id):
    print("********ENTERED BET MATCH******")
    #get match by match's id
    curr_match = Match.objects.get(id=match_id)
    print(curr_match)
    #get all player's past bets
    player_bets = Bet.objects.filter(player=request.user)
    #checks if bet was already made for the desired match - a player cannot bet on a match more than once
    if(player_bets.filter(match=curr_match)):
        error_message = f"You have already made a bet on this match: {curr_match}. You can't make another bet"
        return render(request, 'index.html', {'message': error_message})
    #make a bet only possible by POST method - get player's prediction and player's bet tokens from the POST method content
    if request.method == 'POST':
        bet_tokens = request.POST.get('token')
        #integer validation for token input
        try:
            bet_tokens = int(bet_tokens)
        except ValueError as ex:
                error_message = "You did not enter an integer number for your bet - request aborted"
                return render(request, 'index.html', {'message': error_message})
        #validate bet amount does not go below minimum allowed
        if (bet_tokens < 1):
            # maximum token amount exceeds
            error_message = f"Bet must be a positive number of tokens and have to be larger than 1 - request aborted"
            return render(request, 'index.html', {'message': error_message})
        #validate bet amount does not go above maximum allowed (player's current total tokens)
        if (bet_tokens > request.user.bet_tokens_amount):
            print(f"!! error betting. entered {bet_tokens} while maximum amount is:{request.user.bet_tokens_amount}")
            error_message = f"you entered {bet_tokens} tokens while your current maximum amount is: {request.user.bet_tokens_amount}\n Please try again"
            return render(request, 'index.html', {'message': error_message})
        #if bet is valid - reduce player's token amount left after the bet and get player's prediction
        else:
            print("NUMBER IS", bet_tokens)
            request.user.bet_tokens_amount = request.user.bet_tokens_amount - bet_tokens
            request.user.save()
            print(f"current number of tokens for {request.user.username} is: {request.user.bet_tokens_amount}") 
            player_predict = request.POST.get('Predict_result')
            print("PREDICTION IS", player_predict)
    Bet.objects.create(player=request.user, match=curr_match,tokens=bet_tokens, prediction=player_predict)
    success_message = f"Your bet of {bet_tokens} tokens was completed successfully!"
    return render(request, 'index.html', {'message': success_message})

######## show_bets - shows personal bets to logged player - either active bets ot past bets which ended (each type accessible from different url)
@login_required
def show_bets(request):
    #bet type recieved from a query search - either "active" or "past"
    bet_type = request.GET.get('bets')
    print(f"{bet_type}")
    #creates an indicator variable for past type bets
    past = None
    win_rate_ratio = None
    #filtering player's bets according to bet type
    if bet_type == "active":
        shown_bets = Bet.objects.filter(player=request.user).filter(active=True)
    elif bet_type =="past":
        past = True
        shown_bets = Bet.objects.filter(player=request.user).filter(active=False)
        #creating statistic info of player win rate - won bets are bets with profit
        won_bets = shown_bets.filter(profit__isnull=False)
        #format ratio syntax to be not fractional, with two digit cut after decimal point
        win_rate_ratio = (len(won_bets)/len(shown_bets))*100
        win_rate_ratio = "{:.2f}".format(win_rate_ratio)
    #creates context dictionary of shown bets ,"past" indicator, total number of bets and win rate for jinja displaying purposes
    context = {
        'player_bet': shown_bets,  # Replace 'data' with the data you want to pass to the template
        'past': past,
        'total_bets': len(shown_bets),
        'win_rate': f"{win_rate_ratio}%"
    }
    print(f"{context}")
    return render(request, 'bets.html', context)  

######### my_profile - filter player's owened prized for displaying them in personal player profile's html page
@login_required
def my_profile(request):
    my_prizes = Prize.objects.filter(owner=request.user)
    context = {
        'prizes': my_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'my_profile.html', context)

###### prize_shop - displays prizes available for purchasing (prizes not owned by any player currently) in the prize shop html page
@login_required
def prize_shop(request):
    all_prizes = Prize.objects.filter(owner__isnull=True)
    context = {
        'prizes': all_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'prize_shop.html', context)

###### sorts_and_filters - a general function for sorting and filtering matches and prizes according to general query searches
## this is a function for prize shop and matches results proccessing
#this function proccess layers of sorts and filters above each other if necessary
@login_required
def sorts_and_filters(request):
    #get sort type by query search - e.g. "lowtohigh" for prizes prices or "soonertolater" for matches dates
    sort_type = request.GET.get("sort")
    #if the function was called from matches - get league filter if theres any in the query search
    league_filter = request.GET.get("league")
    #if request has a query search "?view=all" - no searched string is presented
    if request.GET.get("view") == "all":
        pass
    else:
        searched_sort = request.GET.get("search")
    #get all available active prizes and all active matches
    all_prizes = Prize.objects.filter(owner__isnull=True)
    all_matches = Match.objects.filter(active=True)
    #filtering matches according to desired league if requested
    if league_filter:
        all_matches = all_matches.filter(league__name = league_filter)
    #applying search layer for filters & sorts if desired by player - e.g "ar" search will filter games for "arsenal" and "barcelona.. (explanation continues next line)
    #(example continues) ..however applying "english league" filter will display only results for "arsenal" given the searched string mentioned above
    if searched_sort:
        all_matches = all_matches.filter(Q(team_1__name__contains=searched_sort)|Q(team_2__name__contains=searched_sort))
    #checks if the query search for sort type is for prize objects - prizes sorts by prices
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
    #assuming the query search is not for prize objects - remains with match objects
    #matches sorts by dates
    elif(sort_type == "soonertolater"):
            all_matches = all_matches.order_by("date")
    elif(sort_type == "latertosooner"):
            all_matches = all_matches.order_by("-date")
    #create context dictionary for matches
    context = {
        'matches':all_matches,
        'searchsort': searched_sort,
        'filter': league_filter
    }
    print(f"{context}")
    return render(request, 'matches.html', context)

####### buy_prize - proccesses prize object purchesed by player via prize shop and updates it as owned by the player
#in addition, updates "prize vouchers" amount for player (the app's resource for buying prizes)
@login_required
def buy_prize(request, prize_id):
    print(f"prize is: {prize_id}")
    prize = Prize.objects.get(id=prize_id)
    print(f"prize is: {prize}")
    #apply purchasing only by POST method
    if request.method == 'POST':
        #checks if the use has enough ptize vouchers to but the prize
        if (prize.price > request.user.prize_vouchers_amount):
            print(f"!! error buying. price is {prize.price} while maximum amount you have is: {request.user.prize_vouchers_amount}")
            # maximum prize vouchers amount exceeds - notify the player in home page and cancels purchase
            error_message = f"price is {prize.price} vouchers while maximum amount you have is: {request.user.prize_vouchers_amount}\n Please try again"
            return render(request, 'index.html', {'message': error_message})
        #proceeds with purchase player has sufficient prize vouchers for desired prize
        else:
            prize.owner = request.user
            print(f"Owner of {prize.name} is {prize.owner}")
            prize.save()
            request.user.prize_vouchers_amount = request.user.prize_vouchers_amount - prize.price
            request.user.save()
            print(f"current number of price vouchers for {request.user.username} is: {request.user.prize_vouchers_amount}")
            owned_prizes = Prize.objects.filter(owner=request.user) 
    #rendering players profile for viewing the new purchased prize
    context = {
        'prizes': owned_prizes
    }
    print(f"prize context is:{context}")
    return render(request, 'my_profile.html', context)