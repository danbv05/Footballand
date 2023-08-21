# general info

1. Project link in render: https://footballand.onrender.com/
2. Project link in github: https://github.com/danbv05/Footballand
3. Admin superuser details: username - Dan ; Password - 123
4. Simple user details: username - jabbajubba95 ; Password - jabba95

# Footballand
python manage.py runserver
1. This project is a football games betting game app
   a. Each play has ingame currency ("tokens") to bet games (not real money)
   b. By winning bets the player earns more tokens and another ingame currency called "Prize vouchers" - this currency lets the user buy prizes from the app's prize shop 
2. Upon entry to app - you will be requested to log in/ register
3. By successfully logging in - you will get access to the app's features
   a.Home Page - displays updates about finished matches you made a bet on and lets you claim 10 free tokens each day (once only)
   b.Matches - displays active matches (that has not been placed yet) and lets you make a bet with your token (it also contains search, filter by league and sort by dates options)
   c.Active Bets - shows the player his current active bets
   d.Prize Shop - displays all avilable prizes & their prices in prize vouchers and lets the player buy them (it also contains sort by prices option)
   e.My Profile - lets the player view all of his past bets and contains a display of all of his owned prizes
4. App's admin adds matches and prizes from django admin's feature
