# Generated by Django 4.2.20 on 2025-04-08 12:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardWidget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "widget_type",
                    models.CharField(
                        choices=[
                            ("stock_chart", "Stock Chart"),
                            ("market_overview", "Market Overview"),
                            ("news_feed", "News Feed"),
                            ("watchlist", "Watchlist"),
                            ("performance", "Portfolio Performance"),
                            ("prediction", "Stock Predictions"),
                            ("custom", "Custom Widget"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("is_default", models.BooleanField(default=False)),
                ("default_config", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="UserDashboardWidget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.IntegerField(default=0)),
                ("size", models.CharField(default="medium", max_length=20)),
                ("is_enabled", models.BooleanField(default=True)),
                ("config", models.JSONField(default=dict)),
                ("last_refreshed", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dashboard_widgets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "widget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="dashboard.dashboardwidget",
                    ),
                ),
            ],
            options={
                "ordering": ["position"],
                "unique_together": {("user", "widget")},
            },
        ),
    ]
