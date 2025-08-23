from django.shortcuts import render, redirect
from .forms import EcoActionForm
from .models import EcoAction, RegionInfo
from django.utils.timezone import localtime, now, timedelta
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
from django.conf import settings
from django.db.models import Count, functions
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# 🏆 EcoTrack Local - Views for Eco Actions Tracking
# 🎯 Define point values for each action type
POINT_VALUES = {
    'walk': 5,
    'solar': 10,
    'recycle': 4,
    'plant': 8,
    'refill': 3,
    'bike': 6,
    'compost': 5,
    'share': 2,
    'repair': 7,
    'save_water': 4,
}


# 🏅 Badge thresholds for progress tracking
BADGE_THRESHOLDS = {
    "🌱 Newcomer": 0,
    "🎉 Eco Starter": 10,
    "🥉 Bronze": 50,
    "🥈 Silver": 100,
    "🏅 Gold": 200
}


# ✅ Log a new eco action
@login_required
def log_action(request):
    if request.method == 'POST':
        form = EcoActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.user = request.user
            action.save()

            # Update user's profile stats
            profile = request.user.profile
            profile.total_actions += 1

            # 🧮 Add weighted points
            points = POINT_VALUES.get(action.action_type, 1)
            profile.total_points += points

            # 🏅 Update badge based on points
            profile.badge_level = assign_badge(profile.total_points)
            profile.save()

            return redirect('dashboard')
    else:
        form = EcoActionForm()
    return render(request, 'tracker/log_action.html', {'form': form})


# 📊 Dashboard view
@login_required
def dashboard(request):
    week_ago = now() - timedelta(days=7)
    actions = EcoAction.objects.filter(
        user=request.user, timestamp__gte=week_ago)

    summary = {}
    for action in actions:
        summary[action.action_type] = summary.get(action.action_type, 0) + 1

    profile = request.user.profile
    total_actions = profile.total_actions
    total_points = profile.total_points
    badge = profile.badge_level
    streak_count = calculate_streak(request.user)

    # 🚀 Progress toward next badge
    badge_info = get_next_badge_info(total_points)

    return render(request, 'tracker/dashboard.html', {
        'summary': summary,
        'total_actions': total_actions,
        'total_points': total_points,
        'badge': badge,
        'streak_count': streak_count,
        'next_badge': badge_info['next_badge'],
        'points_needed': badge_info['points_needed'],
        'progress_percent': badge_info['progress_percent']
    })


# 👤 Profile view
@login_required
def profile_view(request):
    username = request.GET.get('user')

    if username and username != request.user.username:
        # View-only mode for another user's profile
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        editable = False
    else:
        # Logged-in user's own profile
        user = request.user
        profile = user.profile
        editable = True

    total_actions = profile.total_actions
    total_points = profile.total_points
    badge_level = profile.badge_level
    streak_count = calculate_streak(user)

    return render(request, 'tracker/profile.html', {
        'user': user,
        'profile': profile,
        'editable': editable,
        'total_actions': total_actions,
        'total_points': total_points,
        'badge_level': badge_level,
        'streak_count': streak_count
    })


# 🏅 Helper: assign badge level based on points
def assign_badge(points):
    if points >= 200:
        return "🏅 Gold"
    elif points >= 100:
        return "🥈 Silver"
    elif points >= 50:
        return "🥉 Bronze"
    elif points >= 10:
        return "🎉 Eco Starter"
    return "🌱 Newcomer"


# 🔍 Helper: get badge level based on points
# 🚀 Helper: calculate progress toward next badge
def get_next_badge_info(points):
    thresholds = sorted(BADGE_THRESHOLDS.items(), key=lambda x: x[1])
    for i, (badge, threshold) in enumerate(thresholds):
        if points < threshold:
            progress_percent = int((points / threshold) * 100)
            return {
                'next_badge': badge,
                'points_needed': threshold - points,
                'progress_percent': min(progress_percent, 100)
            }
    return {
        'next_badge': "🏅 Gold",
        'points_needed': 0,
        'progress_percent': 100
    }


