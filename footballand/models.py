from django.db import models
from django.contrib.auth.models import AbstractUser

#Player class - abstract class of django user
#bet_tokens_amount - currency for betting matches
#prize_vouchers_amount - currency for buying prizes
#daily_token_used - boolean indicating if player has claimed free tokens once a day
#previous_login - datetime field saving previous session login time
class Player(AbstractUser):
    bet_tokens_amount = models.IntegerField(null=False, default=500)
    prize_vouchers_amount = models.IntegerField(null=False, default=0)
    daily_token_used = models.BooleanField(default=False)
    previous_login = models.DateTimeField(null=True, blank=True)

class League(models.Model):
    name = models.CharField(max_length=500, default="La Liga", null=False)
    
    def __str__(self):
        return f"{self.name}"
    
class Footballteam(models.Model):
    name = models.CharField(max_length=500, default="FC Barcelona", null=False)
    symbol = models.ImageField(upload_to="teams_symbols", default="https://loremflickr.com/cache/resized/3849_14857076316_4e420c7870_n_320_240_nofilter.jpg")

    def __str__(self):
        return f"{self.name}"
    
#Match class - containing match attributes
#profit_ratio - sets profit ratio for player (tokens & prize vouchers) for each outcome(team 1 wins, team 2 wins, draw)
#if player prediction was right - he recieves tokens & prize voucher by the formula: {bet tokens}*{profit ratio}
# e.g for profit ratio - team 1 profit X2, team 2 profit X4, draw profit X3
# continue e.g - if player bet 100 tokens on team 2 and they won - player recieves 400 tokens & prize vouchers
#result_team_1 + result_team_2 combined form the match result: e.g Liverpool (team_1) vs Chelsea(team_2) 4-0 
#"active" attribute - if TRUE, indicates the match hasn't been placed yet
class Match(models.Model):
    team_1 = models.ForeignKey(
    Footballteam,
    on_delete=models.CASCADE,
    related_name='team_1'
    )
    team_2 = models.ForeignKey(
        Footballteam,
        on_delete=models.CASCADE,
        related_name='team_2'
    )
    date = models.DateTimeField("Match date: ")
    league = models.ForeignKey(League, null = False, on_delete=models.CASCADE)
    profit_ratio_team_1_win = models.FloatField (default=1, null= False)
    profit_ratio_team_2_win = models.FloatField (default=1, null= False)
    profit_ratio_draw = models.FloatField (default=1, null= False)
    active = models.BooleanField(default=True)
    result_team_1 = models.IntegerField(null=True, blank=True)
    result_team_2 = models.IntegerField(null=True, blank=True)
    def clean(self):
        if self.team_1 == self.team_2:
            raise models.ValidationError("Both teams cannot be the same.")

    def __str__(self):
        return f"{self.team_1} VS {self.team_2}"

#Bet class - bet object for each bet a player has made (each bet is for a specific match)
#"active" attribute - if TRUE, indicates the bet wasn't concluded yet
#profit - amount of tokens & prize vouchers the player has earned if he won the bet
class Bet(models.Model):
    player = models.ForeignKey(Player, null = False, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, null = False, on_delete=models.CASCADE)
    OUTCOME_CHOICES = (
        ('1', 'Team 1 wins'),
        ('2', 'Team 2 wins'),
        ('X', 'Draw'),
    )
    prediction = models.CharField(max_length=1, choices=OUTCOME_CHOICES)
    tokens = models.IntegerField(default=1, null= False)
    active = models.BooleanField(default=True)  # Set default to True for active items
    profit = models.IntegerField(null = True, blank = True)
    def __str__(self):
        return f"***{self.match}***"

class Prize(models.Model):
    name = models.CharField(max_length=500, null=False)
    image = models.ImageField(upload_to="prizes_images", default="https://loremflickr.com/cache/resized/3849_14857076316_4e420c7870_n_320_240_nofilter.jpg")
    price = models.IntegerField(default=100, null=False)
    owner = models.ForeignKey(Player, null = True, blank = True, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}"

    
