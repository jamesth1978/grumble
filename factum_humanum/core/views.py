from django.shortcuts import render

def index(request):
    context = {
        "title": "Django example",
    }
    return render(request, "index.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import Creator, Work
from .forms import CreatorForm, WorkForm
from .pdf import generate_certificate_pdf


def index(request):
    works = Work.objects.select_related('creator').all()[:10]
    context = {
        "title": "Created by Humans - Work Registration",
        "works": works,
    }
    return render(request, "index.html", context)


@require_http_methods(["GET", "POST"])
def register_work(request):
    """Handle work registration with creator information"""
    if request.method == 'POST':
        creator_form = CreatorForm(request.POST)
        work_form = WorkForm(request.POST)
        
        if creator_form.is_valid() and work_form.is_valid():
            # Get or create creator
            creator, created = Creator.objects.get_or_create(
                email=creator_form.cleaned_data['email'],
                defaults={'name': creator_form.cleaned_data['name']}
            )
            
            # Create work
            work = work_form.save(commit=False)
            work.creator = creator
            work.save()
            
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
    }
    return render(request, 'certificate.html', context)


def download_certificate(request, work_id):
    """Generate and download PDF certificate"""
    work = get_object_or_404(Work, id=work_id)
    
    pdf_buffer = generate_certificate_pdf(work)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{work.id}.pdf"'
    
    return response
