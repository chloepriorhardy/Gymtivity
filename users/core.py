from collections import deque
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


def get_new_friends(user):
    # Query the database using a connection managed by Django.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT "
            "    user.id AS user_id, "
            "    user.first_name AS user_first_name, "
            "    user.last_name AS user_last_name, "
            "    friend.id AS friend_id, "
            "    friend.first_name AS friend_first_name, "
            "    friend.last_name AS friend_last_name "
            "FROM users_friend "
            "JOIN users_user AS user "
            "ON users_friend.user_id = user.id "
            "JOIN users_user AS friend "
            "ON users_friend.friend_id = friend.id;"
        )

        # rows is a tuple of tuples
        rows = cursor.fetchall()

    # Build the graph
    graph = {}
    for row in rows:
        # Each row has six items, the first three are for one user,
        # the last three for the second user.
        user = (row[0], row[1], row[2])
        friend = (row[3], row[4], row[5])
        _add_friend(graph, user, friend)

    # Transform friends ready for JSON serialization.
    # Same layout as we used in `get_friends`.
    new_friends = []
    for friend_id, first_name, last_name in _find_new_friends(graph, user):
        new_friends.append(
            {
                "user_id": friend_id,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

    return new_friends


def _add_friend(graph, user, friend):
    if user not in graph:
        # Initialize a new, empty set if we've not seen this user before
        graph[user] = set()
    if friend not in graph:
        # Same again for the friend user.
        graph[friend] = set()

    # A the friend object to the set of user that are adjacent to `user`
    graph[user].add(friend)
    # A the user object to the set of user that are adjacent to `friend`
    graph[friend].add(user)


def _find_new_friends(graph, user, limit=5):
    queue = deque([user])
    visited = set([user])
    current_friends = graph[user] | visited
    potential_friends = set()

    while queue and len(potential_friends) < limit:
        node = queue.popleft()
        for friend in graph[node]:
            if friend not in visited:
                queue.append(friend)
                visited.add(friend)
            if friend not in current_friends:
                potential_friends.add(friend)

    return list(potential_friends)[:limit]
