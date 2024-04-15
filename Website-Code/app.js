// Initialize the API Gateway client
var apigClient = apigClientFactory.newClient();

// Function to search photos using the SDK
function searchPhotos() {
  const query = document.getElementById('searchQuery').value;
  console.log(query);

  var paramInput = {
    "q" : query
  }
  
  
  // Use the SDK to make the search request
  apigClient
    .searchGet(paramInput, {}, {
        'Access-Control-Allow-Origin': '*'
    })
    .then(function(response) {
      // Process and display the results
      console.log(response)
      
      const resultsContainer = document.getElementById('searchResults');
      resultsContainer.innerHTML = ''; // Clear previous results
      const photos = response.data.result; // Adjust this if the structure is different
      photos.forEach(photo => {
        fetch(photo.url,{ mode: 'cors', method: "GET"})
        .then(response => {
          // Check if the request was successful
          if (!response.ok) {
              throw new Error('Network response was not ok ' + response.statusText);
          }
          console.log("Response Text")
          console.log(response);

          return response.text(); // or response.text() if the data is plain text
        })
        .then(data => {
          console.log("Data returned")
          console.log(data); // Handle the data from the response
          img.src = data;
        })
        .catch(error => {
          console.error('There was a problem with the fetch operation:', error);
        });

        const img = document.createElement('img');
        //img.src = photo.url; // Make sure 'url' is the correct key for the image URL
        img.alt = photo.labels[0];
        img.height = 300;
        img.title = photo.labels[0];
        resultsContainer.appendChild(img);
      });
    }).catch(function(error) {
      console.error('Search Error:', error);
    });
}

// Function to handle the photo upload
document.getElementById('uploadForm').addEventListener('submit', function(e) {
  e.preventDefault();

  const photoFile = document.getElementById('photoUpload').files[0];
  const customLabels = document.getElementById('customLabels').value;
  
  // Generate a unique filename, for example, using the current timestamp
  const filename = photoFile.name;

  var custom_param = {
    bucket: 'images-bucket-54015', 
    filename: filename,
    "x-amz-meta-customLabels": customLabels
  }
  
  // You need to read the file and convert it to a format suitable for the SDK
  const reader = new FileReader();
  reader.onload = function(event) {
    const photo = event.target.result; // This is a base64-encoded string of the file
    console.log(photo);
    // Use the SDK to upload the photo
    apigClient.uploadBucketFilenamePut(custom_param, photo, {
        'Access-Control-Allow-Origin': '*',
        "x-amz-meta-customLabels": customLabels
    })
    .then(function(response) {
      console.log('Upload Success:', response);
      // Handle successful upload here
    }).catch(function(error) {
      console.error('Upload Error:', error);
    });
  };
  
  // Read the photo file as a data URL (base64-encoded)
  reader.readAsDataURL(photoFile);
});
