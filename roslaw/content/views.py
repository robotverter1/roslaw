from django.views.generic import TemplateView, CreateView, View, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, Http404  # Add Http404 import
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Chapter, Section, Subsection, QA, QA_Subsection, QAReference
from django.core.exceptions import FieldError  # Add this import for FieldError
from django.apps import apps
import logging


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "content/dashboard.html"
    login_url = "accounts:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get unread notifications count for the navbar
        context['unread_notifications'] = user.notifications.filter(is_read=False).count()

        # Get active items from query parameters
        active_chapter_id = self.request.GET.get("chapter", None)
        active_section_id = self.request.GET.get("section", None)
        active_subsection_id = self.request.GET.get("subsection", None)
        filter_status = self.request.GET.get("status", None)  # New parameter for filtering by status

        chapters = Chapter.objects.all().order_by("order")

        if not active_chapter_id and chapters.exists():
            active_chapter_id = chapters.first().id

        active_sections = []
        if active_chapter_id:
            active_chapter_id = int(active_chapter_id)
            active_sections = Section.objects.filter(
                chapter_id=active_chapter_id
            ).order_by("order")

            if not active_section_id and active_sections.exists():
                active_section_id = active_sections.first().id

        active_subsections = []
        if active_section_id:
            active_section_id = int(active_section_id)
            active_subsections = Subsection.objects.filter(
                section_id=active_section_id
            ).order_by("order")

            if not active_subsection_id and active_subsections.exists():
                active_subsection_id = active_subsections.first().id

        context.update(
            {
                "published_count": QA.objects.filter(
                    author=user, status=QA.STATUS_PUBLISHED
                ).count(),
                "in_review_count": QA.objects.filter(
                    author=user, status=QA.STATUS_IN_REVIEW
                ).count(),
                "rejected_count": QA.objects.filter(
                    author=user, status=QA.STATUS_REJECTED
                ).count(),
                "chapters": chapters,
                "active_chapter_id": active_chapter_id,
                "active_section_id": active_section_id,
                "active_subsection_id": active_subsection_id,
                "active_sections": active_sections,
                "active_subsections": active_subsections,
            }
        )

        if active_subsection_id:
            active_subsection_id = int(active_subsection_id)
            
            # Base query - filter by subsection
            base_query = QA.objects.filter(qa_subsections__subsection_id=active_subsection_id)
            
            # Apply status filter if provided
            if filter_status and filter_status != 'all':
                base_query = base_query.filter(status=filter_status)
            
            # Different visibility rules based on user role
            if user.is_content_admin() or user.is_moderator():
                # Admins and moderators can see everything
                qa_items = base_query.order_by("question")
            else:
                # Regular users can see published content and their own content
                published_items = base_query.filter(status=QA.STATUS_PUBLISHED)
                user_items = base_query.filter(author=user)
                
                # Combine querysets
                qa_items = published_items | user_items
                qa_items = qa_items.distinct().order_by("question")

            context["active_qa_items"] = qa_items
            context["filter_status"] = filter_status  # Add to context for template

        return context


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    fields = ["title", "order"]  # уберите 'description', если его нет в модели
    success_url = reverse_lazy("content:dashboard")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Глава успешно создана.")
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                chapter = form.save(commit=False)
                chapter.author = request.user
                chapter.save()
                return JsonResponse({'success': True, 'chapter_id': chapter.id})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().post(request, *args, **kwargs)


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = Section
    fields = ["title", "order"]  # уберите 'description', если его нет в модели
    success_url = reverse_lazy("content:dashboard")

    def form_valid(self, form):
        form.instance.author = self.request.user
        chapter_id = self.request.POST.get("chapter_id")
        if chapter_id:
            form.instance.chapter_id = chapter_id
        else:
            return JsonResponse({'success': False, 'error': 'chapter_id required'}, status=400)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                section = form.save(commit=False)
                section.author = request.user
                chapter_id = request.POST.get("chapter_id")
                if chapter_id:
                    section.chapter_id = chapter_id
                else:
                    return JsonResponse({'success': False, 'error': 'chapter_id required'}, status=400)
                section.save()
                return JsonResponse({'success': True, 'section_id': section.id})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().post(request, *args, **kwargs)


