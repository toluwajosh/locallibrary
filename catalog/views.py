import datetime

from django.contrib.auth.decorators import (
    login_required,
)  # for function based views
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (  # for class based views
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from catalog.forms import RenewBookForm
from catalog.models import Author, Book, BookInstance, Genre


# Create your views here.
@login_required
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact="a"
    ).count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # num_genres = Genre.objects.filter(
    #   name__contains='science').count()

    num_genres = Genre.objects.count()

    # Number of visits to this view, as counted in the session variable.
    # return 0 if `num_visits` does not exist yet
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_visits": num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = "__all__"
    permission_required = "catalog.can_mark_returned"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.can_mark_returned"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.can_mark_returned"


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = "__all__"
    permission_required = "catalog.can_mark_returned"


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = "__all__"
    permission_required = "catalog.can_mark_returned"


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = "catalog.can_mark_returned"


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    pagenate_by = 5


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    permission_required = "catalog.can_mark_returned"

    context = {
        "authore": model,
        "author_update": AuthorUpdate,
        "author_delete": AuthorDelete,
    }


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(book_borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan,
    viewable only by permission."""

    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by(
            "due_back"
        )


@permission_required("catalog.can_mark_returned")
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and
        # populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("all-borrowed"))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(
            weeks=3
        )
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


# class BookListView(generic.ListView):
#     model = Book
#     # your own name for the list as a template variable
#     context_object_name = 'my_book_list'
#     queryset = Book.objects.filter(title__icontains='war')[
#         :5]  # Get 5 books containing the title war
#     # Specify your own template name/location
#     template_name = 'books/my_arbitrary_template_name_list.html'
#     def get_queryset(self):
#        return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
#     def get_context_data(self, **kwargs):
# # Call the base implementation first to get the context
# context = super(BookListView, self).get_context_data(**kwargs)
# # Create any data and add it to the context
# context['some_data'] = 'This is just some data'
# return context
