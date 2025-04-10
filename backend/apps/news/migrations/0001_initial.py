# Generated by Django 4.2.20 on 2025-04-08 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("stocks", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsCategory",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name_plural": "News Categories",
            },
        ),
        migrations.CreateModel(
            name="NewsSource",
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
                ("url", models.URLField()),
                ("logo_url", models.URLField(blank=True, null=True)),
                (
                    "reliability_score",
                    models.DecimalField(
                        blank=True, decimal_places=1, max_digits=3, null=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="NewsArticle",
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
                ("title", models.CharField(max_length=255)),
                ("summary", models.TextField()),
                ("content", models.TextField()),
                ("url", models.URLField(unique=True)),
                ("published_date", models.DateTimeField()),
                ("image_url", models.URLField(blank=True, null=True)),
                (
                    "sentiment_score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=4, null=True
                    ),
                ),
                ("author", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="articles",
                        to="news.newscategory",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articles",
                        to="news.newssource",
                    ),
                ),
                (
                    "stocks",
                    models.ManyToManyField(
                        blank=True, related_name="news_articles", to="stocks.stock"
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["-published_date"],
                        name="news_newsar_publish_efb9f8_idx",
                    ),
                    models.Index(
                        fields=["sentiment_score"],
                        name="news_newsar_sentime_6a17fd_idx",
                    ),
                ],
            },
        ),
    ]