class SubsectionCreateView(LoginRequiredMixin, CreateView):
    model = Subsection
    fields = ["title", "order"]  # уберите 'description', если его нет в модели
    success_url = reverse_lazy("content:dashboard")

    def form_valid(self, form):
        form.instance.author = self.request.user
        section_id = self.request.POST.get("section_id")
        if section_id:
            form.instance.section_id = section_id
        else:
            return JsonResponse({'success': False, 'error': 'section_id required'}, status=400)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.get_form()
            if form.is_valid():
                subsection = form.save(commit=False)
                subsection.author = request.user
                section_id = request.POST.get("section_id")
                if section_id:
                    subsection.section_id = section_id
                else:
                    return JsonResponse({'success': False, 'error': 'section_id required'}, status=400)
                subsection.save()
                return JsonResponse({'success': True, 'subsection_id': subsection.id})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().post(request, *args, **kwargs)


class QACreateView(LoginRequiredMixin, CreateView):
    model = QA
    template_name = 'content/qa_create.html'
    fields = ['question', 'answer']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load all chapters, sections, and subsections for selection
        context['chapters'] = Chapter.objects.all().order_by('order')
        context['sections'] = Section.objects.all().order_by('order')
        context['subsections'] = Subsection.objects.all().order_by('order')
        
        # Get max number of subsection locations allowed
        context['max_locations'] = 3  # User can place QA in up to 3 subsections
        
        # Get max number of references allowed
        context['max_links'] = 3
        
        # Pre-select subsection if specified in query params
        subsection_id = self.request.GET.get('subsection')
        if subsection_id:
            try:
                subsection = Subsection.objects.get(pk=subsection_id)
                context['preselected_subsection'] = subsection
                context['preselected_section'] = subsection.section
                context['preselected_chapter'] = subsection.section.chapter
            except Subsection.DoesNotExist:
                pass
                
        return context
    
    def form_valid(self, form):
        # Set author and initial status
        form.instance.author = self.request.user
        form.instance.status = QA.STATUS_DRAFT  # Use constant from model
        form.instance.written_at = timezone.now()
        
        # Save the QA object
        qa = form.save()
        
        # Handle subsection associations (up to 3)
        selected_subsections = []
        for i in range(1, 4):  # Max 3 locations
            subsection_id = self.request.POST.get(f'subsection_id_{i}')
            if subsection_id:
                selected_subsections.append(subsection_id)
        
        # Create QA_Subsection relationships
        for idx, subsection_id in enumerate(selected_subsections, start=1):
            QA_Subsection.objects.create(
                qa=qa, 
                subsection_id=subsection_id,
                copy_number=idx
            )
        
        # Handle references if any
        for i in range(1, int(self.request.POST.get('reference_count', 0)) + 1):
            description = self.request.POST.get(f'reference_description_{i}')
            url = self.request.POST.get(f'reference_url_{i}')
            
            if url:  # Only create reference if URL is provided
                QAReference.objects.create(
                    qa=qa,
                    description=description or '',
                    url=url
                )
                
        # Handle different submission types
        if 'submit_draft' in self.request.POST:
            qa.status = 'draft'
            messages.success(self.request, "Вопрос-ответ успешно сохранен как черновик.")
        elif 'submit_review' in self.request.POST:
            # Set to "pending" for moderation
            qa.status = 'pending'  # Use 'pending' not QA.STATUS_IN_REVIEW
            messages.success(self.request, "Вопрос-ответ отправлен на проверку.")
        
        qa.save()
        
        # Redirect to appropriate page based on submission type
        if 'submit_draft' in self.request.POST:
            return HttpResponseRedirect(reverse('content:qa_edit', kwargs={'pk': qa.id}))
        else:
            return HttpResponseRedirect(reverse('content:dashboard'))
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Handle AJAX request (for reference adding/removing)
            action = request.POST.get('action')
            
            if action == 'add_reference':
                # Return HTML for new reference form
                reference_index = request.POST.get('index', '1')
                context = {'index': reference_index}
                return JsonResponse({
                    'success': True,
                    'html': render(request, 'content/partials/reference_form.html', context).content.decode('utf-8')
                })
                
            return JsonResponse({'success': False, 'error': 'Invalid action'})
            
        return super().post(request, *args, **kwargs)


