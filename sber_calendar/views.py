from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from django.contrib.messages import constants as messages
from django.shortcuts import redirect
from sber_calendar.models import Profile
import json
from django.core.serializers import serialize
import os


def redirect_view(request):
    response = redirect('/dashboard/')
    return response


@login_required
def dashboard(request):
    user = request.user
    profile = Profile.objects.filter(user=user)[0]
    user = User.objects.filter(username=user.username)[0]
    user_events = []
    json_data = open('static/events.json', encoding='utf-8')
    data1 = json.load(json_data)
    colors = {'СМО': '#850000', 'ВМО': '#da9f00', 'МО': '#4a89db', 'СКМ': '#a589be', 'КМ': '#e88990', 'K': '#4ab465'}
    for d in data1['events']:
        position = d['position']
        sub_code = d['sub_code'].split('/')[0]
        address = d['address']
        date = d['date']
        if sub_code == profile.sub_code.split('/')[0]:
            if (position in ['СМО', 'ВМО', 'МО']) and (profile.position in ['СМО', 'ВМО', 'МО']):
                user_events.append({'title': f'{position} {d["sub_code"]} {address}', 'color': colors[position], 'start': date, 'end': date})
            elif (position in ['СКМ', 'КМ']) and (profile.position in ['СКМ', 'КМ']):
                user_events.append({'title': f'{position} {d["sub_code"]} {address}', 'color': colors[position], 'start': date, 'end': date})
            elif (position in ['К']) and (profile.position in ['К']):
                user_events.append({'title': f'{position} {d["sub_code"]} {address}', 'color': colors[position], 'start': date, 'end': date})
    json_events = json.dumps(user_events)
    print(json_events)
    return render(request, 'dashboard.html', {'section': 'dashboard', 'user': user, 'profile': profile, 'events': json_events})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


class SignUpView(generic.TemplateView):
    template_name = 'registration/signup.html'

    def get(self, request):
        user_form = UserForm
        profile_form = ProfileForm
        success_url = reverse_lazy('login')
        context = self.get_context_data()
        context['u_form'] = user_form
        context['p_form'] = profile_form
        return self.render_to_response(context)

    def post(self, request):
        if request.method == "POST":
            u_form = UserForm(request.POST)
            p_form = ProfileForm(request.POST)
            if u_form.is_valid() and p_form.is_valid():
                user = u_form.save()
                p_form = p_form.save(commit=False)
                p_form.user = user
                p_form.save()
                # messages.success(request, f'Registration complete! You may log in!')
                return redirect('login')
            else:
                return HttpResponse('Пароль должен совпадать с проверочным паролем, и содержать цифры и буквы рызных регистров')
        else:
            u_form = UserForm(request.POST)
            p_form = ProfileForm(request.POST)
        return render(request, 'registration/signup.html', {'u_form': u_form, 'p_form': p_form})


def register(request):
    if request.method == "POST":
        u_form = UserForm(request.POST)
        p_form = ProfileForm(request.POST)
        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()
            p_form = p_form.save(commit=False)
            p_form.user = user
            p_form.save()
            messages.success(request, f'Registration complete! You may log in!')
            return redirect('login')
    else:
        u_form = UserForm(request.POST)
        p_form = ProfileForm(request.POST)
    return render(request, 'users/register.html', {'u_form': u_form, 'p_form': p_form})

