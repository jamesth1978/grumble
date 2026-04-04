from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings
from .models import Creator, Work
from .forms import CreatorForm, WorkForm
from .pdf import generate_certificate_pdf
import re
import random
import zipfile
import os
import io


def score_human_text(text: str) -> int:
    """Return a score from 0-100 estimating how likely text was written by a human."""
    text = (text or '').strip()
    if not text:
        return 0

    words = re.findall(r"\w+", text)
    word_count = len(words)
    unique_word_ratio = len(set(words)) / word_count if word_count else 0
    punctuation_count = len(re.findall(r"[!?]", text))

    score = 45

    if punctuation_count >= 1:
        score += 8

    if unique_word_ratio > 0.75:
        score += 10
    elif unique_word_ratio < 0.50:
        score -= 10

    human_clues = {
        'i', 'me', 'my', 'mine', 'you', 'we', 'us', 'our',
        'feel'
    }
    if any(word.lower() in human_clues for word in words):
        score += 10

    swear_stems = {
        'fuck', 'bollocks', 'shit', 'bugger', 'tits', 'damn', 'arse', 'wanker', 
        'piss', 'cunt', 'dick', 'bitch', 'areshole', 'twat'
    }

    # Count swear words including grammatical variations (plurals, -ing, -ed, etc.)
    swear_count = 0
    for word in words:
        word_lower = word.lower()
        for stem in swear_stems:
            # Match stem with optional common suffixes: s, es, ing, ed, er, y
            if re.match(rf'^{re.escape(stem)}(s|es|ing|ed|er|y)?$', word_lower):
                swear_count += 1
                break

    # Apply scoring based on swear count
    if swear_count >= 1:
        score += 25
        # Add random bonus for each additional swear word
        for _ in range(swear_count - 1):
            score += random.randint(4, 9)

    score = max(0, min(100, score))
    return score


def describe_human_score(score: int) -> tuple[str, str]:
    if score >= 85:
        return (
            'This text feels very human.',
            'Nice work — you have used some pretty human words there'
        )
    if score >= 65:
        return (
            'This text looks likely human.',
            'It has enough natural phrasing or swearing to feel authentic.'
        )
    if score >= 40:
        return (
            'This text is ambiguous.',
            'It may still be human, but it has a few patterns that could be either.'
        )
    return (
        'This text reads less like a human sentence.',
        'Definitely a robot.'
    )


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
            
            # Create work (automatically approved)
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


def download_badges(request):
    """Download both logo badges as a zip file"""
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add black logo
        black_logo_path = os.path.join(settings.STATIC_ROOT, 'black_trans_logo_big.png')
        if os.path.exists(black_logo_path):
            zip_file.write(black_logo_path, arcname='black_trans_logo_big.png')
        
        # Add white logo
        white_logo_path = os.path.join(settings.STATIC_ROOT, 'white_trans_logo_big.png')
        if os.path.exists(white_logo_path):
            zip_file.write(white_logo_path, arcname='white_trans_logo_big.png')
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="factum_humanum_badges.zip"'
    
    return response


def human_test(request):
    """Provide a playful text evaluation tool for human-written sentences."""
    sample_text = ''
    score = None
    verdict = None
    explanation = None

    if request.method == 'POST':
        sample_text = request.POST.get('sample_text', '').strip()
        score = score_human_text(sample_text)
        verdict, explanation = describe_human_score(score)

    context = {
        'title': 'Human Proof Test',
        'text': sample_text,
        'score': score,
        'verdict': verdict,
        'explanation': explanation,
    }
    return render(request, 'human_test.html', context)


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
