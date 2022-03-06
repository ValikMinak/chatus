from django.shortcuts import render

from chat.models import Message


def index(request):
    messages = list(Message.objects.values().order_by('-id')[:150])
    messages.reverse()
    context = {'messages': messages}
    return render(request, 'index.html', context)
