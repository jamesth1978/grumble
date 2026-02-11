"""Email sending functions for factum humanum"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_work_received_email(work):
    """Send confirmation email that work has been received and is under review"""
    subject = f"Your work '{work.title}' has been received"
    
    context = {
        'creator_name': work.creator.name,
        'work_title': work.title,
        'work_id': work.id,
    }
    
    html_message = render_to_string('email/work_received.html', context)
    plain_message = f"""
Hello {work.creator.name},

Thank you for registering your work '{work.title}' with Factum Humanum.

Your work has been received and is now under review. Our team will verify that it is likely to have been created by humans rather than AI.

A certificate will be issued once the review is complete. You will receive another email with your certificate.

If you have any questions, please reply to this email.

Best regards,
The Factum Humanum Team
"""
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [work.creator.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_certificate_approved_email(work):
    """Send email with certificate when work is approved"""
    subject = f"Your certificate for '{work.title}' is ready"
    
    context = {
        'creator_name': work.creator.name,
        'work_title': work.title,
        'work_id': work.id,
        'certificate_url': f"{settings.SITE_URL}/certificate/{work.id}/",
    }
    
    html_message = render_to_string('email/certificate_approved.html', context)
    plain_message = f"""
Hello {work.creator.name},

Congratulations! Your work '{work.title}' has been approved and your certificate is ready.

You can view and download your certificate at:
{settings.SITE_URL}/certificate/{work.id}/

Your certificate certifies that '{work.title}' was reviewed and approved as likely human-created by the Factum Humanum team.

Thank you for registering with us!

Best regards,
The Factum Humanum Team
"""
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [work.creator.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_certificate_rejected_email(work):
    """Send email with rejection reason when work is rejected"""
    subject = f"Update on your submission '{work.title}'"
    
    context = {
        'creator_name': work.creator.name,
        'work_title': work.title,
        'reviewer_notes': work.reviewer_notes,
    }
    
    html_message = render_to_string('email/certificate_rejected.html', context)
    plain_message = f"""
Hello {work.creator.name},

Thank you for submitting '{work.title}' to Factum Humanum.

After review, we were unable to approve this work at this time. Here are the notes from our review team:

{work.reviewer_notes}

You are welcome to resubmit your work with any modifications or additional documentation.

Best regards,
The Factum Humanum Team
"""
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [work.creator.email],
        html_message=html_message,
        fail_silently=False,
    )
