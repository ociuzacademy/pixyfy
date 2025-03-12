from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,reverse,HttpResponseRedirect
from.models import*
from django.http import HttpResponse

from collections import defaultdict
# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "POST":
        pswd = request.POST['pswd']
        email = request.POST['email']
        var = tbl_register.objects.filter(pswd=pswd, email=email, utype="user")
        var2=tbl_photogra_register.objects.filter(email=email,pswd=pswd)
        if var:
            for x in var:
             request.session['id'] = x.id
            return render(request,'client/client_index.html')  
        if var2:
            for x in var2:
                request.session['id']=x.id
            return render(request,"photographer/photogra_index.html")
        else:
            txt = """<script>alert("Invalid user Credentials....");window.location='/';</script>"""
            return HttpResponse(txt) 
    else:
        return render(request, "login.html")
    

def logout(request):
    if request.session.has_key('id'):
        del request.session['id']
        logout(request)
    return render(request,'index.html')

                                              #---------photographer--------#

def photogra_index(request):
    folders = PhotoFolder.objects.all()
    return render(request,'photographer/photogra_index.html')





def photogra_register(request):
    error_message = None
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        confirm_pswd = request.POST.get('cpswd')  # Use 'cpswd' to match your form field name

        # Check if passwords match
        if pswd != confirm_pswd:
            error_message = "Passwords do not match."
        elif tbl_photogra_register.objects.filter(email=email).exists():
            error_message = "Email already exists."
        else:
            # Save the new photographer with the provided name, email, and password
            tbl_photogra_register.objects.create(name=name, email=email, pswd=pswd)
            return redirect('/login/')
    
    return render(request, 'photogra_register.html', {'error_message': error_message})

def photogra_profile(request):
    if 'id' not in request.session:
        return redirect('/login/')  # Ensure user is logged in
    
    id = request.session['id']  # Get the logged-in user's ID
    photographer = tbl_photogra_register.objects.get(id=id)  # Fetch the photographer's details

    if request.method == 'POST':
        # Update the fields with the submitted data
        photographer.name = request.POST.get('name')
        photographer.place = request.POST.get('place')  # Ensure this matches the form input name
        photographer.address = request.POST.get('address')

        # If a new image is uploaded, save it
        if request.FILES.get('image'):
            photographer.image = request.FILES['image']

        # Save the updated data
        photographer.save()
        return redirect('/photogra_profile/')  # Redirect to the profile page or a success page

    # Render the profile with the existing data
    return render(request, 'photographer/photogra_profile.html', {'data': photographer})

def photogra_edit_profile(request):
    if 'id' not in request.session:
        return redirect('/login/')  # Ensure user is logged in

    id = request.session['id']
    photographer = tbl_photogra_register.objects.get(id=id)  
    
    if request.method == 'POST':     
        photographer.name = request.POST.get('name')
        photographer.email = request.POST.get('email')  
        
        # Handle password update only if provided
        pswd = request.POST.get('pswd')
        if pswd:  
            photographer.pswd = pswd  
        
        photographer.place = request.POST.get('place')  # Ensure this matches the form input name
        photographer.address = request.POST.get('address')

        # If a new image is uploaded, save it
        if request.FILES.get('image'):
            photographer.image = request.FILES['image']

        # Save the updated data
        photographer.save()

        # Optionally print to check the updated values
        print(f"Updated Place: {photographer.place}")

        return redirect('photogra_profile')       
    return render(request, 'photographer/photogra_edit_profile.html', {'data': photographer})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import PhotoFolder, tbl_photogra_register

def create_folder(request):
    if request.method == "POST":
        folder_id = request.POST.get('folder_id')
        password = request.POST.get('password')
        photographer = tbl_photogra_register.objects.get(id=request.session['id'])

        
        try:
            PhotoFolder.objects.create(folder_id=folder_id, password=password, created_by=photographer)
            messages.success(request, "Folder created successfully!")
            return redirect('create_folder')
        except IntegrityError:
            messages.error(request, "The password you entered is already in use. Please choose a different password.")
    return render(request, 'photographer/create_folder.html')


def folder_list(request):
    created_by = tbl_photogra_register.objects.get(id=request.session['id'])
    folders = PhotoFolder.objects.filter(created_by=created_by)
    return render(request, 'photographer/folder_list.html', {'folders': folders})


def add_photos(request, id):
    # Get the folder by ID or return a 404 if it doesn't exist
    folder = get_object_or_404(PhotoFolder, id=id)

    # Fetch unedited photos (sorted by upload date)
    photos = folder.photos.filter(is_edited=False).order_by('uploaded_at')

    if request.method == 'POST':
        # Check if photos are part of the request
        if 'photos' in request.FILES:
            photo_files = request.FILES.getlist('photos')
            for photo_file in photo_files:
                # Set order for the new photo
                order = folder.photos.count() + 1
                Photo.objects.create(folder=folder, image=photo_file, order=order)

            messages.success(request, "Photos uploaded successfully!")
            return redirect('add_photos', id=id)  # Redirect to show uploaded photos

    return render(request, 'photographer/add_photos.html', {
        'folder': folder,
        'photos': photos  # Pass unedited photos to the template
    })

