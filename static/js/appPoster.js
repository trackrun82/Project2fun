const imageContainer = document.getElementById('image-container');
const loader = document.getElementById('loader');

let ready = false;
let imagesLoaded = 0;
let totalImages = 0;
let photosArray = [];

// Count
const count = 30;
// const apiKey = 'YOUR_API_KEY_HERE';
const apiUrl = `/api/v1.0/profit_movies`;

// Check if all images were loaded
function imageLoaded() {
  imagesLoaded++;
  if (imagesLoaded === totalImages) {
    ready = true;
    loader.hidden = true;
  }
}

// Helper Function to Set Attributes on DOM Elements
function setAttributes(element, attributes) {
  for (const key in attributes) {
    element.setAttribute(key, attributes[key]);
  }
}

// Create Elements For Links & Photos, Add to DOM
function displayPhotos(displayData) {
    imagesLoaded = 0;
    totalImages = displayData.length;

    // console.log(`totalImages`);
    // console.log(totalImages);
    // console.log(`displayData`);
    // console.log(displayData);

    // The currency formatter
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
      });

    // Run function for each object in photosArray
    displayData.forEach((photo) => {

        // Formatting the monies
        theProfit = formatter.format(photo.profit);
        theBudget = formatter.format(photo.budget);
        
        // Create <div> with class = "img-container"
        const imageDiv = document.createElement('div');
        setAttributes(imageDiv, {
            class: 'img-container',
        });

        // Create text block for image
        const textBlockDiv = document.createElement('div');
        setAttributes(textBlockDiv, {
            class: 'text-block',
        });
        const para = document.createElement("P");
        para.innerHTML = `Year: ${photo.year_pub}<br>Profit: ${theProfit}<br>Budget: ${theBudget}<br>Duration: ${photo.duration}`;
        textBlockDiv.appendChild(para);

        // Description block
        const descriptionBlockDiv = document.createElement('div');
        setAttributes(descriptionBlockDiv, {
            class: 'description-block lead',
        });
        const paraDescription = document.createElement("P");
        paraDescription.innerHTML = photo.description;
        descriptionBlockDiv.appendChild(paraDescription);

        // Create <a> to link to full photo
        const href_url = `https://www.imdb.com/title/${photo.movie_id}/`;
        const aTag = document.createElement('a');
        setAttributes(aTag, {
            href: href_url,
            target: '_blank',
        });

        // Create <img> for photo
        const img = document.createElement('img');
        setAttributes(img, {
            src: photo.poster_url,
            alt: photo.title,
            title: photo.title,
        });

        // Event Listener, check when each is finished loading
        img.addEventListener('load', imageLoaded);

        // Put <img> inside aTag, then put both inside imageContainer
        aTag.appendChild(img);

        // Put <img> and textBlockDiv inside imageDiv
        imageDiv.appendChild(aTag);
        imageDiv.appendChild(textBlockDiv);
        imageDiv.appendChild(descriptionBlockDiv);

        // Then put imageDiv inside imageContainer
        imageContainer.appendChild(imageDiv);
    });
}

// =================================================================
//       Set up the HTML dropdown QUERY SECTION dynamically
// =================================================================
function optionsHTML(theChoice, choiceArray) {
  d3.select("form").selectAll("div").remove();
  let div = d3.select("form").append("div");
  let theLabel = div.append("label")
                    .attr("for", "select"+theChoice)
                    .text(`Select ${theChoice}`);
  let select = div.append("select")
                  .attr("id", "select"+theChoice)
                  .attr("name", theChoice);
  select.selectAll("option")
        .data(choiceArray)
        .enter()
        .append("option")
        .attr("value", d => d)
        .text(d => d);
  let defaultEmpty = select.append("option")
                          .attr("value", "")
                          .text("")
                          .attr("selected", "selected");
};


function movieDataYear(theYear, theKeysArray, nested_data) {
  console.log(`Data for ${theYear}`);
  targeted_data = nested_data[theKeysArray.indexOf(theYear)].values;
  
  console.log(targeted_data);

  return targeted_data;
};

// Get photos from Heroku Database
async function getPhotos() {
  try {
        const response = await fetch(apiUrl);
        const myData = await response.json();
        const myData_sorted = myData.sort((a,b) => b.profit - a.profit);
        // Choose first 300.
        photosArray = myData_sorted.slice(0, 300);
        
        displayPhotos(photosArray);

        // Using d3.nest()
        var nested_data_year = d3.nest()
                .key(d => d.year_pub).sortKeys(d3.ascending)
                .entries(myData_sorted);

        // console.log("nested_data_year");
        // console.log(nested_data_year);

        theKeysYear = nested_data_year.map(d => d.key);

        // Create the DropDown for year.
        optionsHTML("Year", theKeysYear);

        // Select the button
        var button = d3.select("#filter-btn");

        // Select the form
        var form = d3.select("form");

        // Create event handlers for clicking the button or pressing the enter key
        button.on("click", runEnter);
        form.on("submit",runEnter);

        // Create the function to run for both events
        function runEnter() {
        // Prevent the page from refreshing
        d3.event.preventDefault();

        // Select the input elements and get the raw HTML node
        let inputYear = d3.select("#selectYear");

        // Get the value property of the input elements
        let inputValueYear = inputYear.property("value");

        // Print the selected input values to the console
        console.log(`The query Year: ${inputValueYear}`);

        // Get the data for the selected year.
        let selectedData = movieDataYear(inputValueYear, theKeysYear, nested_data_year);
        console.log("selectedData");
        console.log(selectedData);

        // Remove all previous images
        d3.select("#image-container").selectAll('div').remove();

        // render the photos
        displayPhotos(selectedData);
        };

    } catch (error) {
            // Catch error
            console.log(`There is an error.`);
            console.log(error);
        };
}

// Check to see if scrolling near bottom of page, Load More Photos
window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000 && ready) {
    ready = false;
    getPhotos();

    console.log('Loading more posters')
  }
});

// On Load
getPhotos();