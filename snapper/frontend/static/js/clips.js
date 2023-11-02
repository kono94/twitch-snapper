let page = 1;
let loading = false;
let iframeCheckBlocked = false;
let allContentLoaded = false; // Flag to indicate if all content has been loaded
const perPage = 4;
let clips = [];
const clipsContainer = document.getElementById("main-clips-container");
let sortBy = "latest"; // Default sort
let lastUtcTimestamp = utcTimestampFromPrevDay(7);
async function initialLoad() {
  while (
    window.innerHeight >= document.body.offsetHeight &&
    !allContentLoaded
  ) {
    await loadClips();
    page++;
  }
}
initialLoad();

// Function to fetch and render clips
async function loadClips() {
  if (loading || allContentLoaded) return; // Prevent additional fetches if already loading
  loading = true;
  const fetchRequest = `/api/clips?page=${page}&per_page=${perPage}&sort_by=${sortBy}${
    lastUtcTimestamp == null ? "" : `&last_timestamp_iso=${lastUtcTimestamp}`
  }`;
  const response = await fetch(fetchRequest);

  tmp = await response.json();
  clips = clips.concat(tmp);
  if (tmp.length < perPage) {
    allContentLoaded = true; // Set flag to true because all content has been loaded
  }

  tmp.forEach((clip) => {
    // Create and append new clip elements
    const clipDiv = document.createElement("div");
    clipDiv.className = "bg-secondary clip";
    // Add a thumbnail image
    const thumbnail = document.createElement("img");
    thumbnail.src = clip.thumbnail_url;
    thumbnail.className = "clip-thumbnail";

    clipDiv.innerHTML = `
          [${clip.id}] <a href="https://clips.twitch.tv/${
      clip.twitch_clip_id
    }" target="_blank">${clip.twitch_clip_id}</a><br>
          Channel: ${clip.stream.channel_name}<br>
          Keyword trigger: <img class="keyword_emote" src="${
            clip.keyword_trigger.image_url
          }" alt="${clip.keyword_trigger.value}"><br>
          Keyword amount: ${clip.keyword_count}<br>
          When: ${clip.created}<br>
          <div class="rating-text">
            <span>Rating:</span>
            <span class="rating-value-text" data-clip-id="${
              clip.id
            }">${formatDecimalOfRating(clip.rating)}</span>
          </div>`;

    const starRatingDiv = document.createElement("div");
    starRatingDiv.className = "star-rating prevent-select";
    starRatingDiv.setAttribute("data-clip-id", clip.id);
    // Create the 5 star spans and append to the main div
    for (let i = 1; i <= 5; i++) {
      const starSpan = document.createElement("span");
      starSpan.className = "star";
      starSpan.setAttribute("data-value", i);
      starSpan.innerHTML = "&#9733;";
      starRatingDiv.appendChild(starSpan);
    }

    // Add click event to thumbnail
    thumbnail.addEventListener("click", () => loadIframe(clip, clipDiv));

    clipDiv.appendChild(starRatingDiv);
    clipDiv.appendChild(thumbnail);
    clipsContainer.appendChild(clipDiv);

    addStarListeners(starRatingDiv);
    highlightStars(starRatingDiv, clip.rating);
  });
  loading = false;
}

// Function to replace thumbnail with iframe
function loadIframe(clip, clipDiv) {
  const iframe = document.createElement("iframe");
  iframe.src = `https://clips.twitch.tv/embed?clip=${clip.twitch_clip_id}&parent=localhost`;
  iframe.className = "clip-iframe";
  iframe.allowFullscreen = true;
  iframe.style.position = "relative";
  iframe.style.height = "100%";
  iframe.style.width = "100%";
  iframe.frameBorder = "0";

  const thumbnail = clipDiv.querySelector(".clip-thumbnail");
  clipDiv.replaceChild(iframe, thumbnail);
}

function resetClipsAndContainer() {
  page = 1; // Reset to first page
  document.getElementById("main-clips-container").innerHTML = ""; // Clear existing clips
  allContentLoaded = false;
  clips = [];
  loadClips(); // Reload clips
}

setInterval(() => {
  const clipDivs = document.querySelectorAll(".clip");
  clipDivs.forEach((clipDiv, index) => {
    const iframe = clipDiv.querySelector("iframe");
    if (iframe === null) {
      return;
    }
    if (!isInViewport(iframe)) {
      // Replace iframe with thumbnail
      const clip = clips[index];

      //replace iframes with thumbnails - inline
      const thumbnail = document.createElement("img");
      thumbnail.src = clip.thumbnail_url;
      thumbnail.className = "clip-thumbnail";

      // Add click event to thumbnail
      thumbnail.addEventListener("click", () => loadIframe(clip, clipDiv));
      clipDiv.replaceChild(thumbnail, iframe);
    }
  });
  iframeCheckBlocked = false;
}, 5000);

/****************
 * LISTENERS
 ****************/

// Infinite scrolling logic
window.addEventListener("scroll", () => {
  if (loading || allContentLoaded) return; // If already loading, return

  if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
    // Reached the bottom, load more clips
    page++;
    loadClips();
  }
});

document.getElementById("sort-select").addEventListener("change", function () {
  sortBy = this.value;
  resetClipsAndContainer();
});

document.getElementById("time-select").addEventListener("change", function () {
  if (this.value == "-1") {
    lastUtcTimestamp = null;
  } else {
    lastUtcTimestamp = utcTimestampFromPrevDay(this.value);
  }
  resetClipsAndContainer();
});

/*************
    UTILITY
**************/
function utcTimestampFromPrevDay(lastDaysAmount) {
  return new Date(
    new Date().getTime() - lastDaysAmount * 24 * 60 * 60 * 1000
  ).toISOString();
}

function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <=
      (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}
