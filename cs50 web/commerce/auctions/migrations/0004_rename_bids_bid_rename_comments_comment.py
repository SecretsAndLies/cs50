# Generated by Django 4.2.2 on 2023-06-22 15:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0003_comments_bids"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Bids",
            new_name="Bid",
        ),
        migrations.RenameModel(
            old_name="Comments",
            new_name="Comment",
        ),
    ]
