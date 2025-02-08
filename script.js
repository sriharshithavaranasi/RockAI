// 🎵 Step 1: Spotify API Credentials (Replace with your actual keys)
const CLIENT_ID = '4f166eaf6af848b7b64920d747696c86';  
const CLIENT_SECRET = '03084f1ca8d4406f958d389231833c27';  

// 🎯 Step 2: Spotify API URLs
const TOKEN_URL = 'https://accounts.spotify.com/api/token'; // URL to get the API token
const ARTISTS_URL = 'https://api.spotify.com/v1/browse/new-releases'; // URL to get new albums (artists included)

// 🔑 Step 3: Variable to store API token
let spotifyToken = '';  
let artists = []; // This will store artist data from the API
let currentIndex = 0; // Track which artist is currently displayed

// 🎫 Get Spotify API Token & Refresh It Automatically
async function getSpotifyToken() {
    try {
        const response = await fetch(TOKEN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}`
        });

        const data = await response.json();
        spotifyToken = data.access_token; // Store token
        console.log("✅ New Spotify Token:", spotifyToken);

        // 🎯 Automatically Refresh Token Every 55 Minutes (Before Expiry)
        setTimeout(getSpotifyToken, 55 * 60 * 1000); // Refresh token every 55 minutes
    } catch (error) {
        console.error("❌ Error getting Spotify token:", error);
    }
}


// 🎧 Fetch Artists (Fixes Previews for Left/Right Navigation)
async function fetchArtists() {
    try {
        const response = await fetch(ARTISTS_URL, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${spotifyToken}` }
        });

        const data = await response.json();

        // 🎸 Fetch top songs for each artist
        artists = await Promise.all(
            data.albums.items.slice(0, 5).map(async album => {
                const artist = album.artists[0];
                const topTrack = await getTopTracks(artist.id); // Get top song

                return {
                    name: artist.name,
                    song: topTrack ? topTrack.song : "No Songs Available",
                    image: album.images.length > 1 ? album.images[1].url : 'https://via.placeholder.com/250',
                    preview: topTrack ? topTrack.preview : null
                };
            })
        );

        console.log("✅ Artists Fetched:", artists);
        displayArtist(currentIndex);
    } catch (error) {
        console.error("❌ Error fetching artists:", error);
    }
}


function displayArtist(index) {
    if (artists.length === 0) return;

    const artistTile = document.getElementById("artistTile");
    const artist = artists[index];

    artistTile.innerHTML = `
        <img src="${artist.image}" alt="${artist.name}">
        <h2>${artist.song}</h2>
        <p>${artist.name}</p>
        <audio id="audioPlayer">
            <source id="audioSource" src="${artist.preview || ''}" type="audio/mpeg">
        </audio>
        <button class="remix-btn" onclick="remixSong('${artist.song}')">Remix This Song</button>
        <button id="playPreviewBtn" class="remix-btn" onclick="playPreview()" ${artist.preview ? '' : 'disabled'}>🎵 Play 30s Preview</button>
    `;

    console.log(`🎧 Now displaying: ${artist.name} - ${artist.song} (Preview: ${artist.preview || 'None'})`);
}




// 🎶 Step 8: Next Artist (Right Arrow)
function nextArtist() {
    currentIndex = (currentIndex + 1) % artists.length; // Loop back to the first if at the end
    displayArtist(currentIndex);
}

// 🎶 Step 9: Previous Artist (Left Arrow)
function prevArtist() {
    currentIndex = (currentIndex - 1 + artists.length) % artists.length; // Loop back to the last if at the beginning
    displayArtist(currentIndex);
}

// 🎛️ Step 10: Remix Button (Placeholder Function)
function remixSong(songName) {
    alert(`🎸 Remixing "${songName}"... 🎛️🔥`);
}

// 🎤 Search for an Artist by Name with Multiple Results
// 🎤 Search for an Artist by Name with Song Previews
async function searchArtist() {
    const query = document.getElementById("searchBar").value.trim();
    if (query.length < 2) return; // Prevent searching too early

    try {
        // 🔥 Use Spotify's Search API to Find Artists
        const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=artist`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${spotifyToken}` }
        });

        const data = await response.json();
        if (!data.artists.items.length) return; // Stop if no artists found

        const artist = data.artists.items[0]; // Get the first artist match
        const topTrack = await getTopTracks(artist.id); // Fetch top track

        // 🎸 Store artist details
        artists = [{
            name: artist.name,
            song: topTrack ? topTrack.song : "No Songs Available",
            image: artist.images.length > 0 ? artist.images[0].url : 'https://via.placeholder.com/250',
            preview: topTrack ? topTrack.preview : null
        }];

        currentIndex = 0;
        displayArtist(currentIndex);
    } catch (error) {
        console.error("❌ Error searching for artist:", error);
    }
}



// 🎧 Get an Artist's Top Tracks with Previews
async function getTopTracks(artistId) {
    
    try {
        // 🔥 Fetch the artist's top 10 tracks
        const response = await fetch(`https://api.spotify.com/v1/artists/${artistId}/top-tracks?market=US`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${spotifyToken}` }
        });

        const data = await response.json();
        if (!data.tracks || data.tracks.length === 0) return null; // No tracks found

        // 🎵 Find the first song that has a preview URL
        const track = data.tracks.find(track => track.preview_url !== null);

        return track
            ? { song: track.name, preview: track.preview_url }
            : null; // Return null if no preview found
    } catch (error) {
        console.error("❌ Error fetching top tracks:", error);
        return null;
    }
}

function playPreview() {
    const audioPlayer = document.getElementById("audioPlayer");
    const audioSource = document.getElementById("audioSource");

    if (!audioPlayer || !audioSource || !audioSource.src) {
        console.error("❌ No audio source found or invalid.");
        return;
    }

    console.log(`🎵 Playing preview: ${audioSource.src}`);

    // Pause any playing audio before playing new preview
    document.querySelectorAll("audio").forEach(audio => audio.pause());

    // Reset audio in case it's not working
    audioPlayer.load();
    audioPlayer.currentTime = 0;
    
    audioPlayer.play()
        .then(() => console.log("✅ Playing audio..."))
        .catch(error => console.error("❌ Error playing preview:", error));
}


// 🚀 Step 11: Run Everything When the Page Loads
window.onload = async function () {
    await getSpotifyToken(); // Step 3: Get Spotify Token
    await fetchArtists(); // Step 5: Fetch Artists after getting token
};
