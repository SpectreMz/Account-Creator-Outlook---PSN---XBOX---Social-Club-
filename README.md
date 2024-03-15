# Account-Creator-Outlook---PSN---XBOX---Social-Club-
Account Creator (Outlook - PSN - XBOX - Social Club) - Written in Python

Features:
1) Custom Domain or Compeltely random emails.
2) Custom Password and Dob.
3) Possibility to auto-join a GTA Crew.
4) Set recovery mail automatically using [Mail In A Box] (https://mailinabox.email/) Service.

Feel free to push updates and eventually fixes.

Tool was made only for fun as style-exercise.

====================================================
I will not be responsible for your usage or eventual consequence.
Use at your own risk.
P.s: there are bugs to fix, so if you want fix it and push the fix to my repo.
Tool is in Italian, feel free to make it international.

INSTRUCTIONS
1) Create a folder and put inside the __main__.py
2) Create a folder in the same path of __main__.py file and call it "Accounts"
3) Install requirements using pip (advice python3.12)
4) Be sure that Google Chrome is installed on your PC, else the tool can't work.
5) To edit Tool config, open __main__.py with Visual Studio Code and edit the CONFIGS part.
6) To edit recovery Mail In A Box, need to edit the following parts:
   Function wait_imap_verification_mail_not_async
   wait_imap_verification_mail
   push_mail_creation_to_mitb
   (Probably need also edit few regexs if not live in italy)

7) Follow the video Tutorial.mp4 in the git repository to understand how works.
====================================================

TIPS
1) To avoid phone number verification change your IP
2) In Accounts folder will find folder for each account, is present on it a json file with informations and a picture of linked account in social club.
Json structure is like:

{
    "email": "XXXXXXX@hotmail.com",
    "recovery_mail": "XXXXXXX@XXXXXXX.it",
    "password": "XXXXXXX",
    "dob": [
        "1",
        "4",
        "1994"
    ],
    "city": "XXXXXXX",
    "zip_code": "00055",
    "first_name": "XXXXXXX",
    "last_name": "XXXXXXX",
    "xbox_gamertag": "XXXXXXX",
    "psn_gamertag": "XXXXXXX",
    "creation_date": "15/03/2024 10:42:00"
}

For further help, send me a message on telegram https://t.me/iosonomanuuu


