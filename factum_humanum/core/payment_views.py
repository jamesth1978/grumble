"""Stripe payment handling views"""
import json
try:
    import stripe
except ImportError:
    stripe = None
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Creator, Payment

# Initialize Stripe only if available
if stripe:
    stripe.api_key = settings.STRIPE_SECRET_KEY


@require_http_methods(["GET", "POST"])
def buy_credits(request):
    """Display purchase page and handle checkout"""
    if not stripe:
        return JsonResponse({'error': 'Payment system not configured'}, status=500)
    
    email = request.GET.get('email', '') or request.POST.get('email', '')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            return render(request, 'buy_credits.html', {
                'error': 'Please enter a valid email address',
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
        
        try:
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': settings.STRIPE_PRODUCT_PRICE_ID,
                        'quantity': 1,
                    }
                ],
                mode='payment',
                customer_email=email,
                metadata={'email': email, 'credits': 5},
                success_url=f"{settings.SITE_URL}/credits/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.SITE_URL}/credits/cancel/",
            )
            
            return redirect(session.url, code=303)
        except Exception as e:
            print(f"Stripe session creation failed: {e}")
            return render(request, 'buy_credits.html', {
                'error': f'Payment error: {str(e)}',
                'email': email,
                'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
    
    return render(request, 'buy_credits.html', {
        'email': email,
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_http_methods(["GET"])
def checkout_success(request):
    """Handle successful checkout"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return render(request, 'checkout_status.html', {
            'success': False,
            'message': 'No session ID provided',
        })
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Check if payment was successful
        if session.payment_status == 'paid':
            email = session.metadata.get('email', session.customer_email)
            
            # Check if payment already processed
            payment = Payment.objects.filter(stripe_session_id=session_id).first()
            if payment:
                if payment.fulfilled:
                    return render(request, 'checkout_status.html', {
                        'success': True,
                        'message': f'Payment already processed! {payment.credits_granted} credits added to {email}.',
                        'credits': payment.credits_granted,
                    })
            else:
                # Create or get creator
                creator, created = Creator.objects.get_or_create(
                    email=email,
                    defaults={'name': email.split('@')[0]}  # Use first part of email as name
                )
                
                # Get charge info for amount
                charge_id = session.payment_intent  # or retrieve from intent
                
                # Create payment record
                payment = Payment.objects.create(
                    creator=creator,
                    email=email,
                    stripe_charge_id=charge_id,
                    stripe_session_id=session_id,
                    amount_cents=200,  # £2 = 200 pence
                    currency='GBP',
                    credits_granted=5,
                    fulfilled=True,
                    fulfilled_at=timezone.now(),
                )
                
                # Add credits to creator
                creator.credits += 5
                creator.save()
                
                return render(request, 'checkout_status.html', {
                    'success': True,
                    'message': f'Payment successful! 5 credits added to your account.',
                    'email': email,
                    'credits': 5,
                })
        
        return render(request, 'checkout_status.html', {
            'success': False,
            'message': 'Payment was not completed. Please try again.',
        })
    except Exception as e:
        print(f"Checkout success handling failed: {e}")
        return render(request, 'checkout_status.html', {
            'success': False,
            'message': f'Error processing payment: {str(e)}',
        })


@require_http_methods(["GET"])
def checkout_cancel(request):
    """Handle cancelled checkout"""
    return render(request, 'checkout_status.html', {
        'success': False,
        'message': 'Payment cancelled. Please try again when ready.',
    })


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=403)
    
    # Handle checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.metadata.get('email', session.customer_email)
        
        # Check if already processed
        payment = Payment.objects.filter(stripe_session_id=session.id).first()
        if payment:
            if payment.fulfilled:
                return HttpResponse(status=200)
        
        try:
            # Create or get creator
            creator, created = Creator.objects.get_or_create(
                email=email,
                defaults={'name': email.split('@')[0]}
            )
            
            # Create payment record if not exists
            if not payment:
                payment = Payment.objects.create(
                    creator=creator,
                    email=email,
                    stripe_charge_id=session.payment_intent,
                    stripe_session_id=session.id,
                    amount_cents=200,  # £2
                    currency='GBP',
                    credits_granted=5,
                    fulfilled=True,
                    fulfilled_at=timezone.now(),
                )
            
            # Add credits if not already added
            if not payment.fulfilled:
                creator.credits += 5
                creator.save()
                payment.fulfilled = True
                payment.fulfilled_at = timezone.now()
                payment.save()
        
        except Exception as e:
            print(f"Webhook processing error: {e}")
            return HttpResponse(status=500)
    
    return HttpResponse(status=200)
