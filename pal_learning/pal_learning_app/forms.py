from django import forms
from .models import Course,Module,Lesson,Quiz,Question, Choice
from django.forms import inlineformset_factory
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'topic', 'difficulty']
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'sort_order']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content_type', 'content_url', 'body', 'sort_order']
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']
        
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=('text', 'is_correct'),
    extra=4,
    can_delete=True
)