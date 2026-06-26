
from django.db import models
from teachers.models import Teacher
from courses.models import Course

class Building(models.Model):
    """Building where classes are held"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['name']


class Floor(models.Model):
    """Floor within a building"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.CharField(max_length=10)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.building.code} - Floor {self.floor_number}"
    
    class Meta:
        ordering = ['building', 'floor_number']
        unique_together = ['building', 'floor_number']


class Room(models.Model):
    """Room within a floor"""
    ROOM_TYPES = [
        ('classroom', 'Classroom'),
        ('laboratory', 'Laboratory'),
        ('computer_lab', 'Computer Lab'),
        ('science_lab', 'Science Lab'),
        ('library', 'Library'),
        ('auditorium', 'Auditorium'),
        ('conference', 'Conference Room'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    capacity = models.IntegerField(default=30)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.building.code} - {self.room_number}"
    
    def get_full_location(self):
        location = self.building.name
        if self.floor:
            location += f" - Floor {self.floor.floor_number}"
        location += f" - Room {self.room_number}"
        return location
    
    class Meta:
        ordering = ['building', 'room_number']
        unique_together = ['building', 'room_number']


class Term(models.Model):
    """Academic term"""
    TERM_TYPES = [
        ('fall', 'Fall Semester'),
        ('spring', 'Spring Semester'),
        ('summer', 'Summer Semester'),
        ('winter', 'Winter Semester'),
    ]
    
    name = models.CharField(max_length=50)
    term_type = models.CharField(max_length=20, choices=TERM_TYPES)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_term_type_display()} {self.academic_year}"
    
    def save(self, *args, **kwargs):
        if self.is_current:
            Term.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-academic_year', 'start_date']


class TimeSlot(models.Model):
    """Time slot for classes with multiple days support"""
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    SLOT_TYPES = [
        ('morning', 'Morning Session (8:00 - 11:00)'),
        ('afternoon', 'Afternoon Session (2:00 - 5:00)'),
        ('evening', 'Evening Session (5:30 - 8:45)'),
        ('full_day', 'Full Day (8:00 - 5:00)'),
        ('saturday_morning', 'Saturday Morning (8:00 - 11:00)'),
        ('saturday_afternoon', 'Saturday Afternoon (2:00 - 5:00)'),
        ('sunday_morning', 'Sunday Morning (8:00 - 11:00)'),
        ('sunday_afternoon', 'Sunday Afternoon (2:00 - 5:00)'),
        ('weekend_full', 'Weekend Full Day (8:00 - 5:00)'),
        ('custom', 'Custom'),
    ]
    
    days = models.CharField(
        max_length=200,
        default='monday',
        help_text="Comma-separated days (e.g., 'monday,wednesday,friday')"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_type = models.CharField(max_length=20, choices=SLOT_TYPES, default='custom')
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        days_list = [dict(TimeSlot.DAYS_OF_WEEK).get(day.strip(), day) for day in self.days.split(',')]
        days_str = ', '.join(days_list)
        return f"{days_str} {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
    
    def get_days_list(self):
        return [day.strip() for day in self.days.split(',') if day.strip()]
    
    def get_days_display(self):
        days_list = self.get_days_list()
        return ', '.join([dict(TimeSlot.DAYS_OF_WEEK).get(day, day) for day in days_list])
    
    def get_duration(self):
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        duration = end - start
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    def get_slot_type_display(self):
        return dict(self.SLOT_TYPES).get(self.slot_type, 'Custom')
    
    class Meta:
        ordering = ['-created_at']


class Class(models.Model):
    """Main Class Model"""
    
    # ===== BASIC INFORMATION =====
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10, blank=True, null=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # ===== LOCATION =====
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    room_number = models.CharField(max_length=20, blank=True, null=True)
    
    # ===== SCHEDULE =====
    time_slots = models.ManyToManyField(TimeSlot, blank=True, related_name='classes')
    schedule = models.CharField(max_length=100, blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    days = models.CharField(max_length=50, blank=True, null=True)
    
    # ===== TERM =====
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    term_type = models.CharField(max_length=20, choices=Term.TERM_TYPES, blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    
    # ===== CAPACITY =====
    capacity = models.IntegerField(default=30)
    
    # ===== RELATIONSHIPS =====
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    
    # ===== STATUS =====
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name
    
    def get_student_count(self):
        return self.students.filter(is_active=True).count()
    
    def get_attendance_rate(self):
        from attendance.models import Attendance
        attendances = Attendance.objects.filter(class_obj=self)
        total = attendances.count()
        if total == 0:
            return 0
        present = attendances.filter(status='present').count()
        return round((present / total) * 100, 1)
    
    def get_present_today(self):
        from attendance.models import Attendance
        from datetime import date
        return Attendance.objects.filter(
            class_obj=self, 
            date=date.today(), 
            status='present'
        ).count()
    
    def get_full_location(self):
        if self.building and self.room:
            location = self.building.name
            if self.floor:
                location += f" - Floor {self.floor.floor_number}"
            location += f" - Room {self.room.room_number}"
            return location
        elif self.room_number:
            return f"Room: {self.room_number}"
        return "Location TBD"
    
    def get_term_display(self):
        if self.term:
            return str(self.term)
        return self.term_type or "Term TBD"
    
    def get_schedule_display(self):
        if self.time_slots.exists():
            slots = self.time_slots.all()
            return ", ".join([str(slot) for slot in slots])
        if self.start_time and self.end_time:
            time_str = f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
            if self.days:
                return f"{self.days} {time_str}"
            return time_str
        return self.schedule or "Schedule TBD"
    
    def get_capacity_status(self):
        student_count = self.get_student_count()
        if student_count >= self.capacity:
            return 'full'
        elif student_count >= self.capacity * 0.8:
            return 'near_full'
        elif student_count >= self.capacity * 0.5:
            return 'half_full'
        else:
            return 'available'
    
    class Meta:
        verbose_name_plural = "Classes"
        ordering = ['name']