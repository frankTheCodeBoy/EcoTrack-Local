import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile
from django.test import Client
from tracker.models import EcoAction
from bs4 import BeautifulSoup


# 🔧 Helper to create a fresh user
def create_user(username='ecohero', password='green123'):
    return User.objects.create_user(username=username, password=password)


# 🔧 Helper reused from views
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


@pytest.mark.django_db
def test_profile_created_on_user_creation():
    user = create_user(username='ecohero1')
    assert hasattr(user, 'profile')
    assert isinstance(user.profile, Profile)
    assert user.profile.badge_level == "🌱 Newcomer"


@pytest.mark.django_db
def test_log_action_updates_profile():
    client = Client()
    user = create_user(username='ecohero2')
    client.force_login(user)

    response = client.post(reverse('log_action'), {
        'action_type': 'solar',
        'location': 'Nairobi'
    })

    user.refresh_from_db()
    profile = user.profile
    profile.refresh_from_db()

    assert response.status_code == 302
    assert profile.total_actions == 1
    assert profile.total_points == 10  # 'solar' = 10 points
    assert profile.badge_level == "🎉 Eco Starter"


@pytest.mark.django_db
def test_dashboard_view_renders():
    client = Client()
    user = create_user(username='ecohero3')
    client.force_login(user)

    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b'Eco Points' in response.content or b'Badge' in response.content


@pytest.mark.django_db
def test_leaderboard_view_renders():
    client = Client()
    user = create_user(username='ecohero4')
    client.force_login(user)

    response = client.get(reverse('leaderboard'))
    assert response.status_code == 200
    assert b'Top' in response.content or b'Leaderboard' in response.content


@pytest.mark.django_db
def test_download_certificate_returns_pdf():
    client = Client()
    user = create_user(username='ecohero5')
    client.force_login(user)

    response = client.get(reverse('download_certificate'))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'


@pytest.mark.django_db
def test_assign_badge_levels():
    user = create_user(username='ecohero6')
    profile = Profile.objects.get(user=user)

    badge_map = {
        0: "🌱 Newcomer",
        10: "🎉 Eco Starter",
        50: "🥉 Bronze",
        100: "🥈 Silver",
        200: "🏅 Gold"
    }

    for points, expected_badge in badge_map.items():
        profile.total_points = points
        profile.badge_level = assign_badge(points)
        profile.save()
        profile.refresh_from_db()
        assert profile.badge_level == expected_badge


@pytest.mark.django_db
def test_region_summary_view_with_valid_and_unspecified_data(client):
    # Create users
    user1 = User.objects.create_user(
        username='frank', password='testpass', is_staff=True)
    user2 = User.objects.create_user(username='jane', password='testpass')
    client.login(username='frank', password='testpass')

    # Create profiles safely
    Profile.objects.get_or_create(user=user1)
    Profile.objects.get_or_create(user=user2)

    # Valid region actions
    EcoAction.objects.create(user=user1, location='Nairobi')
    EcoAction.objects.create(user=user1, location='Nairobi')
    EcoAction.objects.create(user=user2, location='Mombasa')

    # Unspecified region actions
    EcoAction.objects.create(user=user1, location='Unknown Region')
    EcoAction.objects.create(user=user1, location='')
    EcoAction.objects.create(user=user1, location=None)

    # Request the view
    response = client.get(reverse('region_summary'))
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.select('table tbody tr')

    # ✅ Extract region names (strip emoji prefix)
    def clean_region_name(cell_text):
        return cell_text.strip().split(maxsplit=1)[-1]

    region_names = [clean_region_name(
        row.find_all('td')[0].text) for row in rows]
    assert 'Nairobi' in region_names
    assert 'Mombasa' in region_names

    # ✅ Action counts and contributor usernames
    nairobi_row = next(row for row in rows if 'Nairobi' in row.text)
    assert '2' in nairobi_row.text
    assert user1.username in nairobi_row.text

    mombasa_row = next(row for row in rows if 'Mombasa' in row.text)
    assert '1' in mombasa_row.text
    assert user2.username in mombasa_row.text

    # 🚫 Unspecified regions excluded from table/chart
    assert not any(loc in region_names for loc in ['Unknown Region', '', None])

    # ⚠️ Fallback card appears with correct counts
    fallback_header = soup.find(
        string=lambda s: s and 'Unspecified Region Summary' in s)
    assert fallback_header is not None

    fallback_section = fallback_header.find_parent('div')
    assert 'Total Actions: 3' in fallback_section.text
    assert 'Unique Contributors: 1' in fallback_section.text

    # 🏆 Contributor links
    profile_url_1 = reverse('profile') + f'?user={user1.username}'
    profile_url_2 = reverse('profile') + f'?user={user2.username}'
    assert soup.find('a', href=profile_url_1)
    assert soup.find('a', href=profile_url_2)


@pytest.mark.django_db
def test_fallback_card_visibility(client):
    # Create users
    admin_user = User.objects.create_user(
        username='admin', password='testpass', is_staff=True)
    regular_user = User.objects.create_user(
        username='user', password='testpass')

    # Create profiles
    Profile.objects.get_or_create(user=admin_user)
    Profile.objects.get_or_create(user=regular_user)

    # Add unspecified actions
    EcoAction.objects.create(user=admin_user, location=None)
    EcoAction.objects.create(user=regular_user, location=None)

    # Admin should see fallback
    client.force_login(admin_user)
    response = client.get(reverse("region_summary"))
    soup = BeautifulSoup(response.content, 'html.parser')
    assert soup.find(string='⚠️ Unspecified Region Summary') is not None

    # Regular user should not see fallback
    client.force_login(regular_user)
    response = client.get(reverse("region_summary"))
    soup = BeautifulSoup(response.content, 'html.parser')
    assert soup.find(string='⚠️ Unspecified Region Summary') is None


MAX_REGIONS = 30


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff", password="pass", is_staff=True)


@pytest.fixture
def non_staff_user(db):
    return User.objects.create_user(
        username="user", password="pass", is_staff=False)


@pytest.fixture
def login_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def mock_region_queryset(monkeypatch):
    class MockQuerySet:
        def annotate(self, **kwargs): return self
        def exclude(self, **kwargs): return self
        def values(self, *args): return self
        def order_by(self, *args): return self

        def __iter__(self): return iter([
            {
                "cleaned_location": f"Region {i}", "total_actions": 100 - i,
                "unique_users": i + 1}
            for i in range(100)
        ])
    monkeypatch.setattr(
        EcoAction.objects, "annotate", lambda *args, **kwargs: MockQuerySet())


@pytest.fixture
def mock_enrich(monkeypatch):
    def fake_enrich(location):
        return type("Info", (), {
            "emoji": "🌍",
            "latitude": -1.0,
            "longitude": 36.0
        })()
    monkeypatch.setattr("tracker.utils.geo.enrich_region", fake_enrich)


def test_staff_sees_all_regions(
        client, staff_user, mock_region_queryset, mock_enrich):
    client.force_login(staff_user)
    response = client.get(reverse("region_summary"))
    assert response.status_code == 200
    assert len(response.context["region_data"]) == 100


def test_non_staff_sees_limited_regions(
        client, non_staff_user, mock_region_queryset, mock_enrich):
    client.force_login(non_staff_user)
    response = client.get(reverse("region_summary"))
    assert response.status_code == 200
    assert len(response.context["region_data"]) == 30  # matches MAX_REGIONS