class QAUpdateView(LoginRequiredMixin, UpdateView):
    model = QA
    template_name = 'content/qa_edit.html'
    fields = ['question', 'answer']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all chapters, sections, subsections for selection
        context['chapters'] = Chapter.objects.all().order_by('order')
        context['sections'] = Section.objects.all().order_by('order')
        context['subsections'] = Subsection.objects.all().order_by('order')
        
        # Get current subsection associations
        qa_subsections = QA_Subsection.objects.filter(qa=self.object).order_by('copy_number')
        context['qa_subsections'] = qa_subsections
        
        # Add references
        context['references'] = QAReference.objects.filter(qa=self.object)
        context['max_links'] = self.object.max_links
        context['max_locations'] = 3
        
        return context
    
    def form_valid(self, form):
        qa = form.save(commit=False)
        
        # Update subsection associations - first delete existing ones
        QA_Subsection.objects.filter(qa=qa).delete()
        
        # Handle new subsection associations (up to 3)
        selected_subsections = []
        for i in range(1, 4):  # Max 3 locations
            subsection_id = self.request.POST.get(f'subsection_id_{i}')
            if subsection_id:
                selected_subsections.append(subsection_id)
        
        # Create QA_Subsection relationships
        for idx, subsection_id in enumerate(selected_subsections, start=1):
            QA_Subsection.objects.create(
                qa=qa, 
                subsection_id=subsection_id,
                copy_number=idx
            )
        
        # Handle references - first delete existing ones
        if not self.request.POST.get('preserve_references'):
            QAReference.objects.filter(qa=qa).delete()
            
            # Then add new ones
            for i in range(1, int(self.request.POST.get('reference_count', 0)) + 1):
                description = self.request.POST.get(f'reference_description_{i}')
                url = self.request.POST.get(f'reference_url_{i}')
                
                if url:  # Only create reference if URL is provided
                    QAReference.objects.create(
                        qa=qa,
                        description=description or '',
                        url=url
                    )
        
        # Handle different submission types
        if 'submit_draft' in self.request.POST:
            qa.status = 'draft'
            messages.success(self.request, "Вопрос-ответ успешно обновлен как черновик.")
        elif 'submit_review' in self.request.POST:
            # Set to "pending" for moderation
            qa.status = 'pending'  # Use 'pending' not QA.STATUS_IN_REVIEW
            messages.success(self.request, "Вопрос-ответ отправлен на проверку.")
        
        qa.save()
        
        # Redirect based on submission type
        if 'submit_draft' in self.request.POST:
            return HttpResponseRedirect(reverse('content:qa_edit', kwargs={'pk': qa.id}))
        else:
            return HttpResponseRedirect(reverse('content:dashboard'))
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Handle AJAX request (for reference adding/removing)
            # Similar to create view
            return JsonResponse({'success': True})
            
        return super().post(request, *args, **kwargs)


