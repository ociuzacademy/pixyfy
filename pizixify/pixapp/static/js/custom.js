// Rotate the image (does not affect other images)
function editField(element, fieldType) {
    const originalText = element.innerText;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = originalText;
    element.innerHTML = '';
    element.appendChild(input);
    input.focus();

    input.addEventListener('blur', () => {
        element.innerHTML = originalText; // Revert if not saved
    });

    input.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            const newValue = input.value;
            // Save the new value via AJAX
            saveField(fieldType, newValue);
            element.innerHTML = newValue; // Update the displayed value
        }
    });
}

function saveAlbumTitle(newTitle, albumId) {
    fetch(`/update_custom_album_title/${albumId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // Ensure CSRF token is included
        },
        body: JSON.stringify({ title: newTitle })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Album title saved successfully:', data.title);
        } else {
            console.error('Error saving album title:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function saveAlbumDescription(newDescription, albumId) {
    fetch(`/update_custom_album_description/${albumId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // Ensure CSRF token is included
        },
        body: JSON.stringify({ description: newDescription })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Album description saved successfully:', data.description);
        } else {
            console.error('Error saving album description:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function savePageTitle(newTitle, page, albumId) {
    fetch(`/update_custom_page_title/${albumId}/${page}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // Ensure CSRF token is included
        },
        body: JSON.stringify({ title: newTitle })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Page title saved successfully:', data.title);
        } else {
            console.error('Error saving page title:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function savePageDescription(newDescription, page, albumId) {
    fetch(`/update_custom_page_description/${albumId}/${page}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() // Ensure CSRF token is included
        },
        body: JSON.stringify({ description: newDescription })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Page description saved successfully:', data.description);
        } else {
            console.error('Error saving page description:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getCsrfToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

// Handle click to show options
document.querySelectorAll('.grid-item .grid-photo').forEach(image => {
    image.addEventListener('click', function () {
        const imageActions = this.parentElement.querySelector('.image-actions');
        
        // Toggle the visibility of image-actions
        if (imageActions.classList.contains('active')) {
            imageActions.classList.remove('active'); // Hide options
        } else {
            // Hide all other actions before showing this one
            document.querySelectorAll('.grid-item .image-actions.active').forEach(activeAction => {
                activeAction.classList.remove('active');
            });
            imageActions.classList.add('active'); // Show options
        }
    });
});

// Optional: Click outside the image to close all options
document.addEventListener('click', function (e) {
    if (!e.target.closest('.grid-item')) {
        document.querySelectorAll('.grid-item .image-actions.active').forEach(activeAction => {
            activeAction.classList.remove('active');
        });
    }
});


let draggedItem = null;

function initializeDragAndDrop() {
    const gridItems = document.querySelectorAll('.grid-item');
    gridItems.forEach(item => {
        item.addEventListener('dragstart', dragStart);
        item.addEventListener('dragover', dragOver);
        item.addEventListener('drop', drop);
        item.addEventListener('dragend', dragEnd); // Add dragend event
    });
}

function dragStart(event) {
    draggedItem = event.target.closest('.grid-item'); // Ensure we get the closest grid item
    event.dataTransfer.setData("text", draggedItem.id);  // Store the dragged item's ID
    draggedItem.classList.add("dragging"); // Add dragging class for visual feedback
}

function dragEnd(event) {
    if (draggedItem) {
        draggedItem.classList.remove("dragging"); // Remove the visual feedback class
    }
    draggedItem = null; // Clear draggedItem
}

function dragOver(event) {
    event.preventDefault(); // Necessary for drop to work
}

function drop(event) {
    event.preventDefault();
    const droppedItem = event.target.closest('.grid-item'); // Ensure we get the closest grid item
    
    // Log the dropped item and dragged item
    console.log("Dropped Item:", droppedItem);
    console.log("Dragged Item:", draggedItem);

    // Check if the dropped item is valid and not the same as the dragged item
    if (!droppedItem || draggedItem === droppedItem) return;

    // Log the parent nodes for debugging
    console.log("Parent of Dropped Item:", droppedItem.parentNode);
    console.log("Parent of Dragged Item:", draggedItem.parentNode);

    // Swap the items in the DOM
    swapItems(draggedItem, droppedItem);

    // Update the order on the server
    updateImageOrder();
}

function swapItems(item1, item2) {
    const parent = item1.parentNode;

    // Check if both items are still in the same parent
    if (parent !== item2.parentNode) {
        console.error("Items are not in the same parent.");
        return;
    }

    // Create a temporary placeholder to facilitate the swap
    const tempPlaceholder = document.createElement('div');

    // Insert the placeholder before item1
    parent.insertBefore(tempPlaceholder, item1);
 
    // Move item2 before item1
    parent.insertBefore(item2, item1);

    // Move item1 after the placeholder
    parent.insertBefore(item1, tempPlaceholder);

    // Remove the placeholder
    parent.removeChild(tempPlaceholder);
}

function updateImageOrder() {
    const order = [];
    
    // Get the new order of photos after the swap
    document.querySelectorAll('.grid-item').forEach((item, index) => {
        const photoId = item.dataset.photoId; // Get the photo ID from data attribute
        if (photoId) {
            order.push({
                photoId: photoId,
                order: index // The new order is the index of the item in the grid
            });
        }
    });

    // Send the updated order to the server via AJAX
    fetch('/update-custom-photo-order/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Ensure you include CSRF token for security
        },
        body: JSON.stringify({
            'order': order, // Send the updated order of photo IDs and their new position
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Photo order updated!");
        } else {
            alert("Error updating photo order.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize the drag-and-drop functionality after the page is loaded
initializeDragAndDrop();


// Call this function after the grid is created or modified
// initializeDragAndDrop();

let isResizing = false;
let currentHandle;
let currentPhotoId;

function initResize(event, handle, photoId) {
    isResizing = true;
    currentHandle = handle;
    currentPhotoId = photoId;

    // Prevent text selection
    event.preventDefault();

    // Add mousemove and mouseup event listeners
    window.addEventListener('mousemove', resize);
    window.addEventListener('mouseup', stopResize);
}

function resize(event) {
    if (!isResizing) return;

    const photoElement = document.getElementById(`photo-${currentPhotoId}`);
    const img = photoElement.querySelector('.grid-photo');

    const rect = photoElement.getBoundingClientRect();
    let newWidth = rect.width;
    let newHeight = rect.height;

    if (currentHandle.includes('right')) {
        newWidth = event.clientX - rect.left;
    }
    if (currentHandle.includes('bottom')) {
        newHeight = event.clientY - rect.top;
    }
    if (currentHandle.includes('left')) {
        newWidth = rect.right - event.clientX;
        photoElement.style.left = `${event.clientX}px`;
    }
    if (currentHandle.includes('top')) {
        newHeight = rect.bottom - event.clientY;
        photoElement.style.top = `${event.clientY}px`;
    }

    // Set the new dimensions
    photoElement.style.width = `${newWidth}px`;
    photoElement.style.height = `${newHeight}px`;
    img.style.width = '100%'; // Ensure the image fills the resized container
    img.style.height = '100%'; // Ensure the image fills the resized container
}

function stopResize() {
    isResizing = false;
    window.removeEventListener('mousemove', resize);
    window.removeEventListener('mouseup', stopResize);
}

let currentRotation = 0;

function rotateeditedImage(imageId) {
    const image = document.getElementById(imageId);
    currentRotation += 90; // Rotate by 90 degrees
    image.style.transform = `rotate(${currentRotation}deg)`;
}

function saveImage(photoId) {
    const photoElement = document.getElementById(`photo-${photoId}`);
    const img = photoElement.querySelector('.grid-photo');
    const width = photoElement.offsetWidth;
    const height = photoElement.offsetHeight;

    // Create a canvas to save the image
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = width;
    canvas.height = height;

    // Save the current rotation state
    const rotationInDegrees = currentRotation % 360; // Ensure rotation is within 0-359 degrees
    const rotationInRadians = rotationInDegrees * (Math.PI / 180); // Convert to radians

    // Translate to the center of the canvas
    context.translate(canvas.width / 2, canvas.height / 2);
    // Rotate the canvas
    context.rotate(rotationInRadians);
    // Draw the image on the canvas, adjusting for the rotation
    context.drawImage(img, -width / 2, -height / 2, width, height);

    // Get base64-encoded image data
    const imageData = canvas.toDataURL('image/jpeg');

    // Send data to the server
    fetch(`/save-edited-album-image/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            photo_id: photoId,
            image_data: imageData,
            width: width,
            height: height // Send the new dimensions
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Image saved successfully!');
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}



function toggleView() {
    const albumContainer = document.getElementById('album-container');
    albumContainer.classList.toggle('portrait');

    const button = document.getElementById('toggleViewButton');
    if (albumContainer.classList.contains('portrait')) {
        button.textContent = 'Switch to Landscape View';
    } else {
        button.textContent = 'Switch to Portrait View';
    }
}