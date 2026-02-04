document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("fileSubmitForm");
  const loadingIndicator = document.getElementById("loadingIndicator");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const submitButton = document.getElementById("wrappedSubmit");
    const bottomDisplay = document.getElementById("bottomDisplay");
    const resultsContainer = document.getElementById("resultsContainer");

    // Disable button and show loading while processing
    submitButton.disabled = true;
    loadingIndicator.style.display = "block";
    resultsContainer.innerHTML = "<p>Processing your file...</p>";
    bottomDisplay.style.display = "block";

    try {
      const response = await fetch("/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        displayResults(data);
      } else {
        resultsContainer.innerHTML = `
                    <div class="error">
                        <h2>Error</h2>
                        <p>${data.error}</p>
                    </div>
                `;
      }
    } catch (error) {
      resultsContainer.innerHTML = `
                <div class="error">
                    <h2>Network Error</h2>
                    <p>Please check your connection and try again.</p>
                </div>
            `;
    } finally {
      // Re-enable button
      loadingIndicator.style.display = "none";
      submitButton.disabled = false;
    }
  });
});

function displayResults(data) {
  const results = data.results;
  const container = document.getElementById("resultsContainer");
  const backgroundElement = document.getElementById("bottomDisplay");
  const button = document.getElementById("myButton");
  const page = [];
  let currentIndex = 0;

  let pageOne = `
        <div class="results">
            <div class="header">
                <h1>Your Listening Statistics</h1>
                <p>Uploaded File: ${data.filename}</p>
            </div>
            
            <div class="summary">
                <h2> Summary </h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Total Plays:</h4>
                        <p class="stat-number">${results.total_plays}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Time Listened:</h4>
                        <p class="stat-number">${results.total_time_minutes} Minutes</p>
                    </div>
                    <div class="stat-card">
                        <h4>FLAC Files:</h4>
                        <p class="stat-number">${results.total_files}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
  page.push(pageOne);

  // Top Songs
  let pageTwo = `
        <div class="section">
            <h2> Top 15 Songs</h2>
            <div class="list">
    `;

  results.top_songs.forEach((song) => {
    pageTwo += `
            <div class="list-item">
                <span class="rank">${song.rank})</span>
                <div class="song-info">
                    <strong>${song.artist}</strong> - "${song.title}"
                    <br>
                    <small>Album: ${song.album} | <b>Plays: ${song.plays}</b></small>
                </div>
                <br>
            </div>
        `;
  });

  pageTwo += `</div></div>`;
  page.push(pageTwo);

  // Top Artists
  let pageThree = `
        <div class="section">
            <h2>Top 10 Artists</h2>
            <div class="list">
    `;

  results.top_artists.forEach((artist) => {
    pageThree += `
            <div class="list-item">
                <span class="rank">${artist.rank})</span>
                <div class="artist-info">
                    <strong>${artist.artist}</strong>
                    <br>
                    <small>${artist.plays} plays</small>
                </div>
            </div>
        `;
  });

  pageThree += `</div></div>`;
  page.push(pageThree);

  // Top Albums
  let pageFour = `
        <div class="section">
            <h2> Top 10 Albums </h2>
            <div class="list">
    `;

  results.top_albums.forEach((album) => {
    pageFour += `
        <div class="list-item">
            <span class="rank">${album.rank})</span>
            <div class="album-info">
                "<strong>${album.album}</strong>" by ${album.artist}
                <br>
                <small>${album.plays} plays</small>
            </div>
        </div>
    `;
  });

  pageFour += `</div></div></div>`;
  page.push(pageFour);

  backgrounds = [
    "url('/static/assets/bg-test.png')",
    "url('/static/assets/bg-test-1.png')",
    "url('/static/assets/bg-test-2.png')",
  ];

  container.innerHTML = page[0];
  backgroundElement.style.backgroundImage = backgrounds[0];

  button.onclick = function () {
    // Fade out
    backgroundElement.style.opacity = "0";
    backgroundElement.style.transition = "opacity 0.5s ease-out";
    container.style.opacity = "0";
    container.style.transition = "opacity 0.5s ease-out";

    setTimeout(() => {
      // Change content
      currentIndex = (currentIndex + 1) % page.length;
      backgroundElement.style.backgroundImage =
        backgrounds[currentIndex % backgrounds.length];
      container.innerHTML = page[currentIndex];

      // Fade in
      container.style.opacity = "1";
      backgroundElement.style.opacity = "1";
    }, 500); // Match the transition duration
  };
}
