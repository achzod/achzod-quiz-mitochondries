"""
Module d'envoi d'emails pour les résultats du quiz Mitochondries
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Configuration Gmail SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL = os.getenv("MAIL_USER", "coaching@achzodcoaching.com")
FROM_PASSWORD = os.getenv("MAIL_PASS", "ydqynezgfaxpaehj")
FROM_NAME = "Achzod - Quiz Mitochondries"


def send_quiz_results(email: str, score: int, total: int, percentage: float, results: List[Dict]) -> bool:
    """
    Envoie l'email avec les résultats du quiz et les corrections
    """
    try:
        # Création du message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = f"🎯 Tes résultats : {score}/{total} ({percentage:.0f}%) - Quiz Mitochondries Achzod"

        # Génération du HTML
        html_content = generate_results_email_html(score, total, percentage, results)

        # Ajout du contenu HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # Envoi de l'email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)

        logger.info(f"[EMAIL SENT] Quiz results sent to {email}")
        return True

    except Exception as e:
        logger.error(f"[EMAIL ERROR] Failed to send quiz results to {email}: {str(e)}")
        return False


def generate_results_email_html(score: int, total: int, percentage: float, results: List[Dict]) -> str:
    """
    Génère le HTML de l'email avec les résultats et corrections
    """

    # Calcul des statistiques
    wrong_answers = [r for r in results if not r["is_correct"]]

    # Message personnalisé selon le score
    if percentage >= 90:
        performance_message = "🏆 <strong>EXCEPTIONNEL !</strong> Tu maîtrises parfaitement les concepts de l'optimisation mitochondriale et de la performance."
        performance_color = "#8DFFE0"
    elif percentage >= 75:
        performance_message = "🎯 <strong>EXCELLENT !</strong> Tu as une très bonne compréhension des principes d'optimisation de la performance."
        performance_color = "#9990EA"
    elif percentage >= 60:
        performance_message = "👍 <strong>BIEN !</strong> Tu as de bonnes bases, quelques révisions sur certains concepts et tu seras au top."
        performance_color = "#9990EA"
    elif percentage >= 50:
        performance_message = "📚 <strong>CORRECT.</strong> Continue à approfondir tes connaissances pour maîtriser tous les concepts."
        performance_color = "#666666"
    else:
        performance_message = "💪 <strong>À AMÉLIORER.</strong> Revois les concepts clés et refais le quiz. Tu vas progresser !"
        performance_color = "#666666"

    # Génération des corrections
    corrections_html = ""
    if wrong_answers:
        corrections_html = "<h2 style='font-family: Eurostile, Arial Black, sans-serif; color: #101010; font-size: 24px; margin: 40px 0 20px 0; text-transform: uppercase; border-left: 6px solid #9990EA; padding-left: 15px;'>📝 TES CORRECTIONS</h2>"

        for idx, result in enumerate(wrong_answers, 1):
            question_html = f"""
            <div style="background: #FFFFFF; border: 3px solid #101010; padding: 25px; margin-bottom: 25px;">
                <div style="font-family: Eurostile, Arial Black, sans-serif; color: #9990EA; font-size: 16px; margin-bottom: 10px; font-weight: bold;">
                    QUESTION {result['question_id']}
                </div>
                <div style="font-family: Proxima Nova, Arial, sans-serif; color: #101010; font-size: 17px; font-weight: bold; margin-bottom: 15px; line-height: 1.5;">
                    {result['question']}
                </div>
                <div style="margin: 15px 0;">
                    <div style="background: #FFE5E5; border: 2px solid #FF4444; padding: 12px; margin-bottom: 10px; border-radius: 0;">
                        <strong style="color: #FF4444;">❌ Ta réponse :</strong> <span style="font-family: Proxima Nova, Arial, sans-serif; color: #101010;">{result['options'][result['user_answer']] if result['user_answer'] >= 0 else "Pas de réponse"}</span>
                    </div>
                    <div style="background: #E5FFE5; border: 2px solid #44FF44; padding: 12px; border-radius: 0;">
                        <strong style="color: #008800;">✓ Bonne réponse :</strong> <span style="font-family: Proxima Nova, Arial, sans-serif; color: #101010;">{result['options'][result['correct_answer']]}</span>
                    </div>
                </div>
                <div style="background: linear-gradient(135deg, #9990EA 0%, #8DFFE0 100%); padding: 15px; margin-top: 15px; border: 3px solid #101010;">
                    <div style="font-family: Eurostile, Arial Black, sans-serif; color: #FFFFFF; font-size: 14px; margin-bottom: 8px; font-weight: bold;">
                        💡 EXPLICATION
                    </div>
                    <div style="font-family: Proxima Nova, Arial, sans-serif; color: #FFFFFF; font-size: 15px; line-height: 1.6;">
                        {result['explanation']}
                    </div>
                </div>
            </div>
            """
            corrections_html += question_html
    else:
        corrections_html = "<p style='font-family: Proxima Nova, Arial, sans-serif; color: #8DFFE0; font-size: 18px; font-weight: bold; text-align: center; margin: 30px 0;'>🎉 Aucune erreur ! Tu as tout bon ! 🎉</p>"

    # HTML complet
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Résultats Quiz Mitochondries</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #F5F5F5; font-family: Arial, sans-serif;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #F5F5F5;">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #FFFFFF;">

                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #9990EA 0%, #8DFFE0 100%); padding: 40px 30px; text-align: center; border: 6px solid #101010;">
                                <h1 style="font-family: Eurostile, Arial Black, sans-serif; color: #FFFFFF; font-size: 32px; margin: 0 0 10px 0; text-transform: uppercase; text-shadow: 3px 3px 0 #101010;">
                                    🧬 QUIZ MITOCHONDRIES
                                </h1>
                                <p style="font-family: Proxima Nova, Arial, sans-serif; color: #FFFFFF; font-size: 18px; margin: 0; font-weight: bold;">
                                    TES RÉSULTATS SONT LÀ !
                                </p>
                            </td>
                        </tr>

                        <!-- Score principal -->
                        <tr>
                            <td style="padding: 40px 30px; text-align: center; border-left: 6px solid #101010; border-right: 6px solid #101010;">
                                <div style="background: linear-gradient(135deg, #9990EA 0%, #8DFFE0 100%); border: 5px solid #101010; padding: 30px; margin-bottom: 25px;">
                                    <div style="font-family: Eurostile, Arial Black, sans-serif; color: #FFFFFF; font-size: 56px; margin: 0; text-shadow: 4px 4px 0 #101010;">
                                        {score}/{total}
                                    </div>
                                    <div style="font-family: Proxima Nova, Arial, sans-serif; color: #FFFFFF; font-size: 28px; margin: 10px 0 0 0; font-weight: bold;">
                                        {percentage:.0f}%
                                    </div>
                                </div>

                                <p style="font-family: Proxima Nova, Arial, sans-serif; color: #101010; font-size: 18px; line-height: 1.6; margin: 20px 0;">
                                    {performance_message}
                                </p>
                            </td>
                        </tr>

                        <!-- Corrections -->
                        <tr>
                            <td style="padding: 0 30px 40px 30px; border-left: 6px solid #101010; border-right: 6px solid #101010;">
                                {corrections_html}
                            </td>
                        </tr>

                        <!-- CTA Promo Code -->
                        <tr>
                            <td style="padding: 40px 30px; background: #101010; text-align: center; border: 6px solid #101010;">
                                <div style="background: linear-gradient(135deg, #9990EA 0%, #8DFFE0 100%); padding: 30px; border: 4px solid #FFFFFF;">
                                    <h2 style="font-family: Eurostile, Arial Black, sans-serif; color: #FFFFFF; font-size: 28px; margin: 0 0 15px 0; text-transform: uppercase; text-shadow: 3px 3px 0 #101010;">
                                        🎁 TA SURPRISE !
                                    </h2>
                                    <p style="font-family: Proxima Nova, Arial, sans-serif; color: #FFFFFF; font-size: 18px; line-height: 1.6; margin: 0 0 20px 0;">
                                        Bravo d'avoir complété le quiz ! Voici ton code promo exclusif :
                                    </p>
                                    <div style="background: #FFFFFF; border: 4px solid #101010; padding: 20px; margin: 20px 0;">
                                        <div style="font-family: Eurostile, Arial Black, sans-serif; color: #101010; font-size: 36px; letter-spacing: 3px; margin: 0;">
                                            QUIZZ25
                                        </div>
                                    </div>
                                    <p style="font-family: Proxima Nova, Arial, sans-serif; color: #FFFFFF; font-size: 20px; font-weight: bold; margin: 15px 0 25px 0;">
                                        -25% SUR TOUS LES COACHINGS
                                    </p>
                                    <a href="https://www.achzodcoaching.com" style="display: inline-block; background: #FFFFFF; color: #101010; font-family: Eurostile, Arial Black, sans-serif; font-size: 18px; font-weight: bold; text-decoration: none; padding: 18px 40px; border: 4px solid #101010; text-transform: uppercase; margin-top: 10px; box-shadow: 6px 6px 0 #101010;">
                                        DÉCOUVRIR LES COACHINGS →
                                    </a>
                                </div>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px; text-align: center; background-color: #F5F5F5; border: 6px solid #101010; border-top: none;">
                                <p style="font-family: Proxima Nova, Arial, sans-serif; color: #666666; font-size: 14px; line-height: 1.6; margin: 0;">
                                    <strong>Achzod Coaching</strong><br>
                                    Expert en Performance Humaine et Pharmacologie Avancée<br>
                                    <a href="https://www.achzodcoaching.com" style="color: #9990EA; text-decoration: none;">www.achzodcoaching.com</a>
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return html
