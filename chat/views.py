from django.shortcuts import render

from chat.models import Message


def index(request):
    messages = Message.objects.values()
    context = {'messages': list(messages)}
    return render(request, 'index.html', context)
