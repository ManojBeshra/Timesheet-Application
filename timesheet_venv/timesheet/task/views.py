from django.shortcuts import render

# Create your views here.

def task(request):
    return render(request, 'task.html')

def taskdetails(request):
    return render(request, 'taskdetails.html')

