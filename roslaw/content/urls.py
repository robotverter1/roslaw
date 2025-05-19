from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from . import views

def moderator_check(user):
    """Function to check if user has moderation permissions."""
    return user.is_authenticated and (
        user.is_superuser or 
        user.is_content_admin() or 
        user.is_moderator() or
        getattr(user, 'role', '') in ['admin', 'curator', 'moderator']
    )

app_name = 'content'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Chapter CRUD
    path('chapter/create/', views.ChapterCreateView.as_view(), name='chapter_create'),
    path('chapter/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    path('chapter/<int:pk>/edit/', views.ChapterUpdateView.as_view(), name='chapter_edit'),
    path('chapter/<int:pk>/delete/', views.ChapterDeleteView.as_view(), name='chapter_delete'),
    
    # Section CRUD
    path('section/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('section/<int:pk>/', views.SectionDetailView.as_view(), name='section_detail'),
    path('section/<int:pk>/edit/', views.SectionUpdateView.as_view(), name='section_edit'),
    path('section/<int:pk>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    
    # Subsection CRUD
    path('subsection/create/', views.SubsectionCreateView.as_view(), name='subsection_create'),
    path('subsection/<int:pk>/', views.SubsectionDetailView.as_view(), name='subsection_detail'),
    path('subsection/<int:pk>/edit/', views.SubsectionUpdateView.as_view(), name='subsection_edit'),
    path('subsection/<int:pk>/delete/', views.SubsectionDeleteView.as_view(), name='subsection_delete'),
    
    # QA CRUD paths
    path('qa/create/', views.QACreateView.as_view(), name='qa_create'),
    path('qa/<int:pk>/edit/', views.QAUpdateView.as_view(), name='qa_edit'),
    path('qa/<int:pk>/', views.QADetailView.as_view(), name='qa_detail'),
    path('qa/<int:pk>/review/', views.QAReviewView.as_view(), name='qa_review_action'),
    path('qa/<int:pk>/send-to-review/', views.QASendToReviewView.as_view(), name='qa_send_to_review'),
    path('qa/<int:pk>/delete/', views.QADeleteView.as_view(), name='qa_delete'),
    path('qa/cancel/<int:pk>/', views.QACancelCreationView.as_view(), name='qa_cancel'),
    path('qa/cancel/', views.QACancelCreationView.as_view(), name='qa_cancel_create'),
    
    # Fix: Add the missing qa_cancel_edit URL pattern
    path('qa/<int:pk>/cancel/', views.QACancelCreationView.as_view(), name='qa_cancel_edit'),
    
    # Add explicit previewing path for content in moderation
    path('qa/<int:pk>/preview/', views.QADetailView.as_view(), name='qa_preview'),
    
    # User QA management
    path('my-qa/', views.QAUserListView.as_view(), name='user_qa_list'),
    
    # Moderation URLs - ensure all use qa_id parameter
    path('moderation/', views.moderation_view, name='moderation'),
    path('moderation/<int:qa_id>/', views.moderation_detail, name='moderation_detail'),
    
    # Redirect legacy review URLs to moderation detail
    path('review/<int:qa_id>/', views.moderation_detail, name='review_item'),
    
    # Keep these for backwards compatibility but they'll redirect to the new views
    path('moderation/review/<int:article_id>/', views.moderation_detail, name='review'),
    
    # We can remove these since their functionality is now in moderation_detail
    # path('review/<int:item_id>/approve/', views.approve_item, name='approve_item'),
    # path('review/<int:item_id>/reject/', views.reject_item, name='reject_item'),
    
    # Debug URL - temporary
    path('debug/qa-status/', views.debug_qa_status, name='debug_qa_status'),
    
    # Make sure all necessary URL patterns are present
    path('chapter/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    path('section/<int:pk>/', views.SectionDetailView.as_view(), name='section_detail'),
    path('subsection/<int:pk>/', views.SubsectionDetailView.as_view(), name='subsection_detail'),
]
