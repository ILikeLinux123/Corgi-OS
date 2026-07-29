# corgi.py


import random


# -------------------------
# Corgi Faces
# -------------------------

NORMAL = r"""
      / \_/\
 ____/ •ᴥ• )
/         O
\   (_____/
/_____/   U
"""


WARNING = r"""
        :/

      / \_/\
 ____/ •-• )
/         O
\   (_____/
/_____/   U
"""


PANIC = r"""
        CORGI PANIC
        I MEAN KERNEL PANIC 

        :'(

        / \_/\
   ____/  x x)
  /         O
 /   (_____/
/_____/   U
"""


SAD = r"""

        :(

      / \_/\
 ____/ •︿• )
/         O
\   (_____/
/_____/   U
"""


# -------------------------
# Panic Messages
# -------------------------

COMMON_MESSAGES = [

    "I don't think that's supposed to happen...",

    "Uh oh.",

    "I may have made a small mistake...",

    "That was not in da training manual.",

    "Have you tried turning it off and on again?",

    "One moment... my tiny brain is thinking.",

    "Something went wrong. Probably my fault.",

    "Da kernel is having a bad day.",

    "I need a moment to process this.",

]


UNCOMMON_MESSAGES = [

    "I blame da keyboard.",

    "Da computer sneezed.",

    "Da bits went somewhere day shouldn't.",

    "Da cables looked suspicious.",

    "My paws may have pressed something.",

    "Da kernel slipped on a virtual banana.",

    "I was not chewing on da code, I promise.",

]


RARE_MESSAGES = [

    "CRITCLE SYSTEM NOT FOUND!1!1!!",

    "da treats directory has vanished.",

    "I deleted my own homework folder.",

    "Error 418: I Corgi.",

    "Da kernel looked at me wierd.",

    "Please tell da humans I tried my best.",

    "I have lost my bones.sys file.",

]


ULTRA_RARE_MESSAGES = [

    "Wait... who compiled ME?",

    "Do not open /SYSTEM/DO_NOT_LOOK.",

    "da paw has touched da forbidden file.",

    "I am da corgi.",

    "da compooter isnt doing da compootering",

]


# -------------------------
# Message Generator
# -------------------------

def panic_message():

    roll = random.randint(1, 1000)


    # 90%
    if roll <= 900:

        return random.choice(
            COMMON_MESSAGES
        )


    # 9%
    elif roll <= 990:

        return random.choice(
            UNCOMMON_MESSAGES
        )


    # 0.9%
    elif roll <= 999:

        return random.choice(
            RARE_MESSAGES
        )


    # 0.1%
    else:

        return random.choice(
            ULTRA_RARE_MESSAGES
        )



# -------------------------
# Display
# -------------------------

def show(face):

    print(face)



def panic():

    print(PANIC)

    print()

    print(
        "Corgi says:"
    )

    print(
        panic_message()
    )