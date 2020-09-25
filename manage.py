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

# 1. 026363159, 1912297600
# everything goes fine here. hope so there. and husband asking if the first daughter did the marriage, if not why.
# 2. 029521233, 1913444225
# everything goes fine here. hope so. any problem there?
# 3. 023391427, 1915564411(my wf)
# I am fine here, and I hope so there.
# yesterday, when I calling with my boss, I heard the news that you are finding new job in company(maybe named "Unhaeng").
# I hope it's good news, and want to know about it in detail.
