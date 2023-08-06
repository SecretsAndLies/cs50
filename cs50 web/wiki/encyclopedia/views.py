from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.http import HttpResponseRedirect
from markdown2 import markdown

from . import util
from random import choice


class NewArticleForm(forms.Form):
    title = forms.CharField(label="Article Title")
    content = forms.CharField(label="Article Text", widget=forms.Textarea)


class EditArticleForm(forms.Form):
    content = forms.CharField(label="Article Text", widget=forms.Textarea)


def index(request):
    if "q" in request.GET:
        query = request.GET["q"].lower()
        lowerEntries = [x.lower() for x in util.list_entries()]
        if query in lowerEntries:
            return render(request, "encyclopedia/article.html",
                          {
                              "title": query,
                              "text": markdown(util.get_entry(query))
                          }
                          )

        # check for substring matches
        matchingItems = []
        for entry in lowerEntries:
            if query in entry:
                matchingItems.append(entry)

        if matchingItems:
            return render(request, "encyclopedia/results.html", {
                "entries": matchingItems
            })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def article(request, title):
    text = util.get_entry(title)
    if text:
        return render(request, "encyclopedia/article.html",
                      {
                          "title": title,
                          "text": markdown(text),
                          "rawText": text
                      }
                      )
    return render(request, "encyclopedia/error.html",
                  {
                      "error_message": "Page Not Found",
                  }
                  )


def random(request):
    title = choice(util.list_entries())
    return HttpResponseRedirect(f"wiki/{title}")


def edit(request):
    # pre populate the form with existing content
    if request.method == "GET":
        title = request.GET["title"]
        text = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": text
        })

    # form has been submitted
    if request.method == "POST":
        title = request.POST["title"]
        newText = request.POST["newContent"]

        util.save_entry(title, newText)

        return HttpResponseRedirect(f"wiki/{title}")


def new(request):

    # Check if method is POST
    if request.method == "POST":
        form = NewArticleForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title not in util.list_entries():
                util.save_entry(title, content)

                return HttpResponseRedirect(f"wiki/{title}")
            else:
                return render(request, "encyclopedia/error.html",
                              {
                                  "error_message": "Page Already Exists",
                              }
                              )
        else:

            # If the form is invalid, re-render the page with existing information.
            return render(request, "new.html", {
                "form": form
            })

    return render(request, "encyclopedia/new.html", {
        "form": NewArticleForm()
    })
