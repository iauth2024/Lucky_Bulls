import os
from django.core.management.base import BaseCommand
from django.db import transaction
import pandas as pd
from Lucky_Bulls.models import HalalStock  # We'll create this model next

class Command(BaseCommand):
    help = 'Imports Halal stocks from Excel file'
    
    def handle(self, *args, **options):
        # Path to your Excel file
        file_path = os.path.join(os.path.dirname(__file__), '../../../Lucky_Bulls/Zam Zam Halal Stocks.xlsx')
        
        try:
            df = pd.read_excel(file_path)
            created_count = 0
            
            with transaction.atomic():
                # Clear existing data
                HalalStock.objects.all().delete()
                
                for index, row in df.iterrows():
                    HalalStock.objects.create(
                        company_name=row['Company Name'],
                        ticker=row['Ticker']
                    )
                    created_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {created_count} Halal stocks.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing Halal stocks: {str(e)}'))