from django.shortcuts import render, get_object_or_404
from .models import PhotoFolder, Photo

def access_folder(request, folder_id):
    folder = get_object_or_404(PhotoFolder, id=folder_id)

    # Fetch all unedited photos associated with the folder (if you want to exclude edited ones)
    photos = folder.photos.filter(is_edited=False).order_by('uploaded_at')

    if request.method == 'POST' and request.FILES.get('photo'):
        # Handling photo upload
        new_photo = Photo(folder=folder, image=request.FILES['photo'])
        new_photo.save()

        # Optionally, add a success message or redirect
        return render(request, 'photographer/add_photos.html', {
            'folder': folder,
            'photos': photos,  # Refresh photo list
            'message': 'Photo uploaded successfully!'
        })

    # Pass the folder and its photos to the template
    return render(request, 'photographer/add_photos.html', {
        'folder': folder,
        'photos': photos  # Ensure previously uploaded photos are passed to the template
    })

from django.shortcuts import get_object_or_404, redirect
from .models import Photo

def delete_photo(request, photo_id):
    # Get the photo object to delete
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Delete the photo
    photo.delete()
    
    # Redirect to the page where the photos are displayed (e.g., add_photos view)
    return redirect('add_photos', id=photo.folder.id)


import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import PhotoFolder, Photo, Album
from .models import tbl_photogra_register

def create_album(request):
    # Fetch photographer's ID from the session
    photographer_id = request.session.get('id')
    if not photographer_id:
        return redirect('login')  # Redirect to login if photographer is not found in the session

    # Get photographer object using the ID stored in the session
    photographer = get_object_or_404(tbl_photogra_register, id=photographer_id)

    # Fetch folders created by the photographer
    folders = PhotoFolder.objects.filter(created_by_id=photographer_id)

    if request.method == 'POST':
        # Get form data
        title = request.POST['title']
        total_pages = int(request.POST['total_pages'])

        # Create a dictionary for the photos per page
        photos_per_page = {}
        for i in range(total_pages):
            photos_per_page[i + 1] = int(request.POST[f'photos_page_{i}'])

        # Get the selected photos from the POST request
        selected_photos = request.POST.getlist('photos')
        photo_ids = ','.join(selected_photos)  # Store photo IDs as a comma-separated string

        # Retrieve the folder ID from the POST request and get the corresponding folder object
        folder_id = request.POST.get('folder_id')
        folder = get_object_or_404(PhotoFolder, id=folder_id)

        # Create the album
        album = Album.objects.create(
            title=title,
            total_pages=total_pages,
            photos_per_page=json.dumps(photos_per_page),  # Store the photos per page as JSON
            created_by=photographer,
            photo_ids=photo_ids,
            folder=folder  # Set the folder for the album
        )

        return redirect('album_detail', album_id=album.id)  # Redirect to album detail page

    # Handle folder selection for GET requests
    selected_folder_id = request.GET.get('folder_id')
    selected_folder = None
    photos = []

    if selected_folder_id:
        selected_folder = get_object_or_404(PhotoFolder, id=selected_folder_id)
        # Fetch only photos that have been liked by at least one client
        photos = Photo.objects.filter(
            folder=selected_folder,
            folder__created_by=photographer,
            is_edited=False,  # Exclude edited photos
            likes__isnull=False  # Include only photos that have been liked
        ).distinct()

    # Render the create album page
    return render(request, 'photographer/create_album.html', {
        'folders': folders,
        'selected_folder': selected_folder,
        'photos': photos,
    })



