from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib import auth
import openai

from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
from django.contrib.auth.decorators import login_required

openai_api_key = 'Your_openai_api_key'
openai.api_key = openai_api_key

# Create your views here.
def welcome(request):
    # return render(request,'welcome-page.html')
    return render(request,'chatbot.html')

def login(request):
    if request.method =="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = "Invalid username or password"
            return render(request=request, template_name='login.html',context={'error_message':error_message})

    else:    
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username=username,email=email,password=password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = "Error occurred while signing up"
                return render(request, 'register.html',{'error_message':error_message})
        else:
            error_message = "Password doesn't match"
        return render(request, 'register.html',{'error_message':error_message})

    return render(request, 'register.html')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required
def ask_openai(message):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":message}]
    )
    answer = response.choices[0].message.content
    return answer

@login_required
def chatbot(request):
    chats = Chat.objects.filter(user = request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user = request.user, message = message, response = response, created_at = timezone.now())
        chat.save()
        return JsonResponse({'message':message, 'response':response})
    return render(request=request,template_name='chatbot.html',context={'chats':chats})

