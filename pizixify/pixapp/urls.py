from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import*

urlpatterns = [
   path('', views.index, name='index'),
   path('login/', views.login, name='login'),
   path('logout/', views.logout, name='logout'),
  
    

# -- Client -- #


   path('client_register/', views.client_register, name='client_register'),
     path('upload_photos/', upload_photos, name='upload_photos'),
    path('client_index/', views.client_index, name='client_index'),
    path('client_view_folder/', views.client_view_folder, name='client_view_folder'),
    path('like_photo/<int:photo_id>/', views.like_photo, name='like_photo'),
    path('client_create_album/', views.client_create_album, name='client_create_album'),
   path('client_album/<int:album_id>/', views.client_album, name='client_album'),
   path('client_albums_view/', views.client_albums_view, name='client_albums_view'),
    path('update-photo-order/', views.update_photo_order, name='update-photo-order'),
     path('favorites/', views.favorites_view, name='favorites'),
     path('liked-photos/<int:folder_id>/', views.view_liked_photos, name='view_liked_photos'),
     path('update_album_title/<int:album_id>/', views.update_album_title, name='update_album_title'),
    path('update_album_description/<int:album_id>/', views.update_album_description, name='update_album_description'),
    path('update_page_title/<int:album_id>/<int:page>/', views.update_page_title, name='update_page_title'),
    path('update_page_description/<int:album_id>/<int:page>/', views.update_page_description, name='update_page_description'),

path('view-album/<str:share_link>/', views.album_detail_by_share_link, name='album_detail_by_share_link'),
 path('view-photo-album/', views.view_photogra_album, name='view_photogra_album'),
 path('album/<int:album_id>/pdf/', views.album_detail_pdf, name='album_detail_pdf'),
 path('client_album_pdf/<int:album_id>/', views.client_album_pdf, name='client_album_pdf'),
  path('client_album_detail/<int:album_id>/', views.client_photogra_album_detail, name='client_photogra_album_detail'),
   path('delete_client_album/<int:album_id>/', views.delete_client_album, name='delete_client_album'),

path('client/album/<int:album_id>/download-landscape-pdf/', views.client_album_landscape_pdf, name='client_album_landscape_pdf'),
   path('album/<int:album_id>/download-landscape-pdf/', views.album_detail_landscape_pdf, name='album_detail_landscape_pdf'),


   path('custom-album/create/', views.create_custom_album, name='create_custom_album'),
   path('view_custom_album/<int:album_id>/', views.view_custom_album, name='view_custom_album'),
   path('my-albums/', views.created_albums, name='created_albums'),
    path('delete-album/<int:album_id>/', views.delete_custom_album, name='delete_custom_album'),

 
  
   path('update_custom_album_title/<int:album_id>/', views.update_custom_album_title, name='update_custom_album_title'),
    path('update_custom_album_description/<int:album_id>/', views.update_custom_album_description, name='update_custom_album_description'),
    path('update_custom_page_title/<int:album_id>/<int:page>/', views.update_custom_page_title, name='update_custom_page_title'),
    path('update_custom_page_description/<int:album_id>/<int:page>/', views.update_custom_page_description, name='update_custom_page_description'),

 path('download-pdf-portrait/<int:album_id>/', download_pdf_portrait, name='download_pdf_portrait'),
    path('download-pdf-landscape/<int:album_id>/', download_pdf_landscape, name='download_pdf_landscape'),
    path('update-custom-photo-order/', views.update_custom_photo_order, name='update-custom-photo-order'),
     path('delete_custom_photo/<int:photo_id>/', delete_custom_photo, name='delete_custom_photo'),

#---- Phototgrapher ----#
path('photogra_index/',views.photogra_index,name='photogra_index'),
   path('photogra_register/', views.photogra_register, name='photogra_register'),
   path('photogra_profile/', views.photogra_profile, name='photogra_profile'),
   path('photogra_edit_profile/', views.photogra_edit_profile, name='photogra_edit_profile'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('folder_list/', views.folder_list, name='folder_list'),
    path('access_folder/<int:folder_id>/', views.access_folder, name='access_folder'),
   path('folder/<int:id>/add_photos/', views.add_photos, name='add_photos'),
path('delete_photo/<int:photo_id>/', views.delete_photo, name='delete_photo'),
 path('create_album/', views.create_album, name='create_album'),
 path('album/<int:album_id>/', views.album_detail, name='album_detail'),
 path('view_created_albums/',views.view_created_albums, name='view_created_albums'),
 path('delete_folder/', views.delete_folder, name='delete_folder'),
  path('delete_album/<int:album_id>/', views.delete_album, name='delete_album'),




]
