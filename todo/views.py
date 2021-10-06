# Import Django Libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# HomePage from where you can Login and SignUp
def home(request):
    return render(request, 'todo/home.html')


# Sign Up New User
def signupuser(request):
    if request.method == 'GET':
        return render (request, "todo/signupuser.html", {"forms":UserCreationForm()})
    else:
        # Create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodo')
            except IntegrityError:
                return render (request, "todo/signupuser.html", {"forms":UserCreationForm(), 'error':'Username already in exist'})
        else:
            # Tell the user password did not match
            return render (request, "todo/signupuser.html", {"forms":UserCreationForm(), 'error':'Password did not match not match'})


# Login User
def loginuser(request):
    if request.method == 'GET':
        return render (request, "todo/loginuser.html", {"forms":AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render (request, "todo/loginuser.html", {"forms":AuthenticationForm(), 'error':'Username and Password did not match'})
        else:
            login(request, user)
            return redirect('currenttodo')


# Logout the User
@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


# List all your Todo Entries from where you can update, delete and create new todo
@login_required
def currenttodo(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render (request, "todo/currenttodo.html", {'todos': todos})


# Completed Todo Page
@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render (request, "todo/completedtodo.html", {'todos': todos})


# Create New Todo
@login_required
def createtodo(request):
    if request.method == 'GET':
        return render (request, "todo/createtodo.html", {"forms" : TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render (request, "todo/createtodo.html", {"forms" : TodoForm(), 'error': 'Bad Data Entry.Try Again'})


# Update existing Todo entries
@login_required
def updatetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance = todo)
        return render (request, "todo/updatetodo.html", {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render (request, "todo/updatetodo.html", {'todo': todo, 'form': form, 'error': 'Bad Info'})


# Mark the todo as Completed
@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodo')


# Delete the Todo ftom List
@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')