from django.contrib import admin
from .models import Building, Floor, Room, Term, TimeSlot, Class


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'address', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'address']
    ordering = ['code']


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ['building', 'floor_number', 'name', 'is_active']
    list_filter = ['building', 'is_active']
    search_fields = ['floor_number', 'name', 'building__name']
    ordering = ['building', 'floor_number']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['building', 'room_number', 'name', 'room_type', 'capacity', 'is_active']
    list_filter = ['building', 'room_type', 'is_active']
    search_fields = ['room_number', 'name', 'building__name']
    ordering = ['building', 'room_number']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'term_type', 'academic_year', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['term_type', 'academic_year', 'is_active', 'is_current']
    search_fields = ['name', 'academic_year']
    ordering = ['-academic_year', 'start_date']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_days_display', 'start_time', 'end_time', 'slot_type', 'get_duration', 'is_active']
    list_filter = ['slot_type', 'is_active']
    search_fields = ['days', 'name', 'description']
    ordering = ['-created_at']
    
    def get_days_display(self, obj):
        return obj.get_days_display()
    get_days_display.short_description = 'Days'
    
    def get_duration(self, obj):
        return obj.get_duration()
    get_duration.short_description = 'Duration'


from .forms import ClassForm

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    form = ClassForm
    list_display = ['name', 'section', 'code', 'teacher', 'get_courses_display', 'capacity', 'is_active']
    list_filter = ['is_active', 'teacher', 'term']
    search_fields = ['name', 'section', 'code', 'teacher__first_name', 'teacher__last_name']
    filter_horizontal = ['time_slots', 'courses']  # Added 'courses' to filter_horizontal
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'section', 'code')
        }),
        ('Location', {
            'fields': ('building', 'floor', 'room', 'room_number')
        }),
        ('Schedule', {
            'fields': ('time_slots', 'schedule', 'days', 'start_time', 'end_time')
        }),
        ('Term & Academic', {
            'fields': ('term', 'term_type', 'academic_year', 'start_date', 'end_date')
        }),
        ('Capacity & Relationships', {
            'fields': ('capacity', 'teacher', 'courses')  # Changed from 'course' to 'courses'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_courses_display(self, obj):
        """Display all courses assigned to this class"""
        if obj.courses.exists():
            return ", ".join(c.code for c in obj.courses.all())
        return "No courses assigned"
    get_courses_display.short_description = 'Courses'