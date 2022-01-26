
// Read the CSRF token from this page's header.
// We'll need to send this token to our API with every AJAX request.
const csrf_token = document.head.querySelector(
  'meta[name="csrf-token"]'
).content;

// The request object for our `friends` API endpoint.
// We'll pass to this to `fetch()`.
const friendsRequest = new Request("/api/friends/", {
  method: "GET",
  headers: { "X-CSRFToken": csrf_token },
});

// A helper function that creates a list group item, as a string, for a single friend
function makeFriendListItem(friend) {
  const friendListItemT = `
    <a href="/profile/${friend.user_id}" class="list-group-item list-group-item-action">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">${friend.first_name} ${friend.last_name}</h5>
          <small>Last workout 3 days ago</small>
        </div>
    </a>
  `;
  return friendListItemT;
}

function handleFriendData(data) {
  // The list group element that items will get appended to upon processing data
  // retrieved from our `friends` API endpoint.
  const friendsList = document.getElementById("friendList");

  // Remove any existing items from the list.
  friendsList.innerHTML = "";

  // Append a new list item for each friend in our data.
  data.data.forEach((friend) => {
    friendsList.insertAdjacentHTML(
      "beforeend",
      makeFriendListItem(friend)
    );
  });
}

// Attach a callback function to the `show` event of our model dialog.
// Every time the dialog is shown, we'll fetch a list of friends from
// the API.
const friendsModalEl = document.getElementById("friendsModal");
friendsModalEl.addEventListener("show.bs.modal", function (event) {
  fetch(friendsRequest)
    .then((response) => {
      if (response.status === 200) {
        response.json().then(handleFriendData);
      } else {
        throw new Error("Something went wrong on api server!");
      }
    })
    .catch((error) => {
      console.error(error);
    });
});
