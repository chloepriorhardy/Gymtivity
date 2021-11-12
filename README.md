# Gymtivity

Computer Science Project

## AJAX API

Our initial, very limited, AJAX API has the following endpoints. Note that
we're using the "AJAX" acronym quite loosely here. These endpoints rely on
an existing user session for authentication and respond with JSON formatted
data.

| Route                      | Methods | Description                                                                                          |
| -------------------------- | ------- | ---------------------------------------------------------------------------------------------------- |
| `/api/exercise/<int:pk>/`  | `GET`   | Details for one exercise.                                                                            |
| `/api/exercises/`          | `GET`   | List all exercises.                                                                                  |
| `/api/workout/<int:pk>`    | `GET`   | Details for one workout                                                                              |
| `/api/workouts/`           | `GET`   | List all workouts.                                                                                   |
| `/api/session/<int:pk>`    | `GET`   | Details for one workout session                                                                      |
| `/api/sessions/`           | `GET`   | List all workout sessions.                                                                           |
| `/api/friends/`            | `GET`   | List all friends of the current user                                                                 |
| `/api/friend/<int:friend>` | `POST`  | Create a new friend relationship between the current user and the user identified by `<int:friend>`. |

### Example Session JSON Response

All successful responses have a top-level object with a `data` property.
Unsuccessful requests should expect a suitable HTTP status code and no response
body.

**GET** `/api/session/2/`

```json
{
  "data": {
    "session": {
      "user": {
        "last_login": null,
        "first_name": "A",
        "last_name": "Boon",
        "is_staff": false,
        "is_active": true,
        "date_joined": "2021-09-27T07:29:53Z",
        "username": "a.boon@example.com",
        "email": "a.boon@example.com",
        "id": 3
      },
      "workout": {
        "name": "Murph",
        "description": "Run, pull-ups, push-ups and another run for time.\r\n\r\nPartition the pull-ups, push-ups, and squats as needed. Start and finish with a mile run. If you\u2019ve got a twenty pound vest or body armour, wear it.",
        "rounds": 1,
        "time_limit": "00:00:00",
        "id": 3,
        "exercise_count": 4,
        "intervals": [
          {
            "workout": 3,
            "repeat": 1,
            "time_limit": "00:00:00",
            "style": {
              "name": "For Time",
              "description": "Complete the exercises as quickly as possible.",
              "quantity_name": "T",
              "id": 2
            },
            "rest": "00:00:00",
            "id": 12,
            "schemes": [
              {
                "interval": 12,
                "exercise": {
                  "name": "Run",
                  "description": "Running is a method of terrestrial locomotion allowing humans and other animals to move rapidly on foot....",
                  "source": "https://en.wikipedia.org/wiki/Running",
                  "licence": 1,
                  "id": 12
                },
                "reps": 0,
                "duration": "00:00:00",
                "distance": 1609,
                "time_limit": "00:00:00",
                "calories": 0,
                "id": 18
              },
              {
                "interval": 12,
                "exercise": {
                  "name": "Pull-ups",
                  "description": "1. Grip a pullup bar with your palms facing whichever direction you prefer. In general, having your palms facing towards you is most efficient. ...",
                  "source": "https://www.wikihow.com/Do-Pullups",
                  "licence": 1,
                  "id": 13
                },
                "reps": 100,
                "duration": "00:00:00",
                "distance": 0,
                "time_limit": "00:00:00",
                "calories": 0,
                "id": 23
              },
              {
                "interval": 12,
                "exercise": {
                  "name": "Push-up",
                  "description": "1. Get down on the ground. Lay with your toes on the ground holding yourself up with your hands. ....",
                  "source": "https://www.wikihow.com/Do-a-Push-Up",
                  "licence": 1,
                  "id": 5
                },
                "reps": 200,
                "duration": "00:00:00",
                "distance": 0,
                "time_limit": "00:00:00",
                "calories": 0,
                "id": 24
              },
              {
                "interval": 12,
                "exercise": {
                  "name": "Squat",
                  "description": "The movement begins from a standing position. Weight is often added; typically in the form of a loaded barbell, ...",
                  "source": "https://en.wikipedia.org/wiki/Squat_(exercise)",
                  "licence": 1,
                  "id": 2
                },
                "reps": 300,
                "duration": "00:00:00",
                "distance": 0,
                "time_limit": "00:00:00",
                "calories": 0,
                "id": 25
              },
              {
                "interval": 12,
                "exercise": {
                  "name": "Run",
                  "description": "Running is a method of terrestrial locomotion allowing humans and other animals to move rapidly on foot. ...",
                  "source": "https://en.wikipedia.org/wiki/Running",
                  "licence": 1,
                  "id": 12
                },
                "reps": 0,
                "duration": "00:00:00",
                "distance": 1609,
                "time_limit": "00:00:00",
                "calories": 0,
                "id": 26
              }
            ]
          }
        ]
      },
      "timestamp": "2015-06-05T11:00:00Z",
      "id": 3,
      "performance": {
        "performance": "40 minutes",
        "quantity_name": "Time"
      }
    }
  }
}
```

### CSRF

All `POST`, `PUT` and `DELETE` requests (currently only `/api/friend/<int:friend>`)
are CSRF protected. A CSRF token is available in the `meta` tag of the dashboard
page named `csrf-token`. You can use the following line of JavaScript to get the
token.

```javascript
const csrf_token = document.head.querySelector(
  'meta[name="csrf-token"]'
).content;
```

A request for the JavaScript Fetch API might then look like this.

```javascript
const request = Request("/api/session/2/", {
  method: "GET",
  headers: { "X-CSRFToken": csrf_token },
});
```
