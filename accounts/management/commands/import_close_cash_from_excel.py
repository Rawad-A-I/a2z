from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import CloseCashSchema, CloseCashEntry
from accounts.close_cash_excel import (
    list_employee_workbooks,
    build_workbook_schema_and_data,
)

import os


class Command(BaseCommand):
    help = "Import/refresh Close Cash schemas and seed entries from employee Excel files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--workbook",
            dest="workbook",
            help="Optional: import only a specific workbook filename (e.g., Ahmad.xlsx)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing schema/entries for matching keys",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        target_workbook = options.get("workbook")
        force = options.get("force")

        user_model = get_user_model()
        workbooks = list_employee_workbooks()
        if target_workbook:
            workbooks = [wb for wb in workbooks if os.path.basename(wb) == target_workbook]
            if not workbooks:
                self.stdout.write(self.style.WARNING(f"Workbook {target_workbook} not found."))
                return

        total_sheets = 0
        for workbook_path in workbooks:
            filename = os.path.basename(workbook_path)
            self.stdout.write(self.style.NOTICE(f"Processing {filename} ..."))

            mapping = build_workbook_schema_and_data(workbook_path)
            for sheet_name, payload in mapping.items():
                schema_dict = payload.get("schema", {})
                values = payload.get("values", {})
                entry_date = payload.get("entry_date")

                # Upsert schema
                if force:
                    CloseCashSchema.objects.update_or_create(
                        workbook=filename,
                        sheet_name=sheet_name,
                        version="v1",
                        defaults={"schema_json": schema_dict},
                    )
                else:
                    CloseCashSchema.objects.get_or_create(
                        workbook=filename,
                        sheet_name=sheet_name,
                        version="v1",
                        defaults={"schema_json": schema_dict},
                    )

                # Seed entry if we can match a user by username == filename base (case-insensitive)
                username = filename.replace(".xlsx", "")
                try:
                    user = user_model.objects.get(username__iexact=username)
                except user_model.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"No user matching workbook {filename}; skipping entries"))
                    continue

                # Upsert entry
                defaults = {
                    "data_json": values,
                    "source_version": "v1",
                }
                if entry_date is None:
                    # If no parseable date, fall back to today to avoid nulls
                    from django.utils import timezone
                    entry_date = timezone.now().date()

                if force:
                    CloseCashEntry.objects.update_or_create(
                        user=user,
                        workbook=filename,
                        sheet_name=sheet_name,
                        entry_date=entry_date,
                        source_version="v1",
                        defaults=defaults,
                    )
                else:
                    CloseCashEntry.objects.get_or_create(
                        user=user,
                        workbook=filename,
                        sheet_name=sheet_name,
                        entry_date=entry_date,
                        source_version="v1",
                        defaults=defaults,
                    )
                total_sheets += 1

        self.stdout.write(self.style.SUCCESS(f"Imported/updated schemas and entries for {total_sheets} sheets."))


