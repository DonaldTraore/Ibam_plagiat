"""
Module pour l'envoi d'emails.
"""
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_notification_email(notification):
    """
    Envoie une notification par email.
    """
    if not notification.user.email:
        return False
    
    subject = notification.titre
    message = notification.message
    
    # Contexte pour le template
    context = {
        'user': notification.user,
        'notification': notification,
        'site_name': 'Système de Détection de Plagiat - IBAM',
    }
    
    # Rendre le template HTML
    html_message = render_to_string('emails/notification.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Marquer comme envoyé
        from django.utils import timezone
        notification.email_envoye = True
        notification.date_envoi_email = timezone.now()
        notification.save()
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False


def send_welcome_email(user):
    """
    Envoie un email de bienvenue à un nouvel utilisateur.
    """
    if not user.email:
        return False
    
    subject = 'Bienvenue sur le Système de Détection de Plagiat - IBAM'
    
    context = {
        'user': user,
        'site_name': 'Système de Détection de Plagiat - IBAM',
    }
    
    html_message = render_to_string('emails/welcome.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de bienvenue: {e}")
        return False


def send_rapport_valide_email(rapport):
    """
    Envoie un email de confirmation lorsqu'un rapport est validé.
    """
    etudiant = rapport.etudiant
    
    if not etudiant.email:
        return False
    
    subject = f'Votre rapport "{rapport.titre}" a été validé'
    
    context = {
        'etudiant': etudiant,
        'rapport': rapport,
        'site_name': 'Système de Détection de Plagiat - IBAM',
    }
    
    html_message = render_to_string('emails/rapport_valide.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[etudiant.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de validation: {e}")
        return False


def send_rapport_rejete_email(rapport, avec_pdf=False):
    """
    Envoie un email de notification lorsqu'un rapport est rejeté.
    Optionnellement avec un PDF signé.
    """
    etudiant = rapport.etudiant
    
    if not etudiant.email:
        return False
    
    subject = f'Votre rapport "{rapport.titre}" a été rejeté'
    
    context = {
        'etudiant': etudiant,
        'rapport': rapport,
        'motif_rejet': rapport.motif_rejet,
        'rejete_par': rapport.rejete_par,
        'site_name': 'Système de Détection de Plagiat - IBAM',
    }
    
    html_message = render_to_string('emails/rapport_rejete.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[etudiant.email],
        )
        email.content_subtype = 'html'
        
        # Attacher le PDF signé si disponible
        if avec_pdf and rapport.pdf_signe:
            email.attach_file(rapport.pdf_signe.path)
        
        email.send()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de rejet: {e}")
        return False
