from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import QuestionAnswerForm

@login_required
def create_question_answer(request):
    user = request.user
    if getattr(user, 'role', None) in ['volunteer', 'blocked']:
        return render(request, 'qa/no_permission.html')
    if request.method == 'POST':
        form = QuestionAnswerForm(request.POST)
        if form.is_valid():
            # ...логика сохранения...
            return redirect('qa:create_question_answer')
    else:
        form = QuestionAnswerForm()
    return render(request, 'qa/create_question_answer.html', {'form': form})