# 🔁 Helper: calculate streak (consecutive weeks with actions)
def calculate_streak(user):
    actions = EcoAction.objects.filter(user=user).order_by('-timestamp')
    if not actions.exists():
        return 0

    streak = 0
    current_week = now().isocalendar()[1]

    weeks_seen = set()
    for action in actions:
        week_num = action.timestamp.isocalendar()[1]
        if week_num not in weeks_seen:
            weeks_seen.add(week_num)
            if current_week - streak == week_num:
                streak += 1
            else:
                break
    return streak


# 🏆 Leaderboard view
@login_required
def leaderboard(request):
    top_profiles = Profile.objects.order_by('-total_points')[:10]  # Top 10

    return render(request, 'tracker/leaderboard.html', {
        'top_profiles': top_profiles
    })


# 🏅 Download Eco Achievement Certificate
@login_required
def download_certificate(request):
    profile = request.user.profile
    username = profile.user.username
    badge_level = profile.badge_level or "🌱 Newcomer"
    total_points = profile.total_points

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="eco_certificate.pdf"')

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Pale Yellow Background
    c.setFillColorRGB(1.0, 1.0, 0.85)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Decorative Border
    border_margin = 0.5 * inch
    c.setStrokeColor(colors.darkgreen)
    c.setLineWidth(3)
    c.rect(
        border_margin, border_margin, width - 2 * border_margin,
        height - 2 * border_margin, stroke=1, fill=0)

    # Watermark
    watermark_path = os.path.join(
        settings.BASE_DIR, 'static/images/watermark.png')
    if os.path.exists(watermark_path):
        wm_width = 4.5 * inch
        wm_height = 4.5 * inch
        x = (width - wm_width) / 2
        y = (height - wm_height) / 2
        c.saveState()
        c.setFillAlpha(0.1)
        c.drawImage(
            watermark_path, x, y, width=wm_width, height=wm_height,
            preserveAspectRatio=True, mask='auto')
        c.restoreState()

    # Avatar
    if profile.avatar and hasattr(profile.avatar, 'path'):
        avatar_path = profile.avatar.path
        if os.path.exists(avatar_path):
            c.drawImage(
                avatar_path, inch, height - 1.8 * inch, width=1.2 * inch,
                height=1.2 * inch, mask='auto')

    # Wrapped Title (two lines, shifted down)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.darkgreen)
    c.drawCentredString(width / 2, height - 2.0 * inch, "EcoTrack Local")
    c.drawCentredString(
        width / 2, height - 2.4 * inch, "Achievement Certificate")

    # Recipient
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(
        width / 2, height - 3.1 * inch, f"Awarded to {username}")

    # Badge Level
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.blue)
    c.drawCentredString(
        width / 2, height - 3.9 * inch, f"Badge Level: {badge_level}")

    # Points
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.gray)
    c.drawCentredString(
        width / 2, height - 4.5 * inch, f"Total Eco Points: {total_points}")

    # Date
    date_str = localtime(now()).strftime("%B %d, %Y")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(
        width / 2, height - 5.3 * inch, f"Issued on {date_str}")

    # Signature
    signature_path = os.path.join(
        settings.BASE_DIR, 'static/images/signature.png')
    if os.path.exists(signature_path):
        sig_width = 2 * inch
        sig_height = 1 * inch
        x = width - sig_width - inch
        y = inch - 10

        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(
            x + sig_width / 2, y + sig_height + 6, "Signed by:")
        c.drawImage(
            signature_path, x, y, width=sig_width, height=sig_height,
            preserveAspectRatio=True, mask='auto')
        c.setFont("Helvetica", 10)
        c.drawCentredString(x + sig_width / 2, y - 12, "EcoTrack Coordinator.")

    # Appreciation Ribbon
    ribbon_height = 0.6 * inch
    ribbon_y = border_margin + 12
    ribbon_x = 1.2 * inch
    ribbon_width = width - 2.4 * inch

    c.setFillColor(colors.lightcoral)
    c.roundRect(
        ribbon_x, ribbon_y, ribbon_width, ribbon_height, radius=10,
        fill=1, stroke=0)

    # Appreciation Text
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(colors.whitesmoke)
    message = "Your actions inspire change — thank you"
    message += " for being part of the movement 🌍"
    c.drawCentredString(width / 2, ribbon_y + ribbon_height / 2 - 4, message)

    # Optional Leaf Icon (left of message)
    leaf_path = os.path.join(settings.BASE_DIR, 'static/images/leaf.png')
    if os.path.exists(leaf_path):
        leaf_size = 0.4 * inch
        leaf_x = ribbon_x + 6
        leaf_y = ribbon_y + (ribbon_height - leaf_size) / 2
        c.drawImage(
            leaf_path, leaf_x, leaf_y, width=leaf_size,
            height=leaf_size, preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    return response


# 🌍 Region Summary View
@login_required
def region_summary(request):
    MAX_REGIONS = 30

    # Clean and filter valid regions
    region_data_raw = (
        EcoAction.objects
        .annotate(cleaned_location=functions.Trim('location'))
        .exclude(cleaned_location__isnull=True)
        .exclude(cleaned_location__exact="")
        .exclude(cleaned_location="Unknown Region")
        .values('cleaned_location')
        .annotate(
            total_actions=Count('id'),
            unique_users=Count('user', distinct=True)
        )
        .order_by('-total_actions')
    )

    region_names = [r['cleaned_location'] for r in region_data_raw]
    region_info_map = {
        r.name: r for r in RegionInfo.objects.filter(name__in=region_names)
    }

    region_data = []
    for region in region_data_raw:
        loc = region['cleaned_location']
        info = region_info_map.get(loc)
        region_data.append({
            "cleaned_location": loc,
            "total_actions": region['total_actions'],
            "unique_users": region['unique_users'],
            "emoji": info.emoji if info else "❓",
            "latitude": info.latitude if info else None,
            "longitude": info.longitude if info else None,
        })

    if not request.user.is_staff:
        region_data = region_data[:MAX_REGIONS]

    # Batch top contributors
    top_actions = (
        EcoAction.objects
        .filter(location__in=region_names)
        .values('location', 'user')
        .annotate(action_count=Count('id'))
        .order_by('location', '-action_count')
    )

    seen = set()
    top_contributors = {}
    user_ids = set()

    for entry in top_actions:
        loc = entry['location']
        if loc not in seen:
            seen.add(loc)
            user_ids.add(entry['user'])
            top_contributors[loc] = {
                'user_id': entry['user'],
                'action_count': entry['action_count']
            }

    users = {u.id: u for u in User.objects.filter(id__in=user_ids)}
    profiles = {p.user_id: p for p in Profile.objects.filter(
        user_id__in=user_ids)}

    for loc, data in top_contributors.items():
        data['user'] = users.get(data['user_id'])
        data['profile'] = profiles.get(data['user_id'])

    # Fallback summary
    unspecified_actions = EcoAction.objects.filter(
        location__isnull=True
    ) | EcoAction.objects.filter(
        location__exact=""
    ) | EcoAction.objects.filter(
        location="Unknown Region"
    )

    unspecified_summary = {
        'total_actions': unspecified_actions.count(),
        'unique_users': unspecified_actions.values('user').distinct().count()
    }

    return render(request, 'tracker/region_summary.html', {
        'region_data': region_data,
        'top_contributors': top_contributors,
        'unspecified_summary': unspecified_summary,
        'max_regions': MAX_REGIONS
    })


# 🐞 Error testing view
def trigger_error(request):
    raise Exception("Intentional error for testing")
