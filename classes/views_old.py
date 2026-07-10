from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from django.http import JsonResponse
import json

from accounts.decorators import admin_required
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
    
    paginator = Paginator(buildings, 10)
    page = request.GET.get('page')
    buildings_page = paginator.get_page(page)
    
    context = {
        'buildings': buildings_page,
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
    
    paginator = Paginator(floors, 10)
    page = request.GET.get('page')
    floors_page = paginator.get_page(page)
    
    context = {
        'floors': floors_page,
        'form': form,
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
    
    paginator = Paginator(rooms, 10)
    page = request.GET.get('page')
    rooms_page = paginator.get_page(page)
    
    total_capacity = sum(room.capacity for room in rooms_page)
    
    context = {
        'rooms': rooms_page,
        'form': form,
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
    
    paginator = Paginator(terms, 10)
    page = request.GET.get('page')
    terms_page = paginator.get_page(page)
    
    context = {
        'terms': terms_page,
        'total': Term.objects.count(),
        'active': Term.objects.filter(is_active=True).count(),
        'inactive': Term.objects.filter(is_active=False).count(),
        'current': Term.objects.filter(is_current=True).count(),
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
        form = TermForm()
    
    return render(request, 'Backend/admin/academic/term_form.html', {'form': form, 'title': 'Add Term'})


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
        form = TermForm(instance=term)
    
    return render(request, 'Backend/admin/academic/term_form.html', {'form': form, 'term': term, 'title': 'Edit Term', 'is_edit': True})


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
    
    paginator = Paginator(slots, 10)
    page = request.GET.get('page')
    slots_page = paginator.get_page(page)
    
    context = {
        'timeslots': slots_page,
        'total': TimeSlot.objects.count(),
        'active': TimeSlot.objects.filter(is_active=True).count(),
        'inactive': TimeSlot.objects.filter(is_active=False).count(),
    }
    return render(request, 'Backend/admin/academic/timeslot_list.html', context)


@login_required
@admin_required
def timeslot_add(request):
    if request.method == 'POST':
        selected_days = request.POST.getlist('days')
        slot_type = request.POST.get('slot_type')
        
        if not selected_days:
            messages.error(request, 'Please select at least one day.')
            return render(request, 'Backend/admin/academic/timeslot_form.html', {
                'form': TimeSlotForm(),
                'title': 'Add Time Slot',
                'selected_days': []
            })
        
        days_str = ','.join(selected_days)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            time_slot = TimeSlot.objects.create(
                days=days_str,
                start_time=start_time,
                end_time=end_time,
                slot_type=slot_type or 'custom',
                name=name,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'✅ Time slot added successfully for {time_slot.get_days_display()}!')
            return redirect('classes:timeslot_list')
        except Exception as e:
            messages.error(request, f'Error creating time slot: {str(e)}')
    else:
        form = TimeSlotForm()
    
    return render(request, 'Backend/admin/academic/timeslot_form.html', {
        'form': form,
        'title': 'Add Time Slot',
        'selected_days': []
    })


@login_required
@admin_required
def timeslot_edit(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    selected_days = slot.get_days_list()
    
    if request.method == 'POST':
        selected_days = request.POST.getlist('days')
        slot_type = request.POST.get('slot_type')
        
        if not selected_days:
            messages.error(request, 'Please select at least one day.')
            return render(request, 'Backend/admin/academic/timeslot_form.html', {
                'form': TimeSlotForm(instance=slot),
                'timeslot': slot,
                'title': 'Edit Time Slot',
                'is_edit': True,
                'selected_days': selected_days
            })
        
        days_str = ','.join(selected_days)
        slot.days = days_str
        slot.start_time = request.POST.get('start_time')
        slot.end_time = request.POST.get('end_time')
        slot.slot_type = slot_type or 'custom'
        slot.name = request.POST.get('name')
        slot.description = request.POST.get('description')
        slot.is_active = request.POST.get('is_active') == 'on'
        slot.save()
        
        messages.success(request, f'✅ Time slot updated successfully for {slot.get_days_display()}!')
        return redirect('classes:timeslot_list')
    
    form = TimeSlotForm(instance=slot)
    return render(request, 'Backend/admin/academic/timeslot_form.html', {
        'form': form,
        'timeslot': slot,
        'title': 'Edit Time Slot',
        'is_edit': True,
        'selected_days': selected_days
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
    
    paginator = Paginator(classes, 10)
    page = request.GET.get('page')
    classes_page = paginator.get_page(page)
    
    context = {
        'classes': classes_page,
        'form': form,
        'total_classes': total_classes,
        'active_classes': active_classes,
        'inactive_classes': inactive_classes,
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
    
    context = {
        'form': form,
        'title': 'Add New Class',
        'is_edit': False,
        # Pass data for dropdowns
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
    
    context = {
        'form': form,
        'title': 'Edit Class',
        'class': class_obj,
        'is_edit': True,
        # ===== ADD THESE FOR DROPDOWNS =====
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
    students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
    
    today = date.today()
    for student in students:
        att = Attendance.objects.filter(student=student, class_obj=class_obj, date=today).first()
        student.attendance_status = att.status if att else None
    
    total_students = students.count()
    present_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='present').count()
    absent_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='absent').count()
    late_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='late').count()
    excused_count = Attendance.objects.filter(class_obj=class_obj, date=today, status='excused').count()
    
    present_percentage = attendance_rate_percent(present_count, total_students)
    
    context = {
        'class': class_obj,
        'students': students,
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
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                if not student.class_enrolled or student.class_enrolled != class_obj:
                    student.class_enrolled = class_obj
                    student.save()
                    added_count += 1
            except Student.DoesNotExist:
                continue
        
        if added_count > 0:
            messages.success(request, f'{added_count} student(s) added to "{class_obj.name}" successfully!')
        else:
            messages.warning(request, 'No students were added.')
        return redirect('classes:class_detail', pk=class_obj.pk)
    
    available_students = Student.objects.filter(is_active=True).exclude(class_enrolled=class_obj)
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
        student.class_enrolled = None
        student.save()
        messages.success(request, f'Student "{student.get_full_name()}" removed from "{class_obj.name}" successfully!')
        return redirect('classes:class_detail', pk=class_obj.pk)
    
    context = {
        'class': class_obj,
        'student': student,
    }
    return render(request, 'Backend/admin/class/remove_student.html', context)

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


# ==================== ATTENDANCE VIEWS ====================
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date
from accounts.decorators import admin_required
from .models import Class
from attendance.models import Attendance
from students.models import Student


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
        # Get the class
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Get or create a teacher for the admin
        try:
            # Try to get teacher associated with the user
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            # If user is admin but not a teacher, create a system teacher or use existing
            teacher = Teacher.objects.first()
            if not teacher:
                # Create a system admin teacher
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
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid JSON data: {str(e)}'
            })
        
        attendance_data = data.get('attendance', {})
        attendance_date_str = data.get('date', str(date.today()))
        
        # Parse date
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        saved_count = 0
        errors = []
        success_students = []
        
        # Get all students in this class for validation
        class_students = Student.objects.filter(class_enrolled=class_obj, is_active=True)
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
                
                # Try to find the student
                try:
                    student = Student.objects.get(id=student_id, is_active=True)
                except Student.DoesNotExist:
                    errors.append(f'Student with ID {student_id} not found or inactive')
                    continue
                
                # Check if student is in this class
                if student.class_enrolled != class_obj:
                    errors.append(f'Student {student.get_full_name()} is not enrolled in this class')
                    continue
                
                status = info.get('status')
                remark = info.get('remark', '')
                
                if not status:
                    errors.append(f'No status provided for student {student.get_full_name()}')
                    continue
                
                # Check if status is valid
                valid_statuses = ['present', 'absent', 'late', 'excused']
                if status not in valid_statuses:
                    errors.append(f'Invalid status "{status}" for student {student.get_full_name()}')
                    continue
                
                # Check if attendance already exists for this student, class, and date
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    class_obj=class_obj,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'remarks': remark,
                        'marked_by': teacher
                    }
                )
                
                # If attendance already exists, update it
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
        
        # Prepare response
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
        # Get or create a teacher for the admin
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
        
        data = json.loads(request.body)
        remark = data.get('remark', '')
        attendance_date_str = data.get('date', str(date.today()))
        
        # Parse date
        try:
            attendance_date = date.fromisoformat(attendance_date_str)
        except ValueError:
            attendance_date = date.today()
        
        class_obj = get_object_or_404(Class, pk=class_pk)
        student = get_object_or_404(Student, pk=student_pk)
        
        # Check if attendance exists for today
        attendance = Attendance.objects.filter(
            student=student,
            class_obj=class_obj,
            date=attendance_date
        ).first()
        
        if attendance:
            attendance.remarks = remark
            attendance.marked_by = teacher
            attendance.save()
        else:
            # Create attendance with remark if it doesn't exist
            Attendance.objects.create(
                student=student,
                class_obj=class_obj,
                date=attendance_date,
                status='present',
                remarks=remark,
                marked_by=teacher
            )
        
        return JsonResponse({'success': True, 'remark': remark})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
