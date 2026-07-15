from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import date
from django.http import JsonResponse
import json

from accounts.decorators import admin_required, teacher_required, teacher_or_admin_required
from .models import Building, Floor, Room, Term, TimeSlot, Class
from .forms import (
    BuildingForm, BuildingSearchForm,
    FloorForm, FloorSearchForm,
    RoomForm, RoomSearchForm,
    TermForm,
    TimeSlotForm,
    ClassForm, ClassSearchForm
)
from teachers.models import Teacher
from students.models import Student
from courses.models import Course
from attendance.models import Attendance
from attendance.utils import attendance_rate_percent
from .schedule_conflicts import build_slot_entries, slot_entries_from_time_slots


def get_students_for_course(course):
    """Get all students enrolled in a course"""
    students = Student.objects.filter(
        Q(courses=course) | Q(classes_enrolled__courses=course),
        is_active=True
    ).distinct()
    return students


# ==================== BUILDING VIEWS ====================
@login_required
@admin_required
def building_list(request):
    buildings = Building.objects.all()
    form = BuildingSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        
        if search:
            buildings = buildings.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        if status:
            buildings = buildings.filter(is_active=(status == 'active'))
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(buildings, per_page)
    page = request.GET.get('page')
    buildings_page = paginator.get_page(page)

    context = {
        'buildings': buildings_page,
        'per_page': per_page,
        'form': form,
        'total': Building.objects.count(),
        'active': Building.objects.filter(is_active=True).count(),
        'inactive': Building.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/facility/building_list.html', context)


@login_required
@admin_required
def building_add(request):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            building = form.save()
            messages.success(request, f'✅ Building {building.name} added successfully!')
            return redirect('classes:building_list')
    else:
        form = BuildingForm()
    
    return render(request, 'Backend/admin/facility/building_form.html', {'form': form, 'title': 'Add Building'})


@login_required
@admin_required
def building_edit(request, pk):
    building = get_object_or_404(Building, pk=pk)
    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)
        if form.is_valid():
            building = form.save()
            messages.success(request, f'✅ Building {building.name} updated successfully!')
            return redirect('classes:building_list')
    else:
        form = BuildingForm(instance=building)
    
    return render(request, 'Backend/admin/facility/building_form.html', {'form': form, 'building': building, 'title': 'Edit Building', 'is_edit': True})


@login_required
@admin_required
def building_delete(request, pk):
    building = get_object_or_404(Building, pk=pk)
    if request.method == 'POST':
        name = building.name
        building.delete()
        messages.success(request, f'🗑️ Building {name} deleted successfully!')
        return redirect('classes:building_list')
    
    return render(request, 'Backend/admin/facility/building_delete.html', {'building': building})


@login_required
@admin_required
def building_toggle_status(request, pk):
    building = get_object_or_404(Building, pk=pk)
    building.is_active = not building.is_active
    building.save()
    status = 'activated' if building.is_active else 'deactivated'
    messages.success(request, f'Building {building.name} {status}!')
    return redirect('classes:building_list')


