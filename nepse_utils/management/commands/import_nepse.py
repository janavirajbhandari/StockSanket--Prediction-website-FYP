from django.core.management.base import BaseCommand
from nepse import Nepse
from stocks.models import Stock

class Command(BaseCommand):
    help = "Import NEPSE stock symbols and basic info"

    def handle(self, *args, **kwargs):
        nepse = Nepse()
        nepse.setTLSVerification(False)
        companies = nepse.getCompanyList()

        for company in companies:
            Stock.objects.update_or_create(
                symbol=company["symbol"],
                defaults={
                    "company": company["companyName"],
                    "sector": company.get("sectorName", ""),
                    "industry": company.get("sectorName", ""),
                    "market_cap": "",
                    "revenue": "",
                }
            )

        self.stdout.write(self.style.SUCCESS(f"{len(companies)} stocks imported from NEPSE."))
