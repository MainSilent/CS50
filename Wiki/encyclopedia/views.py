from django.shortcuts import render
import markdown2
from . import util
from random import randint
from .forms import AddForm, EditForm
from django.shortcuts import redirect, HttpResponse

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if util.get_entry(title) == None:
        return render(request, "encyclopedia/index.html", {
            "error": "404 Not Found"
        })
    else:
        return render(request, "encyclopedia/index.html", {
            "title": title,
            "entry": markdown2.markdown(util.get_entry(title))
        })

def random(request):
    entries = util.list_entries()
    random_entry = entries[randint(0, len(entries)) - 1]
    return render(request, "encyclopedia/index.html", {
        "title": random_entry,
        "entry": markdown2.markdown(util.get_entry(random_entry))
    })

def add(request):
    if request.method == "POST":
        form = AddForm(request.POST)
        if util.get_entry(form.data['title']) != None:
            return render(request, "encyclopedia/add.html", {
                "form": AddForm(),
                "error": "An entry with this title already exists"
            })
        else:
            util.save_entry(form.data['title'], form.data['content'])
            return redirect('/wiki/'+form.data['title'])
    else:
        return render(request, "encyclopedia/add.html", {
            "form": AddForm()
        })

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        util.save_entry(title, form.data['content'])
        return redirect('/wiki/'+title)
    else:
        return render(request, "encyclopedia/add.html", {
            "title": title,
            "form": EditForm(initial={'content': util.get_entry(title)})
        })

def search(request):
    q = request.GET.get('q')
    possible = [entry for entry in util.list_entries() if q.lower() in entry.lower()] 
    if util.get_entry(q) != None:
        return entry(request, q)
    elif len(possible) != 0:
        return render(request, "encyclopedia/index.html", {
            "entries": possible
        })
    else:
        return entry(request, None)