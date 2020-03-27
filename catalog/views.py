from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.decorators import (
    login_required,
)  # for function based views
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)  # for class based views
from django.contrib.auth.mixins import PermissionRequiredMixin


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
    num_visits = request.session.get("num_visits", 1)
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


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    pagenate_by = 5


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


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
    """Generic class-based view listing books on loan, viewable only by permission."""

    model = BookInstance
    permission_required = "catalog.can_mark_retured"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by(
            "due_back"
        )


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
