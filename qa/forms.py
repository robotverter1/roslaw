from django import forms

class QuestionAnswerForm(forms.Form):
    question = forms.CharField(label='Вопрос', max_length=500)
    answer = forms.CharField(label='Ответ', widget=forms.Textarea)
    links = forms.CharField(label='Ссылки', required=False, widget=forms.Textarea(attrs={'placeholder': 'Одна ссылка на строку'}))
    copies = forms.ChoiceField(label='Количество копий', choices=[(1, '1'), (2, '2'), (3, '3')])
    category = forms.CharField(label='Категория', max_length=100)
