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
    submitButton.textContent = "Processing...";
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
      submitButton.textContent = "Submit";
    }
  });
});

function displayResults(data) {
  const results = data.results;
  const container = document.getElementById("resultsContainer");
  const button = document.getElementById("myButton");
  const page = [];
  let currentIndex = 0;

  let pageOne = `
        <div class="results">
            <div class="header">
                <h1><u>Your Listening Statistics</u></h1>
                <p>Uploaded File: ${data.filename}</p>
            </div>
            
            <div class="summary">
                <h2><u> Summary </u></h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Total Plays</h4>
                        <p class="stat-number">${results.total_plays}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Time Listened</h4>
                        <p class="stat-number">${results.total_time_minutes} Minutes</p>
                    </div>
                    <div class="stat-card">
                        <h4>FLAC Files</h4>
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
            <h2><u> Top 15 Songs</u></h2>
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
            </div>
        `;
  });

  pageTwo += `</div></div>`;
  page.push(pageTwo);

  // Top Artists
  let pageThree = `
        <div class="section">
            <h2><u>Top 10 Artists</u></h2>
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
            <h2> <u>Top 10 Albums </u></h2>
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

  container.innerHTML = page[0];

  button.onclick = function () {
    currentIndex = (currentIndex + 1) % page.length;
    container.innerHTML = page[currentIndex];
  };
}
