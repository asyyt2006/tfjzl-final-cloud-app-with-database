from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = get_object_or_404(Enrollment, course=course, user=user)
    
    if request.method == 'POST':
        selected_choice_ids = [int(choice_id) for choice_id in request.POST.getlist('choice')]
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_choice_ids)
        submission.save()
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    return redirect('onlinecourse:course_details', course_id=course.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]
    
    total_score = 0
    total_possible = 0
    
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_possible += question.grade
            if question.is_get_score(selected_ids):
                total_score += question.grade
                
    grade_percentage = int((total_score / total_possible) * 100) if total_possible > 0 else 0
    
    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': grade_percentage,
        'submission': submission,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
