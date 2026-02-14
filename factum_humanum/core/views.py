from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Creator, Work
from .forms import CreatorForm, WorkForm
from .pdf import generate_certificate_pdf


def index(request):
    """Display homepage with latest registered works"""
    latest_works = Work.objects.select_related('creator').all()[:12]
    context = {
        "title": "Factum Humanum - Register Your Human-Created Work",
        "works": latest_works,
    }
    return render(request, "index.html", context)


@require_http_methods(["GET", "POST"])
def register_work(request):
    """Handle work registration with creator information"""
    if request.method == 'POST':
        creator_form = CreatorForm(request.POST)
        work_form = WorkForm(request.POST, request.FILES)
        
        if creator_form.is_valid() and work_form.is_valid():
            # Get or create creator
            creator, created = Creator.objects.get_or_create(
                email=creator_form.cleaned_data['email'],
                defaults={'name': creator_form.cleaned_data['name']}
            )
            
            # Check if creator has credits
            if not creator.has_credits():
                return redirect('buy_credits') + f'?email={creator.email}'
            
            # Create work (automatically approved)
            work = work_form.save(commit=False)
            work.creator = creator
            work.save()
            
            # Deduct one credit
            creator.credits -= 1
            creator.save()
            
            return redirect('certificate', work_id=work.id)
    else:
        creator_form = CreatorForm()
        work_form = WorkForm()
    
    context = {
        'creator_form': creator_form,
        'work_form': work_form,
    }
    return render(request, 'register.html', context)


def certificate(request, work_id):
    """Display certificate details and allow PDF download"""
    work = get_object_or_404(Work, id=work_id)
    context = {
        'work': work,
        'registration_id': str(work.id),
    }
    return render(request, 'certificate.html', context)


def download_certificate(request, work_id):
    """Generate and download PDF certificate"""
    work = get_object_or_404(Work, id=work_id)
    
    pdf_buffer = generate_certificate_pdf(work)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{work.id}.pdf"'
    
    return response


def search_registry(request):
    """Search and browse the public registry of registered works"""
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    
    # Start with all works
    works = Work.objects.select_related('creator').all()
    
    # Apply search query
    if query:
        works = works.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(creator__name__icontains=query)
        )
    
    # Apply category filter
    if category_filter:
        works = works.filter(category=category_filter)
    
    # Get category choices for filter dropdown
    category_choices = Work.CATEGORY_CHOICES
    
    # Count results
    total_count = works.count()
    
    # Paginate results (show 20 per page)
    from django.core.paginator import Paginator
    paginator = Paginator(works, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'category_filter': category_filter,
        'category_choices': category_choices,
        'total_count': total_count,
    }
    return render(request, 'search_registry.html', context)


def about(request):
    """Display information about Factum Humanum"""
    context = {
        'title': 'About Factum Humanum',
    }
    return render(request, 'about.html', context)