class QADetailView(LoginRequiredMixin, DetailView):
    model = QA
    template_name = 'content/qa_detail.html'
    context_object_name = 'qa'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user
        
        # Check permissions - allow access to:
        # 1. Content admins/moderators
        # 2. The author of the content
        # 3. Anyone if content is published
        if (user.is_content_admin() or user.is_moderator() or 
            obj.author == user or obj.status == QA.STATUS_PUBLISHED):
            return obj
            
        # If none of the conditions are met, show an error message
        messages.error(self.request, "У вас нет доступа к этому контенту.")
        raise Http404("Content not accessible")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['references'] = QAReference.objects.filter(qa=self.object)
        
        # Add status context for conditional display
        context['is_author'] = self.object.author == self.request.user
        context['is_moderator'] = self.request.user.is_content_admin() or self.request.user.is_moderator()
        context['can_edit'] = context['is_author'] and self.object.status != QA.STATUS_PUBLISHED
        context['need_moderation'] = self.object.status == QA.STATUS_IN_REVIEW
        
        # Get associated subsections
        qa_subsections = QA_Subsection.objects.filter(qa=self.object)
        if qa_subsections.exists():
            subsection = qa_subsections.first().subsection
            section = subsection.section
            chapter = section.chapter
            
            # Add context data
            context['selected_subsection'] = subsection
            context['selected_section'] = section
            context['selected_chapter'] = chapter
            
        return context


class QASendToReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        qa = get_object_or_404(QA, pk=pk)
        
        # Check permissions
        if qa.author != request.user and not request.user.is_content_admin():
            messages.error(request, "У вас нет прав для отправки этого вопрос-ответа на проверку.")
            return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))
        
        # Set status to "pending" for moderation
        qa.status = 'pending'  # Use 'pending' not QA.STATUS_IN_REVIEW
        qa.save()
        
        messages.success(request, "Вопрос-ответ отправлен на проверку.")
        return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))


class QAReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        qa = get_object_or_404(QA, pk=pk)
        
        # Check permissions
        if not request.user.is_content_admin() and not request.user.is_moderator():
            messages.error(request, "У вас нет прав для проверки этого вопрос-ответа.")
            return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))
        
        action = request.POST.get('action')
        
        if action == 'approve':
            qa.status = QA.STATUS_PUBLISHED
            qa.is_published = True
            messages.success(request, "Вопрос-ответ одобрен и опубликован.")
        elif action == 'reject':
            qa.status = QA.STATUS_REJECTED
            messages.success(request, "Вопрос-ответ отклонен.")
        
        qa.save()
        
        return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))


class QACancelCreationView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        # If pk provided, it's cancellation of existing QA edit
        if pk:
            qa = get_object_or_404(QA, pk=pk)
            return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))
        
        # Otherwise, cancel new creation
        return HttpResponseRedirect(reverse('content:dashboard'))
        
    # Add GET method support in case the form is submitted via GET
    def get(self, request, pk=None):
        return self.post(request, pk)


class QAListView(LoginRequiredMixin, ListView):
    model = QA
    template_name = "content/qa_list.html"
    context_object_name = "qa_items"

    def get_queryset(self):
        return QA.objects.filter(author_id=self.request.user.id)


