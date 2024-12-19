from django import forms
from random import choice
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

import markdown2
from . import util
from .util import markdown_to_html

class NewPageForm(forms.Form):
    title = forms.CharField(label="Page Title", max_length=100)
    content = forms.CharField(
        label="Content",
        widget=forms.Textarea(attrs={"rows": 10, "cols": 60})
    )
    
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry_page(request, title):
    entry = util.get_entry(title)
    if not entry:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' does not exist."
        })

    # Convert Markdown content to HTML
    html_content = markdown_to_html(entry)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return redirect("index")
    
    entries = util.list_entries()
    matching_entries = [entry for entry in entries if query.lower() in entry.lower()]
    
    # If exact match, redirect to the entry page
    if query.lower() in [entry.lower() for entry in entries]:
        return redirect("entry_page", title=query)
    
    # Otherwise, render the search results
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": matching_entries
    })

def create_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if the entry already exists
            if util.get_entry(title):
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "error_message": f"An entry with the title '{title}' already exists."
                })

            # Save the new entry
            util.save_entry(title, content)
            return redirect("entry_page", title=title)
    else:
        form = NewPageForm()

    return render(request, "encyclopedia/create.html", {"form": form})

def edit_page(request, title):
    entry = util.get_entry(title)

    if not entry:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' does not exist."
        })

    if request.method == "POST":
        # Save the edited content
        content = request.POST["content"]
        util.save_entry(title, content)
        return redirect("entry_page", title=title)

    # Render form pre-populated with existing content
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": entry
    })

def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries available."
        })
    random_title = choice(entries)
    return redirect("entry_page", title=random_title)
