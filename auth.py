import json
import os
import hashlib
import getpass


USER_FILE = "data/users.json"



def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()



def load_users():

    if not os.path.exists(USER_FILE):

        return {}

    with open(USER_FILE, "r") as file:

        return json.load(file)



def save_users(users):

    os.makedirs(
        "data",
        exist_ok=True
    )


    with open(USER_FILE, "w") as file:

        json.dump(
            users,
            file,
            indent=4
        )



def create_user():

    print("\nNo users found.")
    print("Create your Corgi OS account.\n")


    username = input(
        "Username: "
    )


    while True:

        password = getpass.getpass(
            "Password: "
        )

        confirm = getpass.getpass(
            "Confirm password: "
        )


        if password != confirm:

            print(
                "Passwords do not match!"
            )

            continue


        break



    auto = input(
        "\nEnable automatic login? (y/n): "
    ).lower()


    autologin = auto == "y"



    users = load_users()


    users[username] = {

        "password":
            hash_password(password),

        "admin":
            True,

        "autologin":
            autologin
    }


    save_users(users)


    print(
        "\nAccount created!"
    )



def login():

    users = load_users()

    if not users:
        create_user()
        users = load_users()

    # Check for an autologin user first
    for username, data in users.items():
        if data.get("autologin", False):
            print(f"\nAutomatically logged in as {username}! 🐶")
            return {
                "username": username,
                "admin": data["admin"],
                "password": data["password"],
            }

    print("\nCorgi OS Login\n")

    while True:

        username = input("Username: ")

        if username not in users:
            print("User does not exist.")
            create = input("Create a new user? y/N: ")
            if create.lower() == "y":
                create_user()
                users = load_users()
                print()
                continue
            print()
            continue

        password = getpass.getpass("Password: ")

        if hash_password(password) != users[username]["password"]:
            print("Incorrect password.\n")
            continue

        print("\nLogin successful!")

        return {
            "username": username,
            "admin": users[username]["admin"],
            "password": users[username]["password"],
        }
