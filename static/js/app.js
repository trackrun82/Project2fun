// Code for creating genre drop-down
d3.json("/api/v1.0/genre_names", function(data) {
    // form array of unique genres
    var genres = data.map(genres => genres.genre)
    var uniqueGenres = genres.filter((x, ind, arr) => arr.indexOf(x) === ind)
    
    // Append genres to dropdown
    uniqueGenres.forEach(function(genre) {
      var genreDropdown = d3.select("#selGenre").append("option");
      genreDropdown.text(genre);
    });
});

// Code for creating map
// Create the dark tile layer that will be the background of our map
const darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "dark-v10",
    accessToken: API_KEY
});

// Create the light tile layer
const lightmap = L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/light-v10',
    accessToken: API_KEY
});

// Initialize all of the LayerGroups we'll be using
const layers = {
    movies: new L.LayerGroup()
};

// Create the map object with options
const map = L.map("map", {
    center: [52.4912, -1.9348],
    zoom: 2,
    layers: [darkmap, layers.movies]
});

// Define a baseMaps object to hold our base layers
const baseMaps = {
    "Light Map": lightmap,
    "Dark Map": darkmap
};

// Create overlay object to hold our overlay layers
var overlayMaps = {
    "Movies": layers.movies
};

// Create a layer control and pass in our baseMaps and overlayMaps
// Add the layer control to the map
L.control.layers(baseMaps, overlayMaps, {
    collapsed: false
}).addTo(map);

// Create a new marker cluster group
const markers = L.markerClusterGroup();

// Grab the data with d3
d3.json("/api/v1.0/movies", function(data) {
    
    // Loop through data
    data.forEach(movie => {
        //Check for location
        if(movie.lat && movie.lng){
            const marker = L.marker([movie.lat, movie.lng])
            .bindPopup("<h3>" + movie.title + 
            "</h3><hr><p> Year Produced: " + movie.year +
            "</p><hr><p> Company: " + movie.company + 
            "</p><hr><p> Avg Votes: " + movie.avg_votes + "</p>");
            markers.addLayer(marker);
        }
    });

    // Add our marker cluster layer to the map
    markers.addTo(layers.movies);
});

// Function to handle changes in dropdown
function optionChanged(chosen){

    d3.json("/api/v1.0/genres", function(data){
        // Clear previous markers
        markers.clearLayers();
        
        // Get data for map based on selected genre
        const filteredGenre = data.filter(genres => genres.genre === chosen);
        console.log(filteredGenre)
    
        // Loop through data
        filteredGenre.forEach(movie => {
            //Check for location
            if(movie.lat && movie.lng){
                const marker = L.marker([movie.lat, movie.lng])
                .bindPopup("<h3>" + movie.title + 
                "</h3><hr><p> Year Produced: " + movie.year +
                "</p><hr><p> Company: " + movie.company + 
                "</p><hr><p> Avg Votes: " + movie.avg_votes + "</p>");
                markers.addLayer(marker);
            }
        });
        // Add our marker cluster layer to the map
        markers.addTo(layers.movies);
    });
  };
  
  // Add event listener for submit button
  d3.select('#submit').on('click', optionChanged);
