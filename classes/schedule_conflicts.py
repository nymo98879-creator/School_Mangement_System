# # def normalize_academic_year(academic_year=None, term=None):
# #     year = (academic_year or '').strip()
# #     if not year and term:
# #         year = (getattr(term, 'academic_year', '') or '').strip()
# #     return year


# # def split_days(days):
# #     return [day.strip().lower() for day in (days or '').split(',') if day.strip()]


# # def build_slot_entries(time_slots=None, start_time=None, end_time=None, days=None):
# #     entries = []

# #     if time_slots:
# #         for slot in time_slots:
# #             slot_days = split_days(slot.days)
# #             if slot_days and slot.start_time and slot.end_time:
# #                 entries.append((slot_days, slot.start_time, slot.end_time, str(slot)))

# #     if start_time and end_time and days:
# #         days_list = split_days(days)
# #         if days_list:
# #             time_text = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
# #             entries.append((days_list, start_time, end_time, f"{days} {time_text}"))

# #     return entries


# # def class_slot_entries(class_obj):
# #     time_slots = class_obj.time_slots.all() if class_obj.pk else []
# #     return build_slot_entries(
# #         time_slots=time_slots,
# #         start_time=class_obj.start_time,
# #         end_time=class_obj.end_time,
# #         days=class_obj.days,
# #     )


# # def slots_overlap(first, second):
# #     first_days, first_start, first_end, _ = first
# #     second_days, second_start, second_end, _ = second
# #     day_overlap = any(day in second_days for day in first_days)
# #     time_overlap = first_start < second_end and first_end > second_start
# #     return day_overlap and time_overlap


# # def find_course_schedule_conflict(course, academic_year, slot_entries, exclude_pk=None):
# #     if not course or not academic_year or not slot_entries:
# #         return None

# #     from .models import Class

# #     other_classes = Class.objects.filter(
# #         course=course,
# #         academic_year=academic_year,
# #         is_active=True,
# #     )
# #     if exclude_pk:
# #         other_classes = other_classes.exclude(pk=exclude_pk)

# #     for other in other_classes:
# #         for current_slot in slot_entries:
# #             for other_slot in class_slot_entries(other):
# #                 if slots_overlap(current_slot, other_slot):
# #                     return other, other_slot[3]

# #     return None


# # def find_teacher_schedule_conflict(teacher, academic_year, slot_entries, exclude_pk=None):
# #     if not teacher or not academic_year or not slot_entries:
# #         return None

# #     from .models import Class

# #     other_classes = Class.objects.filter(
# #         teacher=teacher,
# #         academic_year=academic_year,
# #         is_active=True,
# #     )
# #     if exclude_pk:
# #         other_classes = other_classes.exclude(pk=exclude_pk)

# #     for other in other_classes:
# #         for current_slot in slot_entries:
# #             for other_slot in class_slot_entries(other):
# #                 if slots_overlap(current_slot, other_slot):
# #                     return other, other_slot[3]

# #     return None


# from datetime import datetime


# def normalize_academic_year(academic_year, term):
#     """Return a consistent academic-year string to compare across classes."""
#     if academic_year:
#         return academic_year.strip()
#     if term and getattr(term, 'academic_year', None):
#         return term.academic_year.strip()
#     return None


# def _parse_days(days_str):
#     return {d.strip().lower() for d in (days_str or '').split(',') if d.strip()}


# def slot_entries_from_time_slots(time_slots_qs):
#     """Convert a queryset/list of TimeSlot into (day, start_time, end_time) tuples."""
#     entries = []
#     for slot in time_slots_qs:
#         for day in _parse_days(slot.days):
#             entries.append((day, slot.start_time, slot.end_time))
#     return entries


# def class_slot_entries(class_instance):
#     """Get (day, start_time, end_time) entries for a saved Class instance."""
#     return slot_entries_from_time_slots(class_instance.time_slots.all())


# def entries_overlap(entries_a, entries_b):
#     """True if any entry in entries_a overlaps any entry in entries_b (same day, times cross)."""
#     for day_a, start_a, end_a in entries_a:
#         for day_b, start_b, end_b in entries_b:
#             if day_a != day_b:
#                 continue
#             if start_a < end_b and start_b < end_a:
#                 return True
#     return False


