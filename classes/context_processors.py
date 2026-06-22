from .models import Building, Floor, Room, Term, TimeSlot

def sidebar_counts(request):
    return {
        'total_buildings': Building.objects.filter(is_active=True).count(),
        'total_floors': Floor.objects.filter(is_active=True).count(),
        'total_rooms': Room.objects.filter(is_active=True).count(),
        'total_terms': Term.objects.filter(is_active=True).count(),
        'total_timeslots': TimeSlot.objects.filter(is_active=True).count(),
    }