class QAModerationListView(LoginRequiredMixin, ListView):
    model = QA
    template_name = 'content/moderation_list.html'
    context_object_name = 'qa_items'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has moderation permissions
        if not (request.user.role == 'moderator' or request.user.role == 'admin' or 
                request.user.role == 'curator' or request.user.is_content_admin()):
            messages.error(request, "У вас нет прав для модерации контента.")
            return redirect('content:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return QA.objects.filter(status=QA.STATUS_IN_REVIEW).order_by('-created_at')


class QAUserListView(LoginRequiredMixin, ListView):
    model = QA
    template_name = 'content/user_qa_list.html'
    context_object_name = 'qa_items'
    
    def get_queryset(self):
        return QA.objects.filter(author=self.request.user).order_by('-created_at')


class QADeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        qa = get_object_or_404(QA, pk=pk)
        
        # Check permissions
        if qa.author != request.user and not (request.user.role in ['admin', 'curator'] or 
                                             request.user.is_content_admin()):
            messages.error(request, "У вас нет прав для удаления этого вопрос-ответа.")
            return HttpResponseRedirect(reverse('content:qa_detail', kwargs={'pk': qa.id}))
        
        qa.is_deleted = True
        qa.deleted_by = request.user
        qa.save()
        
        messages.success(request, "Вопрос-ответ успешно удален.")
        return HttpResponseRedirect(reverse('content:user_qa_list'))


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

@login_required
def moderation_view(request):
    """
    Simplified moderation view that will display ALL QA items
    """
    # Get absolutely all QA objects with no filtering
    all_qa = list(QA.objects.all().order_by('-created_at'))
    
    # Log exactly what we found
    print(f"MODERATION DEBUG: Found {len(all_qa)} total QA items")
    for qa in all_qa[:5]:  # Print details of first 5 items
        print(f"QA ID: {qa.id}, Question: {qa.question[:20]}, Status: {qa.status}")
    
    # Just pass ALL items to the template
    context = {'all_qa_items': all_qa}
    
    # Use the correct template path
    return render(request, 'content/moderation_simple.html', context)

@login_required
def moderation_detail(request, qa_id):
    """
    View for reviewing a specific QA item with full content display
    """
    # Get the specific QA item
    qa = get_object_or_404(QA, pk=qa_id)
    
    # Get references associated with the QA
    references = QAReference.objects.filter(qa=qa)
    
    # Handle approve/reject actions
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            qa.status = 'published'
            qa.is_published = True
            qa.save()
            messages.success(request, "Публикация одобрена и опубликована.")
            return redirect('content:moderation')
            
        elif action == 'reject':
            qa.status = 'rejected'
            qa.save()
            messages.success(request, "Публикация отклонена.")
            return redirect('content:moderation')
    
    context = {
        'qa': qa,
        'references': references
    }
    
    return render(request, 'content/moderation_detail.html', context)

@login_required
def review_article(request, article_id):
    """
    View for reviewing a specific article
    """
    from content.models import Article
    from django.shortcuts import get_object_or_404, redirect
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            article.status = 'published'
            article.save()  # Fix: The syntax error was here
        elif action == 'reject':
            article.status = 'rejected'
            article.save()
        return redirect('content:moderation')
    return render(request, 'content/review_article.html', {'article': article})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required
def review_item(request, item_id):
    """
    View for reviewing a specific content item
    """
    user = request.user
    user_role = getattr(user, 'role', None)
    # Allow superadmin explicitly and block specific roles
    allowed_roles = ['superadmin', 'admin', 'moderator']
    # If user is superadmin, allow access regardless of other checks
    if hasattr(user, 'is_superuser') and user.is_superuser:
        pass  # Allow access
    # Check role if it's one of the restricted ones
    elif user_role and user_role not in allowed_roles:
        messages.error(request, "You don't have permission to review content.")
        return redirect('/')
    
    # Dynamically try to get the item from various models
    from django.apps import apps
    
    item = None
    models_to_try = ['Article', 'Content', 'Post']
    for model_name in models_to_try:
        try:
            Model = apps.get_model('content', model_name)
            item = Model.objects.filter(id=item_id).first()
            if item:
                break
        except LookupError:
            continue
    if not item:
        messages.error(request, "Content item not found.")
        return redirect('content:moderation')
    
    return render(request, 'content/review_item.html', {'item': item})

@require_POST
@login_required
def approve_item(request, item_id):
    """
    Approve a content item
    """
    user = request.user
    user_role = getattr(user, 'role', None)
    if user_role in ['volunteer', 'blocked', 'specialist']:
        return JsonResponse({'error': "You don't have permission to approve content."}, status=403)
    
    # Similar logic to find the item
    from django.apps import apps
    item = None
    models_to_try = ['Article', 'Content', 'Post']
    for model_name in models_to_try:
        try:
            Model = apps.get_model('content', model_name)
            item = Model.objects.filter(id=item_id).first()
            if item:
                break
        except LookupError:
            continue
    if not item:
        return JsonResponse({'error': "Content item not found."}, status=404)
    
    # Update item status based on available fields
    if hasattr(item, 'is_approved'):
        item.is_approved = True
    if hasattr(item, 'status'):
        item.status = 'approved'
    item.save()
    
    return JsonResponse({'status': 'approved'})

@require_POST
@login_required
def reject_item(request, item_id):
    """
    Reject a content item
    """
    user = request.user
    user_role = getattr(user, 'role', None)
    if user_role in ['volunteer', 'blocked', 'specialist']:
        return JsonResponse({'error': "You don't have permission to reject content."}, status=403)
    
    # Similar logic to find the item
    from django.apps import apps
    item = None
    models_to_try = ['Article', 'Content', 'Post']
    for model_name in models_to_try:
        try:
            Model = apps.get_model('content', model_name)
            item = Model.objects.filter(id=item_id).first()
            if item:
                break
        except LookupError:
            continue
    if not item:
        return JsonResponse({'error': "Content item not found."}, status=404)
    
    # Update item status based on available fields
    if hasattr(item, 'is_approved'):
        item.is_approved = False
    if hasattr(item, 'status'):
        item.status = 'rejected'
    item.save()
    
    return JsonResponse({'status': 'rejected'})

@login_required
def debug_qa_status(request):
    """
    Debug view to check QA statuses in the database
    """
    from django.http import HttpResponse
    import json
    
    # Get all QA items
    all_qa = QA.objects.all().order_by('-created_at')
    
    # Collect debug info
    debug_info = {
        'total_qa_count': all_qa.count(),
        'status_counts': {},
        'status_constants': {
            'STATUS_DRAFT': QA.STATUS_DRAFT,
            'STATUS_PENDING': QA.STATUS_PENDING,
            'STATUS_IN_REVIEW': QA.STATUS_IN_REVIEW,
            'STATUS_ACCEPTED': QA.STATUS_ACCEPTED,
            'STATUS_REJECTED': QA.STATUS_REJECTED,
            'STATUS_PUBLISHED': QA.STATUS_PUBLISHED,
        },
        'recent_items': []
    }
    # Count items by status
    all_statuses = list(QA.objects.values_list('status', flat=True).distinct())
    for status in all_statuses:
        count = QA.objects.filter(status=status).count()
        debug_info['status_counts'][status] = count
    
    # Get info about 10 most recent items
    for qa in all_qa[:10]:
        debug_info['recent_items'].append({
            'id': qa.id,
            'question': qa.question[:50],
            'status': qa.status,
            'created_at': qa.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Return as JSON response
    return HttpResponse(
        json.dumps(debug_info, indent=2),
        content_type='application/json'
    )

@login_required
def moderation_detail_view(request, qa_id):
    """
    View for displaying and moderating a specific QA item
    """
    # Get the QA item
    qa = get_object_or_404(QA, id=qa_id)
    
    # Get references for this QA item
    references = QAReference.objects.filter(qa=qa)
    
    # Handle post requests (approve/reject actions)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            qa.status = 'published'
            qa.is_published = True
            qa.save()
            messages.success(request, "Публикация одобрена и опубликована.")
            return redirect('content:moderation')
            
        elif action == 'reject':
            qa.status = 'rejected'
            qa.save()
            messages.success(request, "Публикация отклонена.")
            return redirect('content:moderation')
    
    # Prepare context data
    context = {
        'qa': qa,
        'references': references,
    }
    
    return render(request, 'content/moderation_detail.html', context)

class ChapterDetailView(LoginRequiredMixin, DetailView):
    model = Chapter
    template_name = 'content/chapter_detail.html'
    context_object_name = 'chapter'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = Section.objects.filter(chapter=self.object).order_by('order')
        context['is_author'] = self.object.author == self.request.user
        context['is_admin'] = self.request.user.is_content_admin() or self.request.user.is_moderator()
        context['can_edit'] = context['is_author'] or context['is_admin']
        context['can_delete'] = context['is_admin']
        return context

class SectionDetailView(LoginRequiredMixin, DetailView):
    model = Section
    template_name = 'content/section_detail.html'
    context_object_name = 'section'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subsections'] = Subsection.objects.filter(section=self.object).order_by('order')
        context['is_author'] = self.object.author == self.request.user
        context['is_admin'] = self.request.user.is_content_admin() or self.request.user.is_moderator()
        context['can_edit'] = context['is_author'] or context['is_admin']
        context['can_delete'] = context['is_admin']
        return context

class SubsectionDetailView(LoginRequiredMixin, DetailView):
    model = Subsection
    template_name = 'content/subsection_detail.html'
    context_object_name = 'subsection'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get QA items associated with this subsection
        qa_items = QA.objects.filter(
            qa_subsections__subsection=self.object,
            is_deleted=False
        )
        
        # Filter by status for regular users
        if not (self.request.user.is_content_admin() or self.request.user.is_moderator()):
            # Regular users see published items and their own items
            published_items = qa_items.filter(status='published')
            own_items = qa_items.filter(author=self.request.user)
            qa_items = published_items | own_items
            qa_items = qa_items.distinct()
            
        qa_items = qa_items.order_by('question')
        
        # Add to context
        context['qa_items'] = qa_items
        context['is_author'] = self.object.author == self.request.user
        context['is_admin'] = self.request.user.is_content_admin() or self.request.user.is_moderator()
        context['can_edit'] = context['is_author'] or context['is_admin']
        
        # Get navigation context
        context['chapter'] = self.object.section.chapter
        context['section'] = self.object.section
        
        return context

class ChapterUpdateView(LoginRequiredMixin, UpdateView):
    model = Chapter
    template_name = 'content/chapter_edit.html'
    fields = ['title', 'order']
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_content_admin():
            messages.error(request, "У вас нет прав для редактирования этой главы.")
            return redirect('content:chapter_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('content:chapter_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.written_at = timezone.now()
        messages.success(self.request, "Глава успешно обновлена.")
        return super().form_valid(form)

class SectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Section
    template_name = 'content/section_edit.html'
    fields = ['title', 'order']
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_content_admin():
            messages.error(request, "У вас нет прав для редактирования этого раздела.")
            return redirect('content:section_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('content:section_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.written_at = timezone.now()
        messages.success(self.request, "Раздел успешно обновлен.")
        return super().form_valid(form)

class SubsectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Subsection
    template_name = 'content/subsection_edit.html'
    fields = ['title', 'order']
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user and not request.user.is_content_admin():
            messages.error(request, "У вас нет прав для редактирования этого подраздела.")
            return redirect('content:subsection_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('content:subsection_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.written_at = timezone.now()
        messages.success(self.request, "Подраздел успешно обновлен.")
        return super().form_valid(form)

class ChapterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        chapter = get_object_or_404(Chapter, pk=pk)
        
        # Check permissions
        if not request.user.is_content_admin() and not request.user.is_moderator():
            messages.error(request, "У вас нет прав для удаления главы.")
            return HttpResponseRedirect(reverse('content:chapter_detail', kwargs={'pk': pk}))
        
        chapter.is_deleted = True
        chapter.deleted_by = request.user
        chapter.save()
        
        messages.success(request, "Глава успешно удалена.")
        return HttpResponseRedirect(reverse('content:dashboard'))

class SectionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(Section, pk=pk)
        
        # Check permissions
        if not request.user.is_content_admin() and not request.user.is_moderator():
            messages.error(request, "У вас нет прав для удаления раздела.")
            return HttpResponseRedirect(reverse('content:section_detail', kwargs={'pk': pk}))
        
        section.is_deleted = True
        section.deleted_by = request.user
        section.save()
        
        messages.success(request, "Раздел успешно удален.")
        return HttpResponseRedirect(reverse('content:dashboard'))

class SubsectionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        subsection = get_object_or_404(Subsection, pk=pk)
        
        # Check permissions
        if not request.user.is_content_admin() and not request.user.is_moderator():
            messages.error(request, "У вас нет прав для удаления подраздела.")
            return HttpResponseRedirect(reverse('content:subsection_detail', kwargs={'pk': pk}))
        
        subsection.is_deleted = True
        subsection.deleted_by = request.user
        subsection.save()
        
        messages.success(request, "Подраздел успешно удален.")
        return HttpResponseRedirect(reverse('content:dashboard'))
