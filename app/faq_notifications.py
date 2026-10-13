"""Notification interne du coach : aucun token personnel ni questionnaire complet."""
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo
import os


def render_admin_notification(row, public_url):
    result = row['result']
    email = row['email']
    zone = ZoneInfo(os.environ.get('FAQ_NOTIFICATION_TIMEZONE', 'Asia/Dubai'))
    completed = datetime.fromtimestamp(row['completed_at'], zone)
    date = completed.strftime('%d/%m/%Y à %H:%M') + ' (' + str(zone) + ')'
    scores = ''.join(
        '<tr><td style="padding:11px 0;border-bottom:1px solid #d9dccf;font:14px Arial,sans-serif;">'
        + escape(category) + '</td><td align="right" style="padding:11px 0;border-bottom:1px solid #d9dccf;font:700 16px Arial,sans-serif;">'
        + str(value['score']) + '/' + str(value['total']) + '</td></tr>'
        for category,value in result['categories'].items())
    consent = ('Contenus et offres demandés ; confirmation par mail encore nécessaire.'
               if row['newsletter'] else 'Pas de demande d’inscription aux contenus et offres.')
    body = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;background:#f5f3eb;color:#171916;font-family:Arial,Helvetica,sans-serif;"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:24px 14px;"><table role="presentation" width="560" cellspacing="0" cellpadding="0" style="width:100%;max-width:560px;background:#fffef9;border:1px solid #d9dccf;"><tr><td style="padding:28px 24px;"><p style="font:900 23px Arial,sans-serif;margin:0 0 28px;">ACHZOD.</p><p style="font:700 11px Arial,sans-serif;letter-spacing:1px;color:#236347;margin:0 0 15px;">FAQ LAB / NOUVEAU QUIZ TERMINÉ</p><h1 style="font:900 31px/1.15 Arial,sans-serif;letter-spacing:-1px;margin:0 0 20px;">Une nouvelle participation.<br>{result['score']}/{result['total']} au quiz.</h1><p style="font:15px/1.7 Arial,sans-serif;margin:0 0 18px;"><b>Participant :</b><br><a href="mailto:{escape(email,quote=True)}" style="color:#171916;overflow-wrap:anywhere;word-break:break-all;">{escape(email)}</a></p><p style="font:13px/1.6 Arial,sans-serif;color:#64685e;margin:0 0 22px;">Terminé le {escape(date)}.<br>Quiz : métabolisme, biomécanique, nutrition et compléments.</p><table role="presentation" width="100%" cellspacing="0" cellpadding="0">{scores}</table><p style="font:13px/1.7 Arial,sans-serif;color:#64685e;margin:22px 0;">{escape(consent)}<br>La participation est enregistrée en base. Le corrigé du participant est traité dans une file séparée ; cette notification n’en garantit pas à elle seule la remise.</p><a href="{escape(public_url.rstrip('/')+'/faq',quote=True)}" style="display:inline-block;padding:14px 22px;background:#f1d548;color:#171916;font:700 14px Arial,sans-serif;text-decoration:none;">Ouvrir le quiz →</a><p style="font:12px/1.6 Arial,sans-serif;color:#64685e;margin:24px 0 0;">Notification interne du coach. Une seule par participation validée. Aucun mail de test QA n’est notifié automatiquement.</p></td></tr></table></td></tr></table></body></html>'''
    text = [f"Nouveau quiz terminé : {result['score']}/{result['total']}",
            'Participant : ' + email, 'Terminé le ' + date, '']
    text.extend(f"{category} : {value['score']}/{value['total']}" for category,value in result['categories'].items())
    text.extend(['',consent,'Le corrigé du participant est traité séparément.',public_url.rstrip('/')+'/faq'])
    return {'subject':f"Quiz terminé · {result['score']}/{result['total']} · {email}",
            'html':body,'text':'\n'.join(text)}