# ==================== FLOOR VIEWS ====================
@login_required
@admin_required
def floor_list(request):
    floors = Floor.objects.all()
    form = FloorSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        building = form.cleaned_data.get('building')
        status = form.cleaned_data.get('status')
        
        if search:
            floors = floors.filter(
                Q(floor_number__icontains=search) | Q(name__icontains=search)
            )
        if building:
            floors = floors.filter(building=building)
        if status:
            floors = floors.filter(is_active=(status == 'active'))
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(floors, per_page)
    page = request.GET.get('page')
    floors_page = paginator.get_page(page)
    
    context = {
        'floors': floors_page,
        'per_page': per_page,
        'form': form,
        'buildings': Building.objects.filter(is_active=True).order_by('name'),
        'total': Floor.objects.count(),
        'active': Floor.objects.filter(is_active=True).count(),
        'inactive': Floor.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/facility/floor_list.html', context)


@login_required
@admin_required
def floor_add(request):
    if request.method == 'POST':
        form = FloorForm(request.POST)
        if form.is_valid():
            floor = form.save()
            messages.success(request, f'✅ Floor {floor.floor_number} added successfully!')
            return redirect('classes:floor_list')
    else:
        form = FloorForm()
    
    return render(request, 'Backend/admin/facility/floor_form.html', {'form': form, 'title': 'Add Floor'})


@login_required
@admin_required
def floor_edit(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    if request.method == 'POST':
        form = FloorForm(request.POST, instance=floor)
        if form.is_valid():
            floor = form.save()
            messages.success(request, f'✅ Floor {floor.floor_number} updated successfully!')
            return redirect('classes:floor_list')
    else:
        form = FloorForm(instance=floor)
    
    return render(request, 'Backend/admin/facility/floor_form.html', {'form': form, 'floor': floor, 'title': 'Edit Floor', 'is_edit': True})


@login_required
@admin_required
def floor_delete(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    if request.method == 'POST':
        name = floor.floor_number
        floor.delete()
        messages.success(request, f'🗑️ Floor {name} deleted successfully!')
        return redirect('classes:floor_list')
    
    return render(request, 'Backend/admin/facility/floor_delete.html', {'floor': floor})


@login_required
@admin_required
def floor_toggle_status(request, pk):
    floor = get_object_or_404(Floor, pk=pk)
    floor.is_active = not floor.is_active
    floor.save()
    status = 'activated' if floor.is_active else 'deactivated'
    messages.success(request, f'Floor {floor.floor_number} {status}!')
    return redirect('classes:floor_list')


# ==================== ROOM VIEWS ====================
@login_required
@admin_required
def room_list(request):
    rooms = Room.objects.all()
    form = RoomSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        building = form.cleaned_data.get('building')
        room_type = form.cleaned_data.get('room_type')
        status = form.cleaned_data.get('status')
        
        if search:
            rooms = rooms.filter(
                Q(room_number__icontains=search) | Q(name__icontains=search)
            )
        if building:
            rooms = rooms.filter(building=building)
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if status:
            rooms = rooms.filter(is_active=(status == 'active'))
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(rooms, per_page)
    page = request.GET.get('page')
    rooms_page = paginator.get_page(page)
    
    total_capacity = sum(room.capacity for room in rooms_page)
    
    context = {
        'rooms': rooms_page,
        'per_page': per_page,
        'form': form,
        'buildings': Building.objects.filter(is_active=True).order_by('name'),
        'total': Room.objects.count(),
        'active': Room.objects.filter(is_active=True).count(),
        'inactive': Room.objects.filter(is_active=False).count(),
        'total_capacity': total_capacity,
    }
    return render(request, 'Backend/admin/facility/room_list.html', context)


@login_required
@admin_required
def room_add(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'✅ Room {room.room_number} added successfully!')
            return redirect('classes:room_list')
    else:
        form = RoomForm()
    
    return render(request, 'Backend/admin/facility/room_form.html', {'form': form, 'title': 'Add Room'})


@login_required
@admin_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'✅ Room {room.room_number} updated successfully!')
            return redirect('classes:room_list')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'Backend/admin/facility/room_form.html', {'form': form, 'room': room, 'title': 'Edit Room', 'is_edit': True})


@login_required
@admin_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        name = room.room_number
        room.delete()
        messages.success(request, f'🗑️ Room {name} deleted successfully!')
        return redirect('classes:room_list')
    
    return render(request, 'Backend/admin/facility/room_delete.html', {'room': room})


@login_required
@admin_required
def room_toggle_status(request, pk):
    room = get_object_or_404(Room, pk=pk)
    room.is_active = not room.is_active
    room.save()
    status = 'activated' if room.is_active else 'deactivated'
    messages.success(request, f'Room {room.room_number} {status}!')
    return redirect('classes:room_list')


# ==================== TERM VIEWS ====================
@login_required
@admin_required
def term_list(request):
    terms = Term.objects.all()
    
    # Get filter parameters
    search = request.GET.get('search', '')
    term_type = request.GET.get('term_type', '')
    academic_year = request.GET.get('academic_year', '')
    status = request.GET.get('status', '')
    
    # Apply filters
    if search:
        terms = terms.filter(
            Q(name__icontains=search) | 
            Q(academic_year__icontains=search)
        )
    
    if term_type:
        terms = terms.filter(term_type=term_type)
    
    if academic_year:
        terms = terms.filter(academic_year=academic_year)
    
    if status:
        if status == 'current':
            terms = terms.filter(is_current=True)
        elif status == 'active':
            terms = terms.filter(is_active=True, is_current=False)
        elif status == 'inactive':
            terms = terms.filter(is_active=False)
    
    # Get all unique academic years for the filter dropdown
    academic_years = Term.objects.values_list('academic_year', flat=True).distinct().order_by('-academic_year')
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(terms, per_page)
    page = request.GET.get('page')
    terms_page = paginator.get_page(page)

    context = {
        'terms': terms_page,
        'per_page': per_page,
        'total': Term.objects.count(),
        'active': Term.objects.filter(is_active=True).count(),
        'inactive': Term.objects.filter(is_active=False).count(),
        'current': Term.objects.filter(is_current=True).count(),
        'academic_years': academic_years,
        'search': search,
        'term_type': term_type,
        'academic_year': academic_year,
        'status': status,
    }
    return render(request, 'Backend/admin/academic/term_list.html', context)


@login_required
@admin_required
def term_add(request):
    if request.method == 'POST':
        form = TermForm(request.POST)
        if form.is_valid():
            term = form.save()
            messages.success(request, f'✅ Term {term.name} added successfully!')
            return redirect('classes:term_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TermForm()
    
    return render(request, 'Backend/admin/academic/term_form.html', {
        'form': form, 
        'title': 'Add Term',
        'is_edit': False
    })


@login_required
@admin_required
def term_edit(request, pk):
    term = get_object_or_404(Term, pk=pk)
    if request.method == 'POST':
        form = TermForm(request.POST, instance=term)
        if form.is_valid():
            term = form.save()
            messages.success(request, f'✅ Term {term.name} updated successfully!')
            return redirect('classes:term_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TermForm(instance=term)
    
    return render(request, 'Backend/admin/academic/term_form.html', {
        'form': form, 
        'term': term, 
        'title': 'Edit Term',
        'is_edit': True
    })


@login_required
@admin_required
def term_delete(request, pk):
    term = get_object_or_404(Term, pk=pk)
    if request.method == 'POST':
        name = term.name
        term.delete()
        messages.success(request, f'🗑️ Term {name} deleted successfully!')
        return redirect('classes:term_list')
    
    return render(request, 'Backend/admin/academic/term_delete.html', {'term': term})


@login_required
@admin_required
def term_toggle_status(request, pk):
    term = get_object_or_404(Term, pk=pk)
    term.is_active = not term.is_active
    term.save()
    status = 'activated' if term.is_active else 'deactivated'
    messages.success(request, f'Term {term.name} {status}!')
    return redirect('classes:term_list')


@login_required
@admin_required
def term_set_current(request, pk):
    term = get_object_or_404(Term, pk=pk)
    term.is_current = True
    term.save()
    messages.success(request, f'✅ {term.name} set as current term!')
    return redirect('classes:term_list')


# ==================== TIME SLOT VIEWS ====================
@login_required
@admin_required
def timeslot_list(request):
    slots = TimeSlot.objects.all()
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(slots, per_page)
    page = request.GET.get('page')
    slots_page = paginator.get_page(page)

    context = {
        'timeslots': slots_page,
        'per_page': per_page,
        'total': TimeSlot.objects.count(),
        'active': TimeSlot.objects.filter(is_active=True).count(),
        'inactive': TimeSlot.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/academic/timeslot_list.html', context)


@login_required
@admin_required
def timeslot_add(request):
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            # Convert days list to comma-separated string
            days_list = form.cleaned_data.get('days')
            days_str = ','.join(days_list)
            
            time_slot = TimeSlot(
                days=days_str,
                start_time=form.cleaned_data.get('start_time'),
                end_time=form.cleaned_data.get('end_time'),
                slot_type=form.cleaned_data.get('slot_type') or 'custom',
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                is_active=form.cleaned_data.get('is_active')
            )
            time_slot.save()
            
            messages.success(request, f'✅ Time slot added successfully for {time_slot.get_days_display()}!')
            return redirect('classes:timeslot_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'Backend/admin/academic/timeslot_form.html', {
                'form': form,
                'title': 'Add Time Slot',
                'selected_days': request.POST.getlist('days'),
                'is_edit': False
            })
    else:
        form = TimeSlotForm()
    
    return render(request, 'Backend/admin/academic/timeslot_form.html', {
        'form': form,
        'title': 'Add Time Slot',
        'selected_days': [],
        'is_edit': False
    })


@login_required
@admin_required
def timeslot_edit(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            # Convert days list to comma-separated string
            days_list = form.cleaned_data.get('days')
            slot.days = ','.join(days_list)
            slot.start_time = form.cleaned_data.get('start_time')
            slot.end_time = form.cleaned_data.get('end_time')
            slot.slot_type = form.cleaned_data.get('slot_type') or 'custom'
            slot.name = form.cleaned_data.get('name')
            slot.description = form.cleaned_data.get('description')
            slot.is_active = form.cleaned_data.get('is_active')
            slot.save()
            
            messages.success(request, f'✅ Time slot updated successfully for {slot.get_days_display()}!')
            return redirect('classes:timeslot_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'Backend/admin/academic/timeslot_form.html', {
                'form': form,
                'timeslot': slot,
                'title': 'Edit Time Slot',
                'is_edit': True,
                'selected_days': request.POST.getlist('days')
            })
    else:
        # Pre-populate the form with existing data
        initial_data = {
            'days': slot.get_days_list(),
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'slot_type': slot.slot_type,
            'name': slot.name,
            'description': slot.description,
            'is_active': slot.is_active
        }
        form = TimeSlotForm(initial=initial_data)
    
    return render(request, 'Backend/admin/academic/timeslot_form.html', {
        'form': form,
        'timeslot': slot,
        'title': 'Edit Time Slot',
        'is_edit': True,
        'selected_days': slot.get_days_list()
    })


@login_required
@admin_required
def timeslot_delete(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    if request.method == 'POST':
        slot.delete()
        messages.success(request, f'🗑️ Time slot deleted successfully!')
        return redirect('classes:timeslot_list')
    
    return render(request, 'Backend/admin/academic/timeslot_delete.html', {'timeslot': slot})


@login_required
@admin_required
def timeslot_toggle_status(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    slot.is_active = not slot.is_active
    slot.save()
    status = 'activated' if slot.is_active else 'deactivated'
    messages.success(request, f'Time slot {status}!')
    return redirect('classes:timeslot_list')


# ==================== CLASS VIEWS ====================
@login_required
@admin_required
def class_list(request):
    classes = Class.objects.all()
    form = ClassSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        teacher = form.cleaned_data.get('teacher')
        building = form.cleaned_data.get('building')
        term = form.cleaned_data.get('term')
        status = form.cleaned_data.get('status')
        
        if search:
            classes = classes.filter(
                Q(name__icontains=search) |
                Q(section__icontains=search) |
                Q(code__icontains=search) |
                Q(room_number__icontains=search)
            )
        if teacher:
            classes = classes.filter(teacher=teacher)
        if building:
            classes = classes.filter(building=building)
        if term:
            classes = classes.filter(term=term)
        if status:
            classes = classes.filter(is_active=(status == 'active'))
    
    total_classes = Class.objects.count()
    active_classes = Class.objects.filter(is_active=True).count()
    inactive_classes = Class.objects.filter(is_active=False).count()
    total_students = Student.objects.count()
    
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = 10
    if per_page not in (5, 10, 20):
        per_page = 10

    paginator = Paginator(classes, per_page)
    page = request.GET.get('page')
    classes_page = paginator.get_page(page)

    # Get teachers and buildings for dropdowns
    teachers = Teacher.objects.filter(is_active=True)
    buildings = Building.objects.filter(is_active=True)

    context = {
        'classes': classes_page,
        'per_page': per_page,
        'form': form,
        'total_classes': total_classes,
        'active_classes': active_classes,
        'inactive_classes': inactive_classes,
        'total_students': total_students,
        'teachers': teachers,
        'buildings': buildings,
    }
    
    return render(request, 'Backend/admin/class/class_list.html', context)


# ==================== CLASS CREATE & EDIT VIEWS ====================
@login_required
@admin_required
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save()
            messages.success(request, f'✅ Class "{class_obj.name}" created successfully!')
            return redirect('classes:class_detail', pk=class_obj.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassForm()
    
    # Get data for dropdowns
    context = {
        'form': form,
        'title': 'Add New Class',
        'is_edit': False,
        'buildings': Building.objects.filter(is_active=True),
        'floors': Floor.objects.filter(is_active=True),
        'rooms': Room.objects.filter(is_active=True),
        'terms': Term.objects.filter(is_active=True),
        'time_slots': TimeSlot.objects.filter(is_active=True),
        'teachers': Teacher.objects.filter(is_active=True),
        'courses': Course.objects.filter(is_active=True),
    }
    return render(request, 'Backend/admin/class/class_form.html', context)


@login_required
@admin_required
def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Class "{class_obj.name}" updated successfully!')
            return redirect('classes:class_detail', pk=class_obj.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClassForm(instance=class_obj)
    
    # Get data for dropdowns
    context = {
        'form': form,
        'title': 'Edit Class',
        'class': class_obj,
        'is_edit': True,
        'buildings': Building.objects.filter(is_active=True),
        'floors': Floor.objects.filter(is_active=True),
        'rooms': Room.objects.filter(is_active=True),
        'terms': Term.objects.filter(is_active=True),
        'time_slots': TimeSlot.objects.filter(is_active=True),
        'teachers': Teacher.objects.filter(is_active=True),
        'courses': Course.objects.filter(is_active=True),
    }
    return render(request, 'Backend/admin/class/class_form.html', context)


@login_required
@admin_required
def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.enrolled_students.filter(is_active=True)
    courses = class_obj.courses.filter(is_active=True)
    
    today = date.today()
    course_list = list(courses)

    for student in students:
        att = None
        if course_list:
            att = Attendance.objects.filter(
                student=student, course__in=course_list, date=today
            ).first()
        student.attendance_status = att.status if att else None

    total_students = students.count()

    if course_list:
        student_ids = students.values_list('id', flat=True)
        present_count = Attendance.objects.filter(
            course__in=course_list,
            date=today,
            status='present',
            student_id__in=student_ids
        ).values('student_id').distinct().count()
        absent_count = Attendance.objects.filter(
            course__in=course_list,
            date=today,
            status='absent',
            student_id__in=student_ids
        ).values('student_id').distinct().count()
        late_count = Attendance.objects.filter(
            course__in=course_list,
            date=today,
            status='late',
            student_id__in=student_ids
        ).values('student_id').distinct().count()
        excused_count = Attendance.objects.filter(
            course__in=course_list,
            date=today,
            status='excused',
            student_id__in=student_ids
        ).values('student_id').distinct().count()
    else:
        present_count = 0
        absent_count = 0
        late_count = 0
        excused_count = 0
    
    present_percentage = attendance_rate_percent(present_count, total_students) if total_students > 0 else 0
    
    context = {
        'class': class_obj,
        'students': students,
        'courses': courses,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'present_percentage': present_percentage,
        'today': today,
    }
    return render(request, 'Backend/admin/class/class_detail.html', context)


@login_required
@admin_required
def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        name = class_obj.name
        class_obj.delete()
        messages.success(request, f'🗑️ Class "{name}" deleted successfully!')
        return redirect('classes:class_list')
    
    return render(request, 'Backend/admin/class/class_delete.html', {'class': class_obj})


@login_required
@admin_required
def class_toggle_status(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    class_obj.is_active = not class_obj.is_active
    class_obj.save()
    status = 'activated' if class_obj.is_active else 'deactivated'
    messages.success(request, f'Class "{class_obj.name}" {status}!')
    return redirect('classes:class_list')


@login_required
@admin_required
def class_add_student(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        if not student_ids:
            messages.warning(request, 'Please select at least one student.')
            return redirect('classes:class_add_student', pk=class_obj.pk)
        
        added_count = 0
        already_enrolled = 0
        
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id, is_active=True)
                if student.classes_enrolled.filter(id=class_obj.id).exists():
                    already_enrolled += 1
                else:
                    student.classes_enrolled.add(class_obj)
                    added_count += 1
            except Student.DoesNotExist:
                continue
        
        if added_count > 0:
            messages.success(request, f'{added_count} student(s) added to "{class_obj.name}" successfully!')
        if already_enrolled > 0:
            messages.warning(request, f'{already_enrolled} student(s) were already enrolled in this class.')
        if added_count == 0 and already_enrolled == 0:
            messages.warning(request, 'No students were added.')
        
        return redirect('classes:class_detail', pk=class_obj.pk)
    
    available_students = Student.objects.filter(is_active=True).exclude(
        classes_enrolled__id=class_obj.id
    )
    
    context = {
        'class': class_obj,
        'available_students': available_students,
    }
    return render(request, 'Backend/admin/class/add_student.html', context)


@login_required
@admin_required
def class_remove_student(request, class_pk, student_pk):
    class_obj = get_object_or_404(Class, pk=class_pk)
    student = get_object_or_404(Student, pk=student_pk)
    
    if request.method == 'POST':
        student.classes_enrolled.remove(class_obj)
        messages.success(request, f'Student "{student.get_full_name()}" removed from "{class_obj.name}" successfully!')
        return redirect('classes:class_detail', pk=class_obj.pk)
    
    context = {
        'class': class_obj,
        'student': student,
    }
    return render(request, 'Backend/admin/class/remove_student.html', context)


# ==================== TEACHER CLASS VIEWS ====================
@login_required
@teacher_required
def teacher_class_list(request):
    """Teacher's view of their classes - ONLY classes assigned to this teacher"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        classes_qs = Class.objects.filter(
            teacher=teacher, is_active=True
        ).annotate(
            active_students_count=Count(
                'enrolled_students', filter=Q(enrolled_students__is_active=True)
            )
        )

        # ===== PAGINATION (unified footer) =====
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (5, 10, 20):
            per_page = 10

        paginator = Paginator(classes_qs, per_page)
        page_number = request.GET.get('page')
        classes_page = paginator.get_page(page_number)

        # Total active students across all of this teacher's classes (per-class sum)
        total_students = Class.objects.filter(
            teacher=teacher, is_active=True
        ).aggregate(
            total=Count('enrolled_students', filter=Q(enrolled_students__is_active=True))
        )['total'] or 0

        context = {
            'classes': classes_page,
            'per_page': per_page,
            'teacher': teacher,
            'total_classes': classes_qs.count(),
            'total_students': total_students,
        }
        return render(request, 'Backend/teacher/class/teacher_class_list.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')

@login_required
@teacher_required
def class_courses_view(request, class_id):
    """View only courses assigned to THIS SPECIFIC class"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Verify the teacher owns this class
        if class_obj.teacher != teacher:
            messages.error(request, 'You do not have permission to view this class.')
            return redirect('classes:teacher_class_list')
        
        # IMPORTANT: Get courses ONLY for THIS SPECIFIC class.
        # Annotate each course with the exact number of ACTIVE students
        # enrolled in that course (per-course count).
        courses = class_obj.courses.filter(is_active=True).annotate(
            active_students_count=Count('students', filter=Q(students__is_active=True))
        )

        # Active students enrolled in THIS class (per-class total + attendance scope)
        students = class_obj.enrolled_students.filter(is_active=True)
        student_ids = list(students.values_list('id', flat=True))

        # Per-course stats
        today = date.today()
        course_data = []

        for course in courses:
            course_student_count = course.active_students_count

            course_attendance_taken = Attendance.objects.filter(
                course=course,
                date=today,
                student_id__in=student_ids,
            ).exists()

            present_today_count = Attendance.objects.filter(
                course=course,
                date=today,
                status='present',
                student_id__in=student_ids,
            ).values('student_id').distinct().count()

            course_data.append({
                'course': course,
                'student_count': course_student_count,
                'attendance_taken': course_attendance_taken,
                'present_today': min(present_today_count, course_student_count),
            })
        
        # ===== PAGINATION (unified footer) =====
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (5, 10, 20):
            per_page = 10

        paginator = Paginator(course_data, per_page)
        page_number = request.GET.get('page')
        courses_page = paginator.get_page(page_number)

        context = {
            'class': class_obj,
            'courses': courses_page,  # ← ONLY courses for THIS class
            'per_page': per_page,
            'students': students,
            'total_students': students.count(),
            'today': today,
            'teacher': teacher,
        }
        return render(request, 'Backend/teacher/class/class_courses.html', context)
        
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('classes:teacher_class_list')


@login_required
@teacher_required
def teacher_course_attendance_view(request):
    """Teachers can take attendance for their courses - ONLY their courses"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Get all classes taught by this teacher
        classes = Class.objects.filter(teacher=teacher, is_active=True).distinct()
        
        # Get all courses from these classes
        all_courses = Course.objects.filter(
            class_offerings__in=classes,
            is_active=True
        ).distinct()
        
        if not all_courses.exists():
            messages.info(request, 'You have no courses assigned to you.')
        
        today = date.today()
        course_data = []
        
        for course in all_courses:
            # Get students enrolled in this course
            students = get_students_for_course(course)
            
            attendance_taken = Attendance.objects.filter(
                course=course,
                date=today
            ).exists()
            student_count = students.count()
            
            present_today_count = Attendance.objects.filter(
                course=course,
                date=today,
                status='present'
            ).values('student_id').distinct().count()
            
            is_class_course = Class.objects.filter(courses=course, teacher=teacher).exists()
            
            course_data.append({
                'course': course,
                'student_count': student_count,
                'attendance_taken': attendance_taken,
                'present_today': min(present_today_count, student_count) if student_count > 0 else 0,
                'is_class_course': is_class_course,
            })
        
        # ===== PAGINATION (unified footer) =====
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
        except (TypeError, ValueError):
            per_page = 10
        if per_page not in (5, 10, 20):
            per_page = 10

        paginator = Paginator(course_data, per_page)
        page_number = request.GET.get('page')
        courses_page = paginator.get_page(page_number)

        context = {
            'courses': courses_page,
            'per_page': per_page,
            'teacher': teacher,
            'today': today,
            'total_courses': len(course_data),
            'has_classes': classes.exists(),
        }
        return render(request, 'Backend/teacher/attendance/course_attendance.html', context)
        
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')


@login_required
@teacher_required
def teacher_course_attendance_detail(request, course_id):
    """Take attendance for a specific course - ONLY if teacher owns the course"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, is_active=True)
        
        # SECURITY: Verify the teacher teaches a class that includes this course
        teacher_classes = Class.objects.filter(teacher=teacher, is_active=True)
        if not Class.objects.filter(pk__in=teacher_classes, courses=course).exists():
            messages.error(request, 'You do not have permission to manage attendance for this course.')
            return redirect('classes:teacher_course_attendance')
        
        # Get all students for this course
        students = get_students_for_course(course)
        
        today = date.today()
        
        # Attach attendance data directly to each student
        for student in students:
            att = Attendance.objects.filter(
                student=student,
                course=course,
                date=today
            ).first()
            if att:
                student.attendance_status = att.status
                student.attendance_remarks = att.remarks
                student.attendance_time_in = att.time_in
                student.attendance_time_out = att.time_out
            else:
                student.attendance_status = None
                student.attendance_remarks = ''
                student.attendance_time_in = None
                student.attendance_time_out = None
        
        if request.method == 'POST':
            saved_count = 0
            for student in students:
                status = request.POST.get(f'student_{student.id}')
                if status:
                    try:
                        attendance, created = Attendance.objects.get_or_create(
                            student=student,
                            course=course,
                            date=today,
                            defaults={
                                'status': status,
                                'remarks': request.POST.get(f'remarks_{student.id}', ''),
                                'marked_by': teacher,
                                'time_in': request.POST.get(f'time_in_{student.id}', None),
                                'time_out': request.POST.get(f'time_out_{student.id}', None)
                            }
                        )
                        if not created:
                            attendance.status = status
                            attendance.remarks = request.POST.get(f'remarks_{student.id}', '')
                            attendance.time_in = request.POST.get(f'time_in_{student.id}', None)
                            attendance.time_out = request.POST.get(f'time_out_{student.id}', None)
                            attendance.marked_by = teacher
                            attendance.save()
                        saved_count += 1
                    except Exception:
                        pass
            
            messages.success(request, f'Attendance saved for {saved_count} students in {course.name}!')
            return redirect('classes:teacher_course_attendance_detail', course_id=course_id)
        
        context = {
            'course': course,
            'students': students,
            'today': today,
            'total_students': students.count(),
            'teacher': teacher,
            'attendance_taken': Attendance.objects.filter(course=course, date=today).exists(),
        }
        return render(request, 'Backend/teacher/attendance/take_course_attendance.html', context)
        
    except Teacher.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('dashboard')
    except Course.DoesNotExist:
        messages.error(request, 'Course not found or inactive.')
        return redirect('classes:teacher_course_attendance')


# ==================== CLASS ASSIGN COURSES ====================
@login_required
@admin_required
def class_assign_courses(request, pk):
    """Assign courses to a class"""
    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        course_ids = request.POST.getlist('courses')

        # Clear existing courses
        class_obj.courses.clear()

        if course_ids:
            selected_courses = Course.objects.filter(id__in=course_ids, is_active=True)
            class_obj.courses.set(selected_courses)

            # Validate no duplicate assignment in the same time slots + academic year
            academic_year = class_obj.academic_year or (class_obj.term.academic_year if class_obj.term else '')
            class_slot_ids = list(class_obj.time_slots.values_list('id', flat=True))

            if class_slot_ids and academic_year:
                conflicting = []
                for course in selected_courses:
                    existing_classes = Class.objects.filter(
                        courses=course,
                        is_active=True,
                    ).exclude(pk=class_obj.pk)
                    for other in existing_classes:
                        other_slot_ids = list(other.time_slots.values_list('id', flat=True))
                        if set(class_slot_ids) & set(other_slot_ids) and other.academic_year == academic_year:
                            conflicting.append((course, other))

                if conflicting:
                    class_obj.courses.clear()
                    conflict_messages = [
                        f"Course '{course.code}' is already assigned to class '{other.name}' ({academic_year}) with overlapping time slots."
                        for course, other in conflicting
                    ]
                    messages.error(request, 'Schedule conflict detected: ' + '; '.join(conflict_messages))
                    return redirect('classes:class_assign_courses', pk=class_obj.pk)

            # Assign the class teacher to these courses if not already assigned
            if class_obj.teacher:
                courses_to_update = Course.objects.filter(id__in=course_ids, teacher__isnull=True)
                for course in courses_to_update:
                    course.teacher = class_obj.teacher
                    course.save()
                messages.success(request, f'✅ {len(course_ids)} courses assigned to {class_obj.name}!')
            else:
                messages.warning(request, f'⚠️ {len(course_ids)} courses assigned but class has no teacher!')
        else:
            messages.warning(request, f'All courses removed from {class_obj.name}!')

        return redirect('classes:class_detail', pk=class_obj.pk)

    # Get all courses and assigned courses
    all_courses = Course.objects.filter(is_active=True).order_by('code')
    assigned_courses = class_obj.courses.all()
    assigned_ids = list(assigned_courses.values_list('id', flat=True))

    context = {
        'class': class_obj,
        'all_courses': all_courses,
        'assigned_ids': assigned_ids,
    }
    return render(request, 'Backend/admin/class/assign_courses.html', context)


# ==================== AJAX ENDPOINTS ====================
@login_required
@admin_required
def get_floors(request, building_id):
    floors = Floor.objects.filter(building_id=building_id, is_active=True)
    return JsonResponse(list(floors.values('id', 'floor_number', 'name')), safe=False)


@login_required
@admin_required
def get_rooms(request, floor_id):
    rooms = Room.objects.filter(floor_id=floor_id, is_active=True)
    return JsonResponse(list(rooms.values('id', 'room_number', 'name', 'room_type', 'capacity')), safe=False)


@login_required
@admin_required
def get_building_rooms(request, building_id):
    rooms = Room.objects.filter(building_id=building_id, is_active=True)
    return JsonResponse(list(rooms.values('id', 'room_number', 'floor__floor_number', 'name', 'room_type', 'capacity')), safe=False)


@login_required
@admin_required
def get_term_details(request, term_id):
    term = get_object_or_404(Term, pk=term_id)
    return JsonResponse({
        'start_date': term.start_date.strftime('%Y-%m-%d'),
        'end_date': term.end_date.strftime('%Y-%m-%d'),
        'academic_year': term.academic_year,
        'name': term.name,
        'term_type': term.get_term_type_display()
    })


@login_required
@admin_required
def get_available_courses(request):
    from courses.models import Course as CourseModel

    time_slot_ids_raw = request.GET.get('time_slot_ids', '')
    academic_year     = request.GET.get('academic_year', '').strip()
    exclude_class_pk  = request.GET.get('exclude_class', None)

    selected_slot_ids = []
    for part in time_slot_ids_raw.split(','):
        part = part.strip()
        if part.isdigit():
            selected_slot_ids.append(int(part))

    available = CourseModel.objects.filter(is_active=True)

    if selected_slot_ids and academic_year:
        selected_slots = TimeSlot.objects.filter(id__in=selected_slot_ids)
        slot_entries = build_slot_entries(time_slots=selected_slots)
        exclude_pk = int(exclude_class_pk) if exclude_class_pk and str(exclude_class_pk).isdigit() else None

        conflicting_course_ids = []
        for course in available:
            if find_course_schedule_conflict(course, academic_year, slot_entries, exclude_pk=exclude_pk):
                conflicting_course_ids.append(course.id)

        if conflicting_course_ids:
            available = available.exclude(id__in=conflicting_course_ids)

    data = [
        {'id': c.id, 'text': f"{c.code} — {c.name}"}
        for c in available.order_by('code')
    ]
    return JsonResponse({'results': data})


@login_required
def get_course_students(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    students = Student.objects.filter(courses=course, is_active=True).distinct().order_by('first_name', 'last_name')
    data = []
    for student in students:
        data.append({
            'id': student.id,
            'name': student.get_full_name,
            'student_id': student.student_id,
            'email': student.email,
            'year': student.year,
            'is_active': student.is_active,
        })
    return JsonResponse({'students': data})


@login_required
def get_class_students(request, class_id):
    class_obj = get_object_or_404(Class, pk=class_id)
    students = class_obj.enrolled_students.filter(is_active=True).order_by('first_name', 'last_name')
    data = []
    for student in students:
        data.append({
            'id': student.id,
            'name': student.get_full_name,
            'student_id': student.student_id,
            'email': student.email,
            'year': student.year,
            'is_active': student.is_active,
        })
    return JsonResponse({'students': data})


# ==================== ATTENDANCE VIEWS ====================
@login_required
@admin_required
def save_attendance(request, class_id):
    """
    Save attendance for all students in a class.
    Expects JSON data with attendance records.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method. Use POST.'
        })
    
    try:
        class_obj = get_object_or_404(Class, id=class_id)
        
        course = class_obj.courses.first()
        if not course:
            return JsonResponse({
                'success': False,
                'message': 'This class is not associated with any course.'
            })
        
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.first()
            if not teacher:
                from django.contrib.auth.models import User
                system_user, created = User.objects.get_or_create(
                    username='system_admin',
                    defaults={
                        'first_name': 'System',
                        'last_name': 'Admin',
                        'is_staff': True,
                        'is_superuser': True
                    }
                )
                teacher = Teacher.objects.create(
                    user=system_user,
                    teacher_id='SYS001',
                    first_name='System',
                    last_name='Admin',
                    is_active=True
                )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid JSON data: {str(e)}'
            })
        
        attendance_data = data.get('attendance', {})
        attendance_date_str = data.get('date', str(date.today()))
        
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        saved_count = 0
        errors = []
        success_students = []
        
        class_students = class_obj.enrolled_students.filter(is_active=True)
        class_student_ids = list(class_students.values_list('id', flat=True))
        
        if not class_student_ids:
            return JsonResponse({
                'success': False,
                'message': 'No students found in this class.',
                'saved_count': 0,
                'errors': ['No students enrolled in this class.']
            })
        
        for student_id_str, info in attendance_data.items():
            try:
                student_id = int(student_id_str)
                
                try:
                    student = Student.objects.get(id=student_id, is_active=True)
                except Student.DoesNotExist:
                    errors.append(f'Student with ID {student_id} not found or inactive')
                    continue
                
                if not student.classes_enrolled.filter(id=class_obj.id).exists():
                    errors.append(f'Student {student.get_full_name()} is not enrolled in this class')
                    continue
                
                if isinstance(info, dict):
                    status = info.get('status')
                    remark = info.get('remark', '')
                else:
                    status = info
                    remark = ''
                
                if not status:
                    errors.append(f'No status provided for student {student.get_full_name()}')
                    continue
                
                valid_statuses = ['present', 'absent', 'late', 'excused']
                if status not in valid_statuses:
                    errors.append(f'Invalid status "{status}" for student {student.get_full_name()}')
                    continue
                
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    course=course,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remark,
                        'marked_by': teacher
                    }
                )
                
                if not created:
                    attendance.status = status
                    if remark:
                        attendance.remarks = remark
                    attendance.marked_by = teacher
                    attendance.save()
                
                saved_count += 1
                success_students.append(student.get_full_name())
                
            except ValueError as e:
                errors.append(f'Invalid student ID {student_id_str}: {str(e)}')
            except Exception as e:
                errors.append(f'Error for student {student_id_str}: {str(e)}')
        
        if errors:
            return JsonResponse({
                'success': True if saved_count > 0 else False,
                'message': f'Attendance saved for {saved_count} student(s) with {len(errors)} warning(s).',
                'saved_count': saved_count,
                'errors': errors,
                'success_students': success_students,
                'date': attendance_date_str
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'Attendance saved successfully for {saved_count} student(s)!',
                'saved_count': saved_count,
                'success_students': success_students,
                'date': attendance_date_str
            })
        
    except Class.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Class not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error saving attendance: {str(e)}'
        })


@login_required
@admin_required
def save_remark(request, class_pk, student_pk):
    """
    Save a remark for a student's attendance.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.first()
        if not teacher:
            from django.contrib.auth.models import User
            system_user, created = User.objects.get_or_create(
                username='system_admin',
                defaults={
                    'first_name': 'System',
                    'last_name': 'Admin',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            teacher = Teacher.objects.create(
                user=system_user,
                teacher_id='SYS001',
                first_name='System',
                last_name='Admin',
                is_active=True
            )
    
    try:
        data = json.loads(request.body)
        remark = data.get('remark', '')
        attendance_date_str = data.get('date', str(date.today()))
        
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        class_obj = get_object_or_404(Class, pk=class_pk)
        student = get_object_or_404(Student, pk=student_pk)
        
        course = class_obj.courses.first()
        if not course:
            return JsonResponse({'success': False, 'error': 'Class has no associated course'})
        
        attendance = Attendance.objects.filter(
            student=student,
            course=course,
            date=attendance_date
        ).first()
        
        if attendance:
            attendance.remarks = remark
            attendance.marked_by = teacher
            attendance.save()
        else:
            Attendance.objects.create(
                student=student,
                course=course,
                date=attendance_date,
                status='present',
                remarks=remark,
                marked_by=teacher
            )
        
        return JsonResponse({'success': True, 'remark': remark})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== COURSE ATTENDANCE VIEWS ====================
@login_required
@admin_required
def save_course_attendance(request, course_id):
    """
    Save attendance for a course.
    Each student is marked ONCE per course per day.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method. Use POST.'
        })
    
    try:
        course = get_object_or_404(Course, id=course_id)
        
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.first()
            if not teacher:
                from django.contrib.auth.models import User
                system_user, created = User.objects.get_or_create(
                    username='system_admin',
                    defaults={
                        'first_name': 'System',
                        'last_name': 'Admin',
                        'is_staff': True,
                        'is_superuser': True
                    }
                )
                teacher = Teacher.objects.create(
                    user=system_user,
                    teacher_id='SYS001',
                    first_name='System',
                    last_name='Admin',
                    is_active=True
                )
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid JSON data: {str(e)}'
            })
        
        attendance_data = data.get('attendance', {})
        attendance_date_str = data.get('date', str(date.today()))
        
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        saved_count = 0
        errors = []
        success_students = []
        
        # Get all students enrolled in this COURSE
        course_year = course.level[0] if course.level and len(course.level) > 0 else None
        if course_year:
            course_students = Student.objects.filter(
                Q(courses__id=course.id) | Q(classes_enrolled__courses=course),
                year=course_year,
                is_active=True
            ).distinct()
        else:
            course_students = Student.objects.filter(
                Q(courses__id=course.id) | Q(classes_enrolled__courses=course),
                is_active=True
            ).distinct()
        
        if not course_students.exists():
            return JsonResponse({
                'success': False,
                'message': 'No students found in this course.',
                'saved_count': 0,
                'errors': ['No students enrolled in this course.']
            })
        
        for student_id_str, info in attendance_data.items():
            try:
                student_id = int(student_id_str)
                
                try:
                    student = Student.objects.get(id=student_id, is_active=True)
                except Student.DoesNotExist:
                    errors.append(f'Student with ID {student_id} not found or inactive')
                    continue
                
                if not student.courses.filter(id=course.id).exists():
                    errors.append(f'Student {student.get_full_name()} is not enrolled in this course')
                    continue
                
                if isinstance(info, dict):
                    status = info.get('status')
                    remark = info.get('remark', '')
                    time_in = info.get('time_in')
                    time_out = info.get('time_out')
                else:
                    status = info
                    remark = ''
                    time_in = None
                    time_out = None
                
                if not status:
                    errors.append(f'No status provided for student {student.get_full_name()}')
                    continue
                
                valid_statuses = ['present', 'absent', 'late', 'excused']
                if status not in valid_statuses:
                    errors.append(f'Invalid status "{status}" for student {student.get_full_name()}')
                    continue
                
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    course=course,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remark,
                        'marked_by': teacher,
                        'time_in': time_in,
                        'time_out': time_out
                    }
                )
                
                if not created:
                    attendance.status = status
                    if remark:
                        attendance.remarks = remark
                    if time_in:
                        attendance.time_in = time_in
                    if time_out:
                        attendance.time_out = time_out
                    attendance.marked_by = teacher
                    attendance.save()
                
                saved_count += 1
                success_students.append(student.get_full_name())
                
            except ValueError as e:
                errors.append(f'Invalid student ID {student_id_str}: {str(e)}')
            except Exception as e:
                errors.append(f'Error for student {student_id_str}: {str(e)}')
        
        if errors:
            return JsonResponse({
                'success': True if saved_count > 0 else False,
                'message': f'Attendance saved for {saved_count} student(s) with {len(errors)} warning(s).',
                'saved_count': saved_count,
                'errors': errors,
                'success_students': success_students,
                'date': attendance_date_str
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'Attendance saved successfully for {saved_count} student(s)!',
                'saved_count': saved_count,
                'success_students': success_students,
                'date': attendance_date_str
            })
        
    except Course.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Course not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error saving attendance: {str(e)}'
        })


@login_required
@admin_required
def save_course_remark(request, course_pk, student_pk):
    """
    Save a remark for a student's attendance in a course.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        teacher = Teacher.objects.first()
        if not teacher:
            from django.contrib.auth.models import User
            system_user, created = User.objects.get_or_create(
                username='system_admin',
                defaults={
                    'first_name': 'System',
                    'last_name': 'Admin',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            teacher = Teacher.objects.create(
                user=system_user,
                teacher_id='SYS001',
                first_name='System',
                last_name='Admin',
                is_active=True
            )
    
    try:
        data = json.loads(request.body)
        remark = data.get('remark', '')
        attendance_date_str = data.get('date', str(date.today()))
        
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        course = get_object_or_404(Course, pk=course_pk)
        student = get_object_or_404(Student, pk=student_pk)
        
        attendance = Attendance.objects.filter(
            student=student,
            course=course,
            date=attendance_date
        ).first()
        
        if attendance:
            attendance.remarks = remark
            attendance.marked_by = teacher
            attendance.save()
        else:
            Attendance.objects.create(
                student=student,
                course=course,
                date=attendance_date,
                status='present',
                remarks=remark,
                marked_by=teacher
            )
        
        return JsonResponse({'success': True, 'remark': remark})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})