# Generated by Django 4.2.2 on 2023-06-23 09:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0008_rename_startingbid_auctionlisting_currentprice"),
    ]

    operations = [
        migrations.RenameField(
            model_name="auctionlisting",
            old_name="listingUserId",
            new_name="listingUserName",
        ),
    ]