# def find_course_schedule_conflict(course, academic_year, slot_entries, exclude_pk=None):
#     """
#     Check if `course` is already assigned to another active Class in the same
#     academic_year with overlapping slot_entries. Returns (other_class, schedule_str) or None.
#     """
#     from .models import Class

#     if not academic_year or not slot_entries:
#         return None

#     candidates = Class.objects.filter(
#         courses=course,
#         academic_year=academic_year,
#         is_active=True,
#     ).distinct()

#     if exclude_pk:
#         candidates = candidates.exclude(pk=exclude_pk)

#     for other in candidates:
#         other_entries = class_slot_entries(other)
#         if entries_overlap(slot_entries, other_entries):
#             return other, other.get_schedule_display()

#     return None


# def find_teacher_schedule_conflict(teacher, academic_year, slot_entries, exclude_pk=None):
#     """
#     Check if `teacher` is already assigned to another active Class in the same
#     academic_year with overlapping slot_entries. Returns (other_class, schedule_str) or None.
#     """
#     from .models import Class

#     if not academic_year or not slot_entries or not teacher:
#         return None

#     candidates = Class.objects.filter(
#         teacher=teacher,
#         academic_year=academic_year,
#         is_active=True,
#     ).distinct()

#     if exclude_pk:
#         candidates = candidates.exclude(pk=exclude_pk)

#     for other in candidates:
#         other_entries = class_slot_entries(other)
#         if entries_overlap(slot_entries, other_entries):
#             return other, other.get_schedule_display()

#     return None


from datetime import datetime


def normalize_academic_year(academic_year, term):
    """Return a consistent academic-year string to compare across classes."""
    if academic_year:
        return academic_year.strip()
    if term and getattr(term, 'academic_year', None):
        return term.academic_year.strip()
    return None


def _parse_days(days_str):
    return {d.strip().lower() for d in (days_str or '').split(',') if d.strip()}


def slot_entries_from_time_slots(time_slots_qs):
    """Convert a queryset/list of TimeSlot into (day, start_time, end_time) tuples."""
    entries = []
    for slot in time_slots_qs:
        for day in _parse_days(slot.days):
            entries.append((day, slot.start_time, slot.end_time))
    return entries


def build_slot_entries(time_slots):
    """Alias used by views.py — same as slot_entries_from_time_slots."""
    return slot_entries_from_time_slots(time_slots)


def class_slot_entries(class_instance):
    """Get (day, start_time, end_time) entries for a saved Class instance."""
    return slot_entries_from_time_slots(class_instance.time_slots.all())


def entries_overlap(entries_a, entries_b):
    """True if any entry in entries_a overlaps any entry in entries_b (same day, times cross)."""
    for day_a, start_a, end_a in entries_a:
        for day_b, start_b, end_b in entries_b:
            if day_a != day_b:
                continue
            if start_a < end_b and start_b < end_a:
                return True
    return False


def find_course_schedule_conflict(course, academic_year, slot_entries, exclude_pk=None):
    """
    Check if `course` is already assigned to another active Class in the same
    academic_year with overlapping slot_entries. Returns (other_class, schedule_str) or None.
    """
    from .models import Class

    if not academic_year or not slot_entries:
        return None

    candidates = Class.objects.filter(
        courses=course,
        academic_year=academic_year,
        is_active=True,
    ).distinct()

    if exclude_pk:
        candidates = candidates.exclude(pk=exclude_pk)

    for other in candidates:
        other_entries = class_slot_entries(other)
        if entries_overlap(slot_entries, other_entries):
            return other, other.get_schedule_display()

    return None


def find_teacher_schedule_conflict(teacher, academic_year, slot_entries, exclude_pk=None):
    """
    Check if `teacher` is already assigned to another active Class in the same
    academic_year with overlapping slot_entries. Returns (other_class, schedule_str) or None.
    """
    from .models import Class

    if not academic_year or not slot_entries or not teacher:
        return None

    candidates = Class.objects.filter(
        teacher=teacher,
        academic_year=academic_year,
        is_active=True,
    ).distinct()

    if exclude_pk:
        candidates = candidates.exclude(pk=exclude_pk)

    for other in candidates:
        other_entries = class_slot_entries(other)
        if entries_overlap(slot_entries, other_entries):
            return other, other.get_schedule_display()

    return None
