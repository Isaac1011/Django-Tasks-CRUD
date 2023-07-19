from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            "form": UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Usamos el try-except por si la DB falla que no se muera la app
            try:
                # se crea el usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                # se guarda el usuario en la DB
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                render(request, 'signup.html', {
                    "form": UserCreationForm,
                    "error": 'User already exists'
                })

        return render(request, 'signup.html', {
            "form": UserCreationForm,
            "error": 'Password do not match'
        })

@login_required
def tasks(request):
    # Tomamos las tasks del usuario que está logeado
    # tasks = Task.objects.filter(user=request.user)

    # Para las tareas completadas
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    # Tomamos las tasks del usuario que está logeado
    # tasks = Task.objects.filter(user=request.user)

    # Para las tareas no completadas
    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            # Actualizamos la task                      esto de user es para actulizar las tareas propias y no de otros usuarios
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error updating task'
            })

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)  # Esto es un objeto
            new_task.user = request.user  # El usuario que creó la tarea
            new_task.save()
            return redirect(tasks)
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid data'
            })

@login_required
def complete_task(request, task_id):
    # lo buscamos en la db
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        # actualizamos
        task.datecompleted = timezone.now()
        # guardamos
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    # lo buscamos en la db
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        # eliminamos
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or Password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')
