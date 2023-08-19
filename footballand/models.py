from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from django.utils import timezone
# Create your models here.
# class Leagues(Enum):
#     La_Liga = 1
#     Premier_League = 2
#     Serie_A= 3
#     Bundes_Liga = 4
#     Ligue_1 = 5
#     Ligat_Al = 6

class Player(AbstractUser):
    bet_tokens_amount = models.IntegerField(null=False, default=500)
    prize_vouchers_amount = models.IntegerField(null=False, default=0)
    daily_token_used = models.BooleanField(default=False)
    previous_login = models.DateTimeField(null=True, blank=True)

class League(models.Model):
    name = models.CharField(max_length=500, default="FC Barcelona", null=False)
    country = models.CharField(max_length=500, default="FC Barcelona", null=False)
    
    def __str__(self):
        return f"{self.name}"
    
class Footballteam(models.Model):
    name = models.CharField(max_length=500, default="FC Barcelona", null=False)
    symbol = models.ImageField(upload_to="teams_symbols", default="https://loremflickr.com/cache/resized/3849_14857076316_4e420c7870_n_320_240_nofilter.jpg")
    league = models.ForeignKey(League, null = False, on_delete=models.CASCADE)
    table_position = models.IntegerField(default=1, null= False)

    def __str__(self):
        return f"{self.name}"

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
    win_ratio_team_1 = models.FloatField (default=1, null= False)
    win_ratio_team_2 = models.FloatField (default=1, null= False)
    draw_ratio = models.FloatField (default=1, null= False)
    active = models.BooleanField(default=True)  # Set default to True for active items
    result_team_1 = models.IntegerField(null=True, blank=True)
    result_team_2 = models.IntegerField(null=True, blank=True)
    def clean(self):
        if self.team_1 == self.team_2:
            raise models.ValidationError("Both teams cannot be the same.")

    def __str__(self):
        return f"{self.team_1} VS {self.team_2}"

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

    
