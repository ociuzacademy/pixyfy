from django.db import models

# Create your models here.
class tbl_register(models.Model):
    name=models.CharField(max_length=100,default=True)
    email=models.CharField(max_length=100,unique=True)
    pswd=models.CharField(max_length=100)
    utype=models.CharField(max_length=100,default="")
    
class tbl_photogra_register(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,unique=True)
    pswd = models.CharField(max_length=100)
    image = models.ImageField(upload_to='photographer_images/', blank=True, null=True)  
    place = models.CharField(max_length=100, blank=True, null=True)  
    address = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name
    
from django.db import models

class PhotoFolder(models.Model):
    folder_id = models.CharField(max_length=100)
    password = models.CharField(max_length=100, unique=True)  # Ensure the password is unique
    created_by = models.ForeignKey('tbl_photogra_register', on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.folder_id} ({self.created_by.name})"

import uuid
from django.db import models
from django.utils import timezone

class Album(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(tbl_photogra_register, on_delete=models.CASCADE)
    folder = models.ForeignKey(PhotoFolder, on_delete=models.CASCADE)
    total_pages = models.PositiveIntegerField(default=1)
    photos_per_page = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    photo_ids = models.TextField(blank=True)
    share_link = models.CharField(max_length=255, blank=True, null=True)

    
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()  # Ensure created_at is set if it's None
        if not self.share_link:
        # Generate a unique share link using the album's creation time and a random UUID
            unique_string = str(self.created_at.timestamp()) + str(uuid.uuid4())
            self.share_link = uuid.uuid5(uuid.NAMESPACE_DNS, unique_string).hex
        super(Album, self).save(*args, **kwargs)


    def __str__(self):
        return self.title


class Photo(models.Model):
    folder = models.ForeignKey(PhotoFolder, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='folder_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(tbl_register, related_name='liked_photos', blank=True)
    order = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    edited_image = models.ImageField(upload_to='edited_photos/', null=True, blank=True)  # Add this field to mark if the image is edited

    def __str__(self):
        return f"Photo in {self.folder.folder_id}"

# Model for Client Album
class ClientAlbum(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name="client_albums")
    total_pages = models.IntegerField()
    photos_per_page = models.JSONField()  # Stores the number of photos per page in JSON format
    page_titles = models.JSONField(blank=True, null=True)  # Optional page titles
    page_descriptions = models.JSONField(blank=True, null=True)  # Optional page descriptions
    created_at = models.DateTimeField(auto_now_add=True)
    photos = models.ManyToManyField(Photo, related_name='client_albums')

    def __str__(self):
        return self.title

    


from django.db import models
from .models import tbl_register  # Import user model
from django.db import models
from .models import tbl_register  # Import user model

class ClientPhoto(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE)  # User who uploaded the photo
    image = models.ImageField(upload_to='client_photos/')  # Store images in 'media/client_photos/'
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when photo was uploaded
    is_edited = models.BooleanField(default=False)  # Track if the photo has been edited
    edited_image = models.ImageField(upload_to='client_photos/edited/', blank=True, null=True)  # Store edited image
    order = models.PositiveIntegerField(default=0)  # Order for arranging photos

    def __str__(self):
        return f"Photo by {self.user.name} - {self.uploaded_at}"

class CustomAlbum(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='custom_albums')
    created_at = models.DateTimeField(auto_now_add=True)
    photos = models.ManyToManyField(ClientPhoto, related_name='custom_albums')
    total_pages = models.IntegerField()
    photos_per_page = models.JSONField()  # Storing total number of pages
    page_titles = models.JSONField(blank=True, null=True)  # Titles for pages
    page_descriptions = models.JSONField(blank=True, null=True)  # Descriptions for pages

    def __str__(self):
        return self.title
