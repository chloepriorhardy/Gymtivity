from django.db import connection


def get_friends(user_id):
    # Query the database using a connection managed by Django.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT friend.id, friend.first_name, friend.last_name "
            "FROM users_user AS user "
            "JOIN users_friend "
            "ON users_friend.user_id = user.id "
            "JOIN users_user AS friend "
            "ON users_friend.friend_id = friend.id "
            "WHERE user.id = %s;",
            [user_id],
        )

        # rows is a tuple of tuples
        rows = cursor.fetchall()

    # Create a list of dictionaries that can easily be serialized to JSON.
    # Each item in the list is a dictionary representation of a friend.
    friends = []
    for friend_id, first_name, last_name in rows:
        friends.append(
            {
                "user_id": friend_id,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

    return friends
