# ui/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import studentcourse, GeneratedQuiz
import requests
import json
from django.conf import settings
from django.utils import timezone


# ---------- Helper Functions ----------

def _default_reminder(name: str, course) -> str:
    """Fallback message if Gemini API fails."""
    return (f"Just a friendly reminder to continue your great work on the '{course.course_name}' course. "
            f"You're at {course.completion_percentage}% and so close to the finish line. "
            f"Keep up the momentum{',' if name not in (None, '', 'there') else ''} {name or ''}!".strip())


def _extract_gemini_text(data: dict) -> str | None:
    """Safely extract the text output from Gemini's JSON response."""
    if not isinstance(data, dict):
        return None

    pf = data.get("promptFeedback") or {}
    if pf.get("blockReason"):
        return None

    cands = data.get("candidates") or []
    if not cands:
        return None

    content = cands[0].get("content") or {}
    parts = content.get("parts") or []
    texts = []
    for p in parts:
        if isinstance(p, dict) and isinstance(p.get("text"), str):
            texts.append(p["text"])
        elif isinstance(p, str):
            texts.append(p)
    out = "\n".join(t.strip() for t in texts if t and t.strip())
    return out or None


# ---------- Gemini AI Function (Updated Endpoint) ----------

def generate_ai_notification_content(user_profile, course):
    """Generate motivational email body using Gemini API (v1)."""
    API_KEY = getattr(settings, "GOOGLE_API_KEY", None)
    name = getattr(user_profile, "fullname", None) or getattr(user_profile, "name", None) or "there"

    if not API_KEY:
        print("Error: Google API Key not found.")
        return _default_reminder(name, course)

    # ✅ Updated endpoint + model
    API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = (
        f"Generate a short, friendly, and motivational email body for a student named {name}. "
        f"The student needs to be reminded to complete their course: '{course.course_name}'. "
        f"They have already completed {course.completion_percentage}% of it. "
        f"Encourage them by highlighting how close they are to finishing. Keep it under 100 words."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()

        data = response.json()
        ai_content = _extract_gemini_text(data)
        if not ai_content:
            return _default_reminder(name, course)
        return ai_content

    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error calling Gemini: {e}")
        return _default_reminder(name, course)


# ---------- Celery Tasks ----------

@shared_task
def send_daily_reminders():
    """Send one motivational reminder email per active user for their top-priority incomplete course."""
    users = User.objects.filter(is_active=True).select_related("userprofile")
    for user in users:
        priority_course = (
            studentcourse.objects
            .filter(student=user)
            .exclude(status='Completed')
            .order_by('-completion_percentage')
            .first()
        )
        if priority_course:
            email_body = generate_ai_notification_content(getattr(user, "userprofile", None), priority_course)
            if not user.email:
                continue

            send_mail(
                f"A friendly reminder about your course: {priority_course.course_name}",
                email_body,
                getattr(settings, "DEFAULT_FROM_EMAIL", "your.actual.email@gmail.com"),
                [user.email],
                fail_silently=False,
            )


@shared_task
def send_ai_quiz_reminders():
    """
    Send a friendly reminder to users who have uncompleted quizzes.
    Each user gets one email listing pending quizzes.
    """
    users = User.objects.filter(is_active=True).select_related("userprofile")

    for user in users:
        pending_quizzes = (
            GeneratedQuiz.objects
            .filter(student=user, is_completed=False)
            .select_related("course")
        )

        if not pending_quizzes.exists() or not user.email:
            continue

        fullname = getattr(getattr(user, "userprofile", None), "fullname", None) or "there"

        # Combine multiple pending quizzes into one email
        quizzes = list(pending_quizzes[:3])
        bullets = "\n".join(f"• {q.course.course_name} — {q.difficulty.capitalize()} quiz" for q in quizzes)
        remaining = pending_quizzes.count() - len(quizzes)
        extra = f"\n(+ {remaining} more pending quiz(es))" if remaining > 0 else ""

        email_body = (
            f"Hi {fullname},\n\n"
            f"Quick nudge to keep your momentum going! You have the following quiz attempts pending:\n"
            f"{bullets}{extra}\n\n"
            f"You’ve got this — even one quick attempt today moves you forward!"
        )

        send_mail(
            f"Reminder: You have pending quizzes to attempt",
            email_body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "your.actual.email@gmail.com"),
            [user.email],
            fail_silently=False,
        )
