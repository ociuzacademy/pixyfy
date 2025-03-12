$(document).ready(function() {
    $(".draggable-image").on("dragstart", function(event) {
      event.originalEvent.dataTransfer.setData("text", event.target.src);  // Store the dragged image source
    });
  
    $(".drop-zone").on("dragover", function(event) {
      event.preventDefault();  // Allow the drop
    });
  
    $(".drop-zone").on("drop", function(event) {
      event.preventDefault();
      
      var imgSrc = event.originalEvent.dataTransfer.getData("text");  // Get the image source
  
      // Ensure that we are only removing the dragged image and not other grid items
      $(this).find(".grid-item").each(function() {
        // Check if this item is not the one being dropped (to avoid removing the dragged image)
        if (!$(this).is(draggedItem)) {
          $(this).remove();  // Remove other grid items
        }
      });
      
      // Add the dragged image to the drop zone
      var newImage = $("<img>").attr("src", imgSrc);
      $(this).append(newImage);
    });
  });
  
  let draggedItem = null;
  
  function dragStart(event) {
      draggedItem = event.target;
      event.dataTransfer.setData("text", event.target.id);
  }
  
  function dragOver(event) {
      event.preventDefault(); // Necessary for drop to work
  }
  
  function drop(event) {
      event.preventDefault();
      const droppedItem = event.target.closest('.grid-item'); // Ensure the target is a grid-item
      if (draggedItem !== droppedItem) {
          // Swap the items
          swapItems(draggedItem, droppedItem);
          // Update the order on the server
          updateImageOrder();
      }
  }
  
  function swapItems(item1, item2) {
      const parent = item1.parentNode;
      const nextSibling = item2.nextSibling;
      parent.insertBefore(item2, item1);
      parent.insertBefore(item1, nextSibling);
  }
  
  function updateImageOrder() {
      const order = [];
      document.querySelectorAll('.grid-item').forEach((item, index) => {
          order.push(item.dataset.photoId);  // Get the photo ID from data attribute
      });
  
      // Send new order to server via AJAX
      fetch('/update-photo-order/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')  // Ensure you include CSRF token
          },
          body: JSON.stringify({
              'order': order,  // Send the new order of photo IDs
          })
      }).then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Photo order updated!");
            } else {
                alert("Error updating photo order.");
            }
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
  