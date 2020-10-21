#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apilotus.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)

# Hello, HyongBom(191-229-5657,191-333-6271)
# I am SongHyok, I am calling at SuJong's sister's favor.
# They are worrying about Sujong, Hyongbom, and mother.
# Especially worrying about Sujong's health, mother's health, Hyongbom's business.
# A few days ago, Sujong's sister dreamed that you(sujong and hyongbom) made a baby. If there is good happening in homeland, let me know.
# They(sujong's sister and his husband here) really want to hear detailed news of homeland.
