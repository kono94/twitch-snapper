// Using 'function' instead of 'const', mainly because of function hoisting and readability
function addStarListeners(ratingDiv) {
  const stars = ratingDiv.querySelectorAll(".star");
  stars.forEach((star, index) => {
    star.addEventListener("click", async (e) => {
      const value = 5 - index;
      const clipId = ratingDiv.getAttribute("data-clip-id");
      // Send value and clipId to the server
      const new_rating = await rateClip(clipId, value);
      highlightStars(ratingDiv, new_rating);
      const ratingTextSpan = document.querySelector(
        `.rating-value-text[data-clip-id="${clipId}"]`
      );
      ratingTextSpan.innerHTML = formatDecimalOfRating(new_rating);
    });
  });
}
function formatDecimalOfRating(rating) {
  return Number(rating).toFixed(1);
}

function highlightStars(ratingDiv, value) {
  const stars = ratingDiv.querySelectorAll(".star");
  let fullStars = Math.floor(value);
  let partialFill = (value % 1) * 100;

  stars.forEach((star, index) => {
    const starValue = 5 - index; // Assuming data-value starts from 5
    let partialDiv = star.querySelector(".partial-fill");

    if (!partialDiv) {
      partialDiv = document.createElement("div");
      partialDiv.classList.add("partial-fill");
      partialDiv.innerHTML = "&#9733;";
      star.appendChild(partialDiv);
    }

    if (starValue <= fullStars) {
      star.classList.add("active");
      partialDiv.style.width = "0%";
    } else if (starValue === fullStars + 1 && partialFill > 0) {
      star.classList.remove("active");
      partialDiv.style.width = `${partialFill}%`;
    } else {
      star.classList.remove("active");
      partialDiv.style.width = "0%";
    }
  });
}

async function updateRating(clipId, new_rating) {
  const response = await fetch(`/api/clip/${clipId}/rate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rating: new_rating }),
  });

  const data = await response.json();
  console.log("New Rating: ", data.new_rating);
  return data.new_rating;
}
function hasUserVoted(clipId) {
  return !!localStorage.getItem(`voted_${clipId}`);
}

function markUserAsVoted(clipId) {
  // localStorage.setItem(`voted_${clipId}`, 'true');
}

async function rateClip(clipId, rating) {
  if (!hasUserVoted(clipId)) {
    new_rating = await updateRating(clipId, rating);
    console.log(new_rating);
    markUserAsVoted(clipId);
    return new_rating;
  } else {
    console.error("You've already voted!");
    throw Exception();
  }
}
