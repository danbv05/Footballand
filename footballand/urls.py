from django.urls import path

from footballand import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.footballand_register, name='footballand_register'),
    path('login/', views.footballand_login, name='footballand_login'),
    path('logout/', views.footballand_logout, name='footballand_logout'),
    path('matches/', views.matches, name='matches'),
    path('bets/', views.show_bets, name='show_bets'),
    path('profile/', views.my_profile, name='my_profile'),
    path('daily_tokens/', views.daily_tokens, name='daily_tokens'),
    path('bet/<int:match_id>', views.bet_match, name='bet_match'),
    path('prize_shop/', views.prize_shop, name='prize_shop'),
    path('sort/', views.sort_results, name='sort_results'),
    path('buy_prize/<int:prize_id>', views.buy_prize, name='buy_prize'),
]