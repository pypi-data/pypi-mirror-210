import csv
import bcrypt
import os

def create_db():
    with open("db.csv", "w", newline='') as database:
        writer = csv.writer(database)
        writer.writerow(["username", "password"])

def signup(username, password):
    if len(username) == 0:
        raise ValueError("Please enter a valid username with characters")
    elif len(username) > 30:
        raise ValueError("The username has to be less than 30 characters")
    elif username == "username" or username == "admin":
        raise ValueError("Don't use a forbidden username")

    if not os.path.isfile("db.csv"):
        create_db()

    with open("db.csv", "r") as database:
        reader = csv.reader(database)
        for u, _ in reader:
            if username == u:
                raise ValueError("This username has already been taken")

    if len(password) < 4:
        raise ValueError("Please make sure your password is more than 4 characters")
    if password == "Password" or password == "password":
        raise ValueError("Choose a stronger password")

    # Hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    # Store the username and hashed password in the database
    with open("db.csv", "a", newline='') as database:
        writer = csv.writer(database)
        writer.writerow([username, hashed_password.decode()])


def login(username, password):
    if not os.path.isfile("db.csv"):
        create_db()

    with open("db.csv", "r") as database:
        reader = csv.reader(database)
        for u, p in reader:
            if username == u:
                if bcrypt.checkpw(password.encode(), p.encode()):
                    return "Login successful"
                else:
                    return "The password is incorrect"

    return "Sorry, username or password doesn't exist"

# Example usage when the library is imported
if __name__ == "__main__":
    username_input = input("What is your username: ")
    password_input = input("Enter your password: ")
    signup_result = signup(username_input, password_input)
    print(signup_result)

    username_input = input("What is your username: ")
    password_input = input("Enter your password: ")
    login_result = login(username_input, password_input)
    print(login_result)