from django.shortcuts import render, get_object_or_404
from .models import Album, Photo
def album_detail(request, album_id):
    # Get the album object
    album = get_object_or_404(Album, id=album_id)
    
    # Get the photo IDs for the album
    photo_ids = album.photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_ids)

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the album detail page with the photos
    return render(request, 'photographer/album_detail.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })


from weasyprint import HTML
from django.template.loader import render_to_string

def album_detail_pdf(request, album_id):
    # Get the album object
    album = get_object_or_404(Album, id=album_id)
    
    # Get the photo IDs for the album
    photo_ids = album.photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_ids)

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template
    html_string = render_to_string('photographer/album_detail_pdf.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response



from django.shortcuts import render
def view_created_albums(request):
    photographer_id = request.session.get('id')  # Assuming photographer ID is stored in session
    albums = Album.objects.filter(created_by_id=photographer_id)  # Filter albums by the logged-in photographer
    return render(request, 'photographer/view_created_albums.html', {'albums': albums})
    

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PhotoFolder

def delete_folder(request):
    if request.method == 'POST':
        # Retrieve the password from the form
        password = request.POST.get('password')

        # Ensure that the session contains the user ID
        user_id = request.session.get('id')
        if not user_id:
            messages.error(request, "You are not logged in.")
            return redirect('login')  # Redirect to login if the user is not authenticated

        # Try to get the folder with the provided password and user ID
        folder = get_object_or_404(PhotoFolder, password=password, created_by_id=user_id)

        # Delete the folder if found
        folder.delete()
        messages.success(request, 'Folder deleted successfully.')

        return redirect('folder_list')  # Redirect to the list of folders

    # If the request method is GET, you can render a confirmation page or provide other functionality
    return redirect('folder_list')  # If GET request, redirect to folder list page
from django.shortcuts import render, redirect, get_object_or_404
from .models import Album

def delete_album(request, album_id):
    # Check if the photographer ID is available in the session
    photographer_id = request.session.get('id')  # Changed to 'id' as per your login view
    if photographer_id is None:
        # Redirect to a login or error page if the photographer ID is not in the session
        return redirect('login')  # Replace with the appropriate URL

    # Get the album to be deleted
    album = get_object_or_404(Album, id=album_id)
    
    # Check if the current user is the creator of the album by matching the photographer's ID
    if album.created_by.id == photographer_id:
        album.delete()  # Delete the album

    return redirect('view_created_albums')  # Redirect to the page that lists albums, or the appropriate page





#-----Client-------#

def client_index(request):
    return render(request,'client/client_index.html')


def client_register(request):
    error_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        
        # Check if the email already exists
        if tbl_register.objects.filter(email=email) or tbl_photogra_register.objects.filter(email=email).exists():
            error_message = "Email already exists."
        else:
            # Save the new user to the database
            tbl_register(name=name, email=email, pswd=pswd, utype='user').save()
            return redirect('/login/')  # Redirect to the login page after successful registration

    return render(request, 'client_register.html', {'error_message': error_message})
from django.shortcuts import render, get_object_or_404, redirect
from .models import PhotoFolder

def client_view_folder(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        try:
            # Find folder using the password
            folder = PhotoFolder.objects.get(password=password)

            # Store the folder ID in the session to allow access
            request.session['folder_password_verified'] = True
            request.session['verified_folder_id'] = folder.id

            # Access the photos using the related name 'photos'
            photos = folder.photos.all()

            return render(request, 'client/client_view_folder.html', {
                'photos': photos,
                'folder': folder,
            })

        except PhotoFolder.DoesNotExist:
            # If folder not found, show an error message and stay on the password page
            return render(request, 'client/client_index.html', {
                'error_message': "Incorrect password. Please try again."
            })

    # If the password has already been verified
    elif request.session.get('folder_password_verified'):
        folder_id = request.session.get('verified_folder_id')
        folder = get_object_or_404(PhotoFolder, id=folder_id)

        # Access the photos through the related name 'photos'
        photos = folder.photos.all()

        return render(request, 'client/client_view_folder.html', {
            'photos': photos,
            'folder': folder,
        })

    # If no folder verification, redirect to index or password entry page
    return redirect('client_index')

def like_photo(request, photo_id):
    user_id = request.session.get('id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))  # Redirect to login if not logged in

    try:
        user = tbl_register.objects.get(id=user_id)
    except tbl_register.DoesNotExist:
        return HttpResponseRedirect(reverse('login'))  # Redirect if user no longer exists

    photo = get_object_or_404(Photo, id=photo_id)
    if user in photo.likes.all():
        photo.likes.remove(user)  # Remove like
    else:
        photo.likes.add(user)  # Add like

    folder = photo.folder
    photos = Photo.objects.filter(folder=folder)

    return render(request, 'client/client_view_folder.html', {
        'folder': folder,
        'photos': photos,
        'user': user
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClientAlbum, Photo
import json
def client_create_album(request):
    # Check if the folder is verified
    if not request.session.get('folder_password_verified'):
        return redirect('client_index')  # Redirect to index if no folder is verified

    # Retrieve the verified folder ID
    folder_id = request.session.get('verified_folder_id')
    folder = get_object_or_404(PhotoFolder, id=folder_id)

    # Fetch liked photos for the specific folder
    user_id = request.session.get('id')  # Assuming session stores client ID
    if not user_id:
        return redirect('login')  # Redirect to login if the user is not logged in

    user = get_object_or_404(tbl_register, id=user_id)
    liked_photos = folder.photos.filter(likes=user)  # Filter liked photos for this user in the folder

    if request.method == 'POST':
        # Get album details from the form
        title = request.POST['title']
        description = request.POST.get('description', '')
        total_pages = int(request.POST['total_pages'])

        # Prepare dictionaries for photos, titles, and descriptions per page
        photos_per_page = {}
        page_titles = {}
        page_descriptions = {}

        for i in range(1, total_pages + 1):
            photos_per_page[i] = int(request.POST.get(f'photos_page_{i}', 0))
            page_titles[i] = request.POST.get(f'page_title_{i}', '').strip()
            page_descriptions[i] = request.POST.get(f'page_desc_{i}', '').strip()

        # Fetch selected photos
        selected_photos = request.POST.get('selected_photos', '').split(',')
        if not selected_photos:
            messages.error(request, "Please select at least one photo.")
            return render(request, 'client/client_create_album.html', {
                'liked_photos': liked_photos,
                'error': "Please select at least one photo."
            })

        # Create the album
        album = ClientAlbum.objects.create(
            title=title,
            description=description,
            created_by=user,
            total_pages=total_pages,
            photos_per_page=json.dumps(photos_per_page),
            page_titles=json.dumps(page_titles),
            page_descriptions=json.dumps(page_descriptions),
        )

        # Add the selected photos to the album
        for photo_id in selected_photos:
            if photo_id:
                photo = Photo.objects.get(id=photo_id)
                album.photos.add(photo)

        messages.success(request, f"Album '{title}' created successfully!")
        return redirect('client_album', album_id=album.id)

    return render(request, 'client/client_create_album.html', {
        'liked_photos': liked_photos,
    })

import json
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render
from .models import ClientAlbum, tbl_register

def client_albums_view(request):
    # Get the client ID from the session
    client_id = request.session.get('id')
    
    # Check if the session contains a valid client ID
    if client_id:
        # Fetch the client record
        client = tbl_register.objects.filter(id=client_id).first()
        if client:
            # Fetch albums created by this client
            client_albums = ClientAlbum.objects.filter(created_by=client)
            return render(request, 'client/client_albums.html', {'client_albums': client_albums})
    
    # If no valid session or client found, redirect to login or show an error
    return render(request, 'login.html', {"error": "Please log in to view your albums."})



import base64
import json
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Photo
@csrf_exempt
def save_edited_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            image_data = data.get('image_data')
            width = data.get('width')  # Get the new width
            height = data.get('height')  # Get the new height

            if not photo_id or not image_data:
                return JsonResponse({'success': False, 'message': 'Invalid data'})

            # Decode the image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            decoded_img = ContentFile(base64.b64decode(imgstr), name=f"edited_photo_{photo_id}.{ext}")

            # Retrieve the original photo
            original_photo = Photo.objects.get(id=photo_id)

            # Save the new edited photo
            edited_photo = Photo.objects.create(
                folder=original_photo.folder,
                image=decoded_img,
                order=original_photo.order,
                is_edited=True
            )

            # Update the original photo to reference the edited image
            original_photo.edited_image = edited_photo.image
            original_photo.is_edited = True
            original_photo.save()

            return JsonResponse({'success': True, 'new_photo_id': edited_photo.id, 'width': width, 'height': height})
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Photo not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
from django.shortcuts import get_object_or_404, render
import json

from django.shortcuts import render, get_object_or_404
from .models import ClientAlbum, Photo
import json

def client_album(request, album_id):
    # Fetch the album
    album = get_object_or_404(ClientAlbum, id=album_id)

    # Retrieve all photos associated with the album
    photos = album.photos.all().order_by('order')

    # Get the current page number from the request (default to 1)
    current_page = int(request.GET.get('page', 1))

    # Parse photos_per_page field
    if isinstance(album.photos_per_page, str):
        try:
            photos_per_page_dict = json.loads(album.photos_per_page)
        except json.JSONDecodeError:
            photos_per_page_dict = {}
    else:
        photos_per_page_dict = album.photos_per_page or {}

    # Parse page titles and descriptions
    if isinstance(album.page_titles, str):
        page_titles = json.loads(album.page_titles) or {}
    else:
        page_titles = album.page_titles or {}

    if isinstance(album.page_descriptions, str):
        page_descriptions = json.loads(album.page_descriptions) or {}
    else:
        page_descriptions = album.page_descriptions or {}

    # Combine titles and descriptions into a single dictionary
    page_info = {
        str(page): {
            'title': page_titles.get(str(page), '').strip(),
            'description': page_descriptions.get(str(page), '').strip(),
        }
        for page in range(1, album.total_pages + 1)
    }

    # Get the number of photos for the current page
    photos_per_page = photos_per_page_dict.get(str(current_page), 0)

    # Calculate the start and end indices for the current page
    start_index = sum(photos_per_page_dict.get(str(i), 0) for i in range(1, current_page))
    end_index = start_index + photos_per_page

    # Get the photos for the current page
    current_page_photos = photos[start_index:end_index]

    # Prepare current page photos with absolute URLs
    current_page_photos = [
        {
            'id': photo.id,
            'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url),
        }
        for photo in current_page_photos
    ]

    # Organize photos by pages for template use
    photos_by_page = {}
    for page in range(1, len(photos_per_page_dict) + 1):
        page_photos_per_page = photos_per_page_dict.get(str(page), 0)
        start_idx = sum(photos_per_page_dict.get(str(i), 0) for i in range(1, page))
        end_idx = start_idx + page_photos_per_page
        photos_by_page[page] = [
            {
                'id': photo.id,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url),
            }
            for photo in photos[start_idx:end_idx]
        ]

    # Calculate total pages
    total_pages = len(photos_per_page_dict)

    # Pagination links list
    total_pages_list = list(range(1, total_pages + 1))

    # Context for rendering the template
    context = {
        'album': album,
        'current_page_photos': current_page_photos,
        'photos_by_page': photos_by_page,
        'total_pages': total_pages,
        'total_pages_list': total_pages_list,
        'page_info': page_info,
    }

    return render(request, 'client/client_album.html', context)


import json
from django.http import JsonResponse
from .models import Photo

def update_photo_order(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            order_data = json.loads(request.body).get('order', [])

            # Update the order of the photos in the database
            for photo_data in order_data:
                photo_id = photo_data['photoId']
                order = photo_data['order']
                photo = Photo.objects.get(id=photo_id)
                photo.order = order
                photo.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})
def favorites_view(request):
    user_id = request.session.get('id')
    if not user_id:
        return HttpResponseRedirect(reverse('login'))  # Redirect to login if not logged in

    # Try to retrieve the user; handle missing user gracefully
    try:
        user = tbl_register.objects.get(id=user_id)
    except tbl_register.DoesNotExist:
        return HttpResponseRedirect(reverse('login'))  # Redirect if user no longer exists

    # Check if the folder password is verified in the session
    folder_verified = request.session.get('folder_password_verified')
    if folder_verified:
        # Get the folder ID from the session
        folder_id = request.session.get('verified_folder_id')

        try:
            folder = PhotoFolder.objects.get(id=folder_id)
            # Filter photos based on the folder and liked by the current user
            liked_photos = Photo.objects.filter(folder=folder, likes=user)
            
            return render(request, 'client/favorites.html', {
                'liked_photos': liked_photos,
                'folder': folder,
                'user': user,
            })

        except PhotoFolder.DoesNotExist:
            # Folder does not exist
            return HttpResponse("Folder not found")

    # If no folder verification, redirect to index or password entry page
    return redirect('client_index')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_album_title(request, album_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title', '')
        album = get_object_or_404(ClientAlbum, id=album_id)
        album.title = title
        album.save()
        return JsonResponse({'status': 'success', 'title': album.title})

@csrf_exempt
def update_album_description(request, album_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description', '')
        album = get_object_or_404(ClientAlbum, id=album_id)
        album.description = description
        album.save()
        return JsonResponse({'status': 'success', 'description': album.description})

@csrf_exempt
def update_page_title(request, album_id, page):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title', '')
        album = get_object_or_404(ClientAlbum, id=album_id)
        # Update the page title in the appropriate structure
        page_titles = json.loads(album.page_titles) if album.page_titles else {}
        page_titles[str(page)] = title
        album.page_titles = json.dumps(page_titles)
        album.save()
        return JsonResponse({'status': 'success', 'title': title})

@csrf_exempt
def update_page_description(request, album_id, page):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description', '')
        album = get_object_or_404(ClientAlbum, id=album_id)
        # Update the page description in the appropriate structure
        page_descriptions = json.loads(album.page_descriptions) if album.page_descriptions else {}
        page_descriptions[str(page)] = description
        album.page_descriptions = json.dumps(page_descriptions)
        album.save()
        return JsonResponse({'status': 'success', 'description': description})

from django.shortcuts import render, get_object_or_404
from .models import Album, Photo
import json
from django.shortcuts import render, get_object_or_404
from .models import Album, Photo
import json
from django.shortcuts import render, get_object_or_404
from .models import Album, Photo
import json


def album_detail_by_share_link(request, share_link):
    # Get the album object using the share link
    album = get_object_or_404(Album, share_link=share_link)

    # Get the photo IDs for the album
    photo_ids = album.photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_ids)

    # Add an absolute_url property dynamically
    for photo in photos:
        photo.absolute_url = photo.image.url

    # Get the photos per page from the album
    photos_per_page = json.loads(album.photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        # Check if the photo should go to the current page
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append(photo)
        else:
            # Move to the next page
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [photo]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the shared album detail page without navigation
    return render(request, 'client/shared_album_detail.html', {
        'album': album,
        'photos_by_page': photos_by_page,
    })

from django.shortcuts import render, get_object_or_404
from .models import PhotoFolder, Album

def view_photogra_album(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        try:
            # Find folder using the password
            folder = PhotoFolder.objects.get(password=password)
            
            # Fetch the albums that belong to this folder
            albums = Album.objects.filter(folder=folder)
            
            return render(request, 'client/view_photogra_album.html', {
                'albums': albums,
                'folder': folder,
            })
        except PhotoFolder.DoesNotExist:
            # If folder not found, show an error message and stay on the password page
            return render(request, 'client/client_index.html', {
                'error_message': "Incorrect password. Please try again."
            })
    else:
        # If password has already been verified (using session), fetch albums based on folder
        if request.session.get('folder_password_verified'):
            folder_id = request.session.get('verified_folder_id')
            folder = get_object_or_404(PhotoFolder, id=folder_id)
            albums = Album.objects.filter(folder=folder)

            return render(request, 'client/view_photogra_album.html', {
                'albums': albums,
                'folder': folder,
            })
    
    # If no password is verified yet, redirect to the password entry page
    return redirect('client_index')



from django.shortcuts import render, get_object_or_404
from .models import ClientAlbum, Photo
import json

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import ClientAlbum, Photo

def client_album_pdf(request, album_id):
    # Get the album object
    album = get_object_or_404(ClientAlbum, id=album_id)
    
    # Retrieve all photos associated with the album
    photos = album.photos.all().order_by('order')

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template for PDF
    html_string = render_to_string('client/client_album_pdf.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response


from django.shortcuts import render, get_object_or_404
from .models import Album, Photo
def client_photogra_album_detail(request, album_id):
    # Get the album object
    album = get_object_or_404(Album, id=album_id)
    
    # Get the photo IDs for the album
    photo_ids = album.photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_ids)

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the album detail page with the photos
    return render(request, 'client/client_photogra_album_detail.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })


from django.shortcuts import render, redirect, get_object_or_404
from .models import Album

def delete_client_album(request, album_id):
    # Check if the photographer ID is available in the session
    client_id = request.session.get('id')  # Changed to 'id' as per your login view
    if client_id is None:
        # Redirect to a login or error page if the photographer ID is not in the session
        return redirect('login')  # Replace with the appropriate URL

    # Get the album to be deleted
    album = get_object_or_404(ClientAlbum, id=album_id)
    
    # Check if the current user is the creator of the album by matching the photographer's ID
    if album.created_by.id == client_id:
        album.delete()  # Delete the album

    return redirect('client_albums_view')  # Redirect to the page that lists albums, or the appropriate page




def album_detail_landscape_pdf(request, album_id):
    # Get the album object
    album = get_object_or_404(Album, id=album_id)
    
    # Get the photo IDs for the album
    photo_ids = album.photo_ids.split(',')
    photos = Photo.objects.filter(id__in=photo_ids)

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template for landscape PDF
    html_string = render_to_string('photographer/album_detail_pdf_landscape.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}_landscape.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response


from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import ClientAlbum, Photo

def client_album_landscape_pdf(request, album_id):
    # Get the album object
    album = get_object_or_404(ClientAlbum, id=album_id)
    
    # Retrieve all photos associated with the album
    photos = album.photos.all().order_by('order')

    # Get the photos per page from the album
    photos_per_page = album.photos_per_page
    photos_per_page = json.loads(photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template for landscape PDF
    html_string = render_to_string('client/client_album_pdf_landscape.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}_landscape.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response

def view_liked_photos(request, folder_id):
    # Get the user_id from the session
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')  # Redirect to login if user is not in the session

    # Try retrieving the user object, if not found, set user to None
    user = tbl_register.objects.filter(id=user_id).first()
    if not user:
        liked_photos = []  # No liked photos if user is not found
    else:
        # Retrieve the folder object
        folder = get_object_or_404(PhotoFolder, id=folder_id)

        # Filter photos in the folder that have been liked by this user
        liked_photos = Photo.objects.filter(folder=folder, likes=user)

    return render(request, 'photographer/view_liked_photos.html', {
        'folder': folder if 'folder' in locals() else None,
        'liked_photos': liked_photos
    })



# client uploading photos and creating album


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ClientPhoto

def upload_photos(request):
    if 'id' not in request.session:  # Changed from 'user_id' to 'id'
        messages.error(request, "You must be logged in to upload photos.")
        return redirect('client_index')  # Redirect to home if not logged in

    user_id = request.session['id']  # Changed from 'user_id' to 'id'

    if request.method == "POST":
        images = request.FILES.getlist('images')  # Get multiple files
        
        # Get the highest order value for the user's photos
        last_order = ClientPhoto.objects.filter(user_id=user_id).order_by('-order').first()
        next_order = (last_order.order + 1) if last_order else 1  # Increment order

        for image in images:
            ClientPhoto.objects.create(user_id=user_id, image=image, order=next_order)
            next_order += 1  # Increment order for each new photo

        messages.success(request, "Photos uploaded successfully.")
        return redirect('upload_photos')  # Refresh the page after upload
    
    photos = ClientPhoto.objects.filter(user_id=user_id).order_by('order')  # Fetch user-specific photos in order
    return render(request, "client/upload_photos.html", {"photos": photos})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import json

def create_custom_album(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(tbl_register, id=user_id)
    
    # Fetch all photos instead of only liked ones
    all_photos = ClientPhoto.objects.all()

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        total_pages = int(request.POST['total_pages'])

        # Prepare dictionaries for photos, titles, and descriptions per page
        photos_per_page = {}
        page_titles = {}
        page_descriptions = {}

        for i in range(1, total_pages + 1):
            photos_per_page[i] = int(request.POST.get(f'photos_page_{i}', 0))
            page_titles[i] = request.POST.get(f'page_title_{i}', '').strip()
            page_descriptions[i] = request.POST.get(f'page_desc_{i}', '').strip()

        # Fetch selected photos
        selected_photos = request.POST.get('selected_photos', '').split(',')
        if not selected_photos or selected_photos == ['']:
            messages.error(request, "Please select at least one photo.")
            return render(request, 'client/create_custom_album.html', {
                'all_photos': all_photos,
                'error': "Please select at least one photo."
            })

        # Create the album
        album = CustomAlbum.objects.create(
            title=title,
            description=description,
            created_by=user,
            total_pages=total_pages,
            photos_per_page=json.dumps(photos_per_page),
            page_titles=json.dumps(page_titles),
            page_descriptions=json.dumps(page_descriptions),
        )

        # Add the selected photos to the album
        for photo_id in selected_photos:
            if photo_id:
                photo = ClientPhoto.objects.get(id=photo_id)
                album.photos.add(photo)

        messages.success(request, f"Album '{title}' created successfully!")
        return redirect('view_custom_album', album_id=album.id)

    return render(request, 'client/create_custom_album.html', {
        'all_photos': all_photos,
    })



from django.shortcuts import render, get_object_or_404
import json
from .models import CustomAlbum  # Adjust the import based on your models
def view_custom_album(request, album_id):
    album = get_object_or_404(CustomAlbum, id=album_id)

    # Retrieve all photos associated with the album, ordered by 'order' field
    photos = album.photos.all().order_by('order', 'uploaded_at')  # Order by `order`, then `uploaded_at`

    # Parse photos_per_page field
    if isinstance(album.photos_per_page, str):
        try:
            photos_per_page_dict = json.loads(album.photos_per_page)
        except json.JSONDecodeError:
            photos_per_page_dict = {}
    else:
        photos_per_page_dict = album.photos_per_page or {}

    # Parse page titles and descriptions
    if isinstance(album.page_titles, str):
        page_titles = json.loads(album.page_titles) or {}
    else:
        page_titles = album.page_titles or {}

    if isinstance(album.page_descriptions, str):
        page_descriptions = json.loads(album.page_descriptions) or {}
    else:
        page_descriptions = album.page_descriptions or {}

    # Combine titles and descriptions into a single dictionary
    page_info = {
        str(page): {
            'title': page_titles.get(str(page), '').strip(),
            'description': page_descriptions.get(str(page), '').strip(),
        }
        for page in range(1, album.total_pages + 1)
    }

    # Organize photos by pages for template use
    photos_by_page = {}
    for page in range(1, len(photos_per_page_dict) + 1):
        page_photos_per_page = photos_per_page_dict.get(str(page), 0)
        start_idx = sum(photos_per_page_dict.get(str(i), 0) for i in range(1, page))
        end_idx = start_idx + page_photos_per_page
        photos_by_page[page] = [
            {
            'id': photo.id,
            'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url),
        }
            for photo in photos[start_idx:end_idx]
        ]

    # Context for rendering the template
    context = {
        'album': album,
        'photos_by_page': photos_by_page,
        'page_info': page_info,
    }

    return render(request, 'client/view_custom_album.html', context)



from django.shortcuts import render, get_object_or_404
from .models import CustomAlbum

def created_albums(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    # Fetch albums created by the logged-in user
    albums = CustomAlbum.objects.filter(created_by_id=user_id)

    return render(request, 'client/created_albums.html', {'albums': albums})


from django.shortcuts import redirect
from django.contrib import messages
from .models import CustomAlbum

def delete_custom_album(request, album_id):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')

    album = get_object_or_404(CustomAlbum, id=album_id, created_by_id=user_id)

    if request.method == "POST":
        album.delete()
        messages.success(request, "Album deleted successfully.")
        return redirect('created_albums')  # Redirect to album list page

    return redirect('view_custom_album', album_id=album_id)  # Redirect back if not POST




import base64
import json
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ClientPhoto

@csrf_exempt
def save_edited_album_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            image_data = data.get('image_data')

            if not photo_id or not image_data:
                return JsonResponse({'success': False, 'message': 'Invalid data'})

            # Decode the image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            decoded_img = ContentFile(base64.b64decode(imgstr), name=f"edited_photo_{photo_id}.{ext}")

            # Retrieve the original photo
            original_photo = get_object_or_404(ClientPhoto, id=photo_id)

            # Replace the existing image without deleting the record
            original_photo.edited_image = decoded_img
            original_photo.is_edited = True
            original_photo.save()

            return JsonResponse({'success': True, 'new_photo_id': original_photo.id})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import json
import base64
from .models import ClientPhoto

@csrf_exempt
def save_edited_album_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            image_data = data.get('image_data')

            if not photo_id or not image_data:
                return JsonResponse({'success': False, 'message': 'Invalid data'})

            # Decode the image data
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            decoded_img = ContentFile(base64.b64decode(imgstr), name=f"edited_photo_{photo_id}.{ext}")

            # Retrieve the original photo
            original_photo = ClientPhoto.objects.get(id=photo_id)

            # Save the new edited photo
            original_photo.edited_image.save(f"edited_photo_{photo_id}.{ext}", decoded_img, save=True)
            original_photo.is_edited = True
            original_photo.save()

            return JsonResponse({'success': True, 'new_photo_id': original_photo.id})

        except ClientPhoto.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Photo not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})






@csrf_exempt
def update_custom_album_title(request, album_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title', '')
        album = get_object_or_404(CustomAlbum, id=album_id)
        album.title = title
        album.save()
        return JsonResponse({'status': 'success', 'title': album.title})

@csrf_exempt
def update_custom_album_description(request, album_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description', '')
        album = get_object_or_404(CustomAlbum, id=album_id)
        album.description = description
        album.save()
        return JsonResponse({'status': 'success', 'description': album.description})

@csrf_exempt
def update_custom_page_title(request, album_id, page):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title', '')
        album = get_object_or_404(CustomAlbum, id=album_id)
        # Update the page title in the appropriate structure
        page_titles = json.loads(album.page_titles) if album.page_titles else {}
        page_titles[str(page)] = title
        album.page_titles = json.dumps(page_titles)
        album.save()
        return JsonResponse({'status': 'success', 'title': title})

@csrf_exempt
def update_custom_page_description(request, album_id, page):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data.get('description', '')
        album = get_object_or_404(CustomAlbum, id=album_id)
        # Update the page description in the appropriate structure
        page_descriptions = json.loads(album.page_descriptions) if album.page_descriptions else {}
        page_descriptions[str(page)] = description
        album.page_descriptions = json.dumps(page_descriptions)
        album.save()
        return JsonResponse({'status': 'success', 'description': description})

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from .models import CustomAlbum, ClientPhoto
import json
from weasyprint import HTML  # Make sure you have WeasyPrint installed

def download_pdf_portrait(request, album_id):
    # Get the album object
    album = get_object_or_404(CustomAlbum, id=album_id)
    
    # Get the photos associated with the album
    photos = album.photos.all().order_by('order')  # This retrieves all ClientPhoto instances related to the album

    # Get the photos per page from the album
    photos_per_page = json.loads(album.photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]

    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template for portrait PDF
    html_string = render_to_string('client/download_pdf_portrait.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response

def download_pdf_landscape(request, album_id):
    # Get the album object
    album = get_object_or_404(CustomAlbum, id=album_id)
    
    # Get the photos associated with the album
    photos = album.photos.all().order_by('order')  # This retrieves all ClientPhoto instances related to the album

    # Get the photos per page from the album
    photos_per_page = json.loads(album.photos_per_page)  # Convert JSON string back to dictionary

    # Organize the photos based on the pages and photos per page
    photos_by_page = []
    current_page = 1
    current_page_photos = []

    for i, photo in enumerate(photos):
        if len(current_page_photos) < photos_per_page.get(str(current_page), 0):
            current_page_photos.append({
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            })
        else:
            photos_by_page.append((current_page, current_page_photos))
            current_page += 1
            current_page_photos = [{
                'photo': photo,
                'absolute_url': request.build_absolute_uri(photo.edited_image.url) if photo.is_edited and photo.edited_image else request.build_absolute_uri(photo.image.url)  # Create absolute URL
            }]
    if current_page_photos:
        photos_by_page.append((current_page, current_page_photos))

    # Render the HTML template for landscape PDF
    html_string = render_to_string('client/download_pdf_landscape.html', {
        'album': album,
        'photos_by_page': photos_by_page,
        'request': request,  # Pass the request object
    })

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{album.title}_landscape.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)

    return response



def update_custom_photo_order(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            order_data = json.loads(request.body).get('order', [])

            # Update the order of the photos in the database
            for photo_data in order_data:
                photo_id = photo_data['photoId']
                order = photo_data['order']
                photo = ClientPhoto.objects.get(id=photo_id)
                photo.order = order
                photo.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClientPhoto
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClientPhoto
def delete_custom_photo(request, photo_id):
    photo = get_object_or_404(ClientPhoto, id=photo_id)

    # Get the user ID from the session
    user_id = request.session.get('id')

    if user_id and photo.user_id == user_id:  # Check if user_id exists and matches
        photo.delete()
        messages.success(request, "Photo deleted successfully!")
    else:
        messages.error(request, "You are not authorized to delete this photo.")

    return redirect('upload_photos')
