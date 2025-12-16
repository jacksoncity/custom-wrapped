document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("fileSubmitForm");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const submitButton = document.getElementById("wrappedSubmit");
    const bottomDisplay = document.getElementById("bottomDisplay");
    const resultsContainer = document.getElementById("resultsContainer");

    // Disable button and show loading
    submitButton.disabled = true;
    submitButton.textContent = "Processing...";
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
      submitButton.disabled = false;
      submitButton.textContent = "Submit";
    }
  });
});

function displayResults(data) {
  const results = data.results;
  const container = document.getElementById("resultsContainer");

  let html = `
        <div class="results">
            <div class="header">
                <h2>Your Listening Statistics</h2>
                <p>File: ${data.filename}</p>

            </div>
            
            <div class="summary">
                <h3> Summary</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Total Plays</h4>
                        <p class="stat-number">${results.total_plays}</p>
                    </div>
                    <div class="stat-card">
                        <h4>Time Listened</h4>
                        <p class="stat-number">${results.total_time_hours} hours</p>
                    </div>
                    <div class="stat-card">
                        <h4>FLAC Files</h4>
                        <p class="stat-number">${results.total_files}</p>
                    </div>
                </div>
            </div>
    `;

  // Top Songs
  html += `
        <div class="section">
            <h3> Top 15 Songs</h3>
            <div class="list">
    `;

  results.top_songs.forEach((song) => {
    html += `
            <div class="list-item">
                <span class="rank">${song.rank}</span>
                <div class="song-info">
                    <strong>${song.artist}</strong> - "${song.title}"
                    <br>
                    <small>Album: ${song.album} | Plays: ${song.plays}</small>
                </div>
            </div>
        `;
  });

  html += `</div></div>`;

  // Top Artists
  html += `
        <div class="section">
            <h3> Top 10 Artists</h3>
            <div class="list">
    `;

  results.top_artists.forEach((artist) => {
    html += `
            <div class="list-item">
                <span class="rank">${artist.rank} )</span>
                <div class="artist-info">
                    <strong>${artist.artist}</strong>
                    <br>
                    <small>${artist.plays} plays</small>
                </div>
            </div>
        `;
  });

  html += `</div></div>`;

  // Top Albums
  html += `
        <div class="section">
            <h3> Top 10 Albums</h3>
            <div class="list">
    `;

  results.top_albums.forEach((album) => {
    html += `
            <div class="list-item">
                <span class="rank">${album.rank}</span>
                <div class="album-info">
                    "<strong>${album.album}</strong>" by ${album.artist}
                    <br>
                    <small>${album.plays} plays</small>
                </div>
            </div>
        `;
  });

  html += `</div></div></div>`;

  container.innerHTML = html;
}
