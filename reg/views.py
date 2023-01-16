from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import SighUpForm
from datetime import date
from .models import usersSub,subPlan


# Create your views here.
def sign_up(request):
    form = SighUpForm
    registered = False
    if request.method == 'POST':
        form = SighUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            registered = True
    dict = {'form':form, 'registered':registered}
    return render(request,'reg/signup.html',context=dict)


def login_page(request):
    form = AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse('home'))

    return render(request,'reg/login.html',context={'form':form})

@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def home(request):
    userSub=[]
    if request.user.is_authenticated():
        userSub = usersSub.objects.filter(user=request.user)
    subsPlan = subPlan.objects.all()
    subscribed=False
    can_pur_new_sub=True
    if userSub.exists():
        #This variable is for tracking monthly subscription
        subscribed=True
        D_now=date.today()
        compareM = D_now-date(userSub[0].subscribeY,userSub[0].subscribeM,userSub[0].subscribeD)
        if compareM.days == 30:
            subscribed = False

        #This variable is for tracking if a user can purchase a new subscription or not
        can_pur_new_sub=False
        if userSub.subP.title=="Globalnet Gold":
            can_pur_new_sub=True
        else:
            compareY= D_now-date(userSub[0].subscribeY,userSub[0].subscribeM,userSub[0].subscribeD)
            if compareY.days == 365:
                can_pur_new_sub = True
    return render(request,'home.html',context={'userSub':userSub,'subPlan':subsPlan,'subscribed':subscribed,'can_pur_new_sub':can_pur_new_sub})