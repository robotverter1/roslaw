from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from content.models import Chapter, Section, Subsection, QA

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with minimal TZ-compliant data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create users for each role
        roles = [
            ("admin", User.ADMIN),
            ("curator", User.CURATOR),
            ("moderator", User.MODERATOR),
            ("specialist", User.SPECIALIST),
            ("volunteer", User.VOLUNTEER),
            ("blocked", User.BLOCKED),
        ]
        users = {}
        for username, role in roles:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "password": "password123",  # Will be set below
                    "first_name": username.capitalize(),
                    "last_name": "User",
                    "role": role,
                    "is_active": role != User.BLOCKED,
                    "approved": True,
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            users[role] = user

        # Create a chapter
        chapter, _ = Chapter.objects.get_or_create(
            title="Глава 1",
            defaults={
                "author": users[User.ADMIN],
                "written_at": "2025-05-17",
                "status": "draft",
                "is_published": False,
                "is_deleted": False,
            },
        )

        # Create a section
        section, _ = Section.objects.get_or_create(
            title="Раздел 1.1",
            chapter=chapter,
            defaults={
                "author": users[User.CURATOR],
                "written_at": "2025-05-17",
                "status": "draft",
                "is_published": False,
                "is_deleted": False,
            },
        )

        # Create a subsection
        subsection, _ = Subsection.objects.get_or_create(
            title="Подраздел 1.1.1",
            section=section,
            defaults={
                "author": users[User.MODERATOR],
                "written_at": "2025-05-17",
                "status": "draft",
                "is_published": False,
                "is_deleted": False,
            },
        )

        # Create a QA
        qa, _ = QA.objects.get_or_create(
            question="Можно ли вернуть товар без чека?",
            answer="Да, с помощью свидетельских показаний (ст. 18 ЗоЗПП).",
            author=users[User.SPECIALIST],
            written_at="2025-05-17",
            status="draft",
            is_published=False,
            is_deleted=False,
        )
        qa.save()
        qa_subsection_rel = getattr(qa, "subsections", None)
        if qa_subsection_rel:
            qa.subsections.add(subsection)

        self.stdout.write(self.style.SUCCESS("Minimal database seeded successfully!"))
