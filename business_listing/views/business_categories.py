from django.shortcuts import render
from ..models import BusinessDetails

def business_categories(request):
    query = request.GET.get('q', '').strip().lower()
    used_keys = BusinessDetails.objects.values_list('category', flat=True).distinct()
    categories = [
        {'key': key, 'label': key}
        for key in used_keys
    ]
    if query:
        categories = [
            item for item in categories
            if query in str(item['key']).lower() or query in str(item['label']).lower()
        ]
    used_country_codes = BusinessDetails.objects.values_list('country', flat=True).distinct()
    countries = [
        {'code': str(code), 'name': str(code)}
        for code in used_country_codes
        if code
    ]
    if query:
        countries = [
            item for item in countries
            if query in item['code'].lower() or query in item['name'].lower()
        ]
    city_tuples = (
        BusinessDetails.objects
        .values_list('city', 'country', 'postal_code')
        .distinct()
    )
    cities = [
        {'name': city, 'country_code': str(country), 'postal_code': postal_code}
        for city, country, postal_code in city_tuples
        if city and country and postal_code
    ]
    if query:
        cities = [
            item for item in cities
            if query in str(item['name']).lower()
            or query in str(item['country_code']).lower()
            or query in str(item['postal_code']).lower()
        ]
    context = {
        'categories': categories,
        'countries': countries,
        'cities': cities,
        'q': request.GET.get('q', '').strip(),
    }
    return render(request, 'business_listing/business_categories.html', context)
