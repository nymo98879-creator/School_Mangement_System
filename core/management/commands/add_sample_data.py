# core/management/commands/add_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Add sample data to all tables without clearing existing data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('📝 Adding sample data...'))
        
        # Import models
        from classes.models import Building, Floor, Room, Term, TimeSlot, Class
        from teachers.models import Teacher
        from students.models import Student
        from courses.models import Faculty, Department, Major, Course
        from attendance.models import Attendance
        
        try:
            # ============================================
            # 1. BUILDING
            # ============================================
            building, created = Building.objects.get_or_create(
                code='MB-01',
                defaults={
                    'name': 'Main Building',
                    'address': '123 University Street, City Center',
                    'description': 'Main academic building with classrooms and labs',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Building: {building.name}')

            building2, created = Building.objects.get_or_create(
                code='LB-02',
                defaults={
                    'name': 'Library Building',
                    'address': '456 Knowledge Avenue',
                    'description': 'University Library and Study Center',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Building: {building2.name}')

            building3, created = Building.objects.get_or_create(
                code='SB-03',
                defaults={
                    'name': 'Science Building',
                    'address': '789 Research Boulevard',
                    'description': 'Science laboratories and research facilities',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Building: {building3.name}')

            # ============================================
            # 2. FLOOR
            # ============================================
            floor1, created = Floor.objects.get_or_create(
                building=building,
                floor_number='1',
                defaults={
                    'name': 'First Floor',
                    'description': 'Main floor with classrooms',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Floor: {floor1.floor_number}')

            floor2, created = Floor.objects.get_or_create(
                building=building,
                floor_number='2',
                defaults={
                    'name': 'Second Floor',
                    'description': 'Upper floor with computer labs',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Floor: {floor2.floor_number}')

            # ============================================
            # 3. ROOM
            # ============================================
            room1, created = Room.objects.get_or_create(
                building=building,
                room_number='101',
                defaults={
                    'floor': floor1,
                    'name': 'Lecture Hall 101',
                    'room_type': 'classroom',
                    'capacity': 40,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Room: {room1.room_number}')

            room2, created = Room.objects.get_or_create(
                building=building,
                room_number='102',
                defaults={
                    'floor': floor1,
                    'name': 'Lecture Hall 102',
                    'room_type': 'classroom',
                    'capacity': 35,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Room: {room2.room_number}')

            room3, created = Room.objects.get_or_create(
                building=building,
                room_number='201',
                defaults={
                    'floor': floor2,
                    'name': 'Computer Lab 201',
                    'room_type': 'computer_lab',
                    'capacity': 25,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Room: {room3.room_number}')

            # ============================================
            # 4. TERM
            # ============================================
            term1, created = Term.objects.get_or_create(
                name='Fall Semester 2024',
                defaults={
                    'term_type': 'fall',
                    'academic_year': '2024-2025',
                    'start_date': date(2024, 9, 1),
                    'end_date': date(2024, 12, 20),
                    'is_active': True,
                    'is_current': True,
                    'description': 'Fall Semester 2024-2025 Academic Year'
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Term: {term1.name}')

            term2, created = Term.objects.get_or_create(
                name='Spring Semester 2025',
                defaults={
                    'term_type': 'spring',
                    'academic_year': '2024-2025',
                    'start_date': date(2025, 1, 10),
                    'end_date': date(2025, 4, 30),
                    'is_active': True,
                    'is_current': False,
                    'description': 'Spring Semester 2024-2025 Academic Year'
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Term: {term2.name}')

            # ============================================
            # 5. TIME SLOT
            # ============================================
            timeslot1, created = TimeSlot.objects.get_or_create(
                days='monday,wednesday,friday',
                start_time='09:00:00',
                end_time='10:30:00',
                defaults={
                    'slot_type': 'morning',
                    'name': 'Morning Session MWF',
                    'description': 'Monday, Wednesday, Friday 9:00 AM - 10:30 AM',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Time Slot: {timeslot1.name}')

            timeslot2, created = TimeSlot.objects.get_or_create(
                days='tuesday,thursday',
                start_time='10:30:00',
                end_time='12:00:00',
                defaults={
                    'slot_type': 'morning',
                    'name': 'Morning Session TTh',
                    'description': 'Tuesday, Thursday 10:30 AM - 12:00 PM',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Time Slot: {timeslot2.name}')

            timeslot3, created = TimeSlot.objects.get_or_create(
                days='monday,wednesday,friday',
                start_time='13:00:00',
                end_time='14:30:00',
                defaults={
                    'slot_type': 'afternoon',
                    'name': 'Afternoon Session MWF',
                    'description': 'Monday, Wednesday, Friday 1:00 PM - 2:30 PM',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Time Slot: {timeslot3.name}')

            # ============================================
            # 6. FACULTY
            # ============================================
            faculty1, created = Faculty.objects.get_or_create(
                code='FST',
                defaults={
                    'name': 'Faculty of Science and Technology',
                    'description': 'Science and Technology Faculty - Home to Computer Science, Engineering, and Mathematics',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Faculty: {faculty1.name}')

            faculty2, created = Faculty.objects.get_or_create(
                code='FBA',
                defaults={
                    'name': 'Faculty of Business and Administration',
                    'description': 'Business and Administration Faculty - Home to Management, Finance, and Marketing',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Faculty: {faculty2.name}')

            faculty3, created = Faculty.objects.get_or_create(
                code='FAS',
                defaults={
                    'name': 'Faculty of Arts and Sciences',
                    'description': 'Arts and Sciences Faculty - Home to Humanities, Social Sciences, and Natural Sciences',
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Faculty: {faculty3.name}')

            # ============================================
            # 7. DEPARTMENT
            # ============================================
            dept1, created = Department.objects.get_or_create(
                code='CS',
                defaults={
                    'name': 'Computer Science Department',
                    'description': 'Department of Computer Science - Programming, AI, and Software Engineering',
                    'faculty': faculty1,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Department: {dept1.name}')

            dept2, created = Department.objects.get_or_create(
                code='MATH',
                defaults={
                    'name': 'Mathematics Department',
                    'description': 'Department of Mathematics - Pure and Applied Mathematics',
                    'faculty': faculty1,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Department: {dept2.name}')

            dept3, created = Department.objects.get_or_create(
                code='MGT',
                defaults={
                    'name': 'Management Department',
                    'description': 'Department of Management - Business Administration and Leadership',
                    'faculty': faculty2,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Department: {dept3.name}')

            # ============================================
            # 8. MAJOR
            # ============================================
            major1, created = Major.objects.get_or_create(
                code='BSCS',
                defaults={
                    'name': 'Bachelor of Science in Computer Science',
                    'degree_type': 'bachelor',
                    'description': 'Comprehensive program in Computer Science covering programming, algorithms, and systems',
                    'department': dept1,
                    'duration': 4,
                    'total_credits': 120,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Major: {major1.name}')

            major2, created = Major.objects.get_or_create(
                code='BSMATH',
                defaults={
                    'name': 'Bachelor of Science in Mathematics',
                    'degree_type': 'bachelor',
                    'description': 'Program in Pure and Applied Mathematics',
                    'department': dept2,
                    'duration': 4,
                    'total_credits': 120,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Major: {major2.name}')

            major3, created = Major.objects.get_or_create(
                code='MBA',
                defaults={
                    'name': 'Master of Business Administration',
                    'degree_type': 'master',
                    'description': 'Professional MBA program',
                    'department': dept3,
                    'duration': 2,
                    'total_credits': 60,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Major: {major3.name}')

            # ============================================
            # 9. COURSE
            # ============================================
            course1, created = Course.objects.get_or_create(
                code='CS101',
                defaults={
                    'course_id': 'CS101',
                    'name': 'Introduction to Programming',
                    'description': 'Basic programming concepts using Python',
                    'credits': 3,
                    'level': '100',
                    'duration': '16 weeks',
                    'fee': 500.00,
                    'major': major1,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Course: {course1.name}')

            course2, created = Course.objects.get_or_create(
                code='CS201',
                defaults={
                    'course_id': 'CS201',
                    'name': 'Data Structures and Algorithms',
                    'description': 'Advanced programming concepts and algorithms',
                    'credits': 3,
                    'level': '200',
                    'duration': '16 weeks',
                    'fee': 550.00,
                    'major': major1,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Course: {course2.name}')

            course3, created = Course.objects.get_or_create(
                code='MATH101',
                defaults={
                    'course_id': 'MATH101',
                    'name': 'Calculus I',
                    'description': 'Differential and Integral Calculus',
                    'credits': 4,
                    'level': '100',
                    'duration': '16 weeks',
                    'fee': 450.00,
                    'major': major2,
                    'is_active': True
                }
            )
            self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Course: {course3.name}')

            # Add prerequisites
            if created:
                course2.prerequisites.add(course1)
                self.stdout.write(f'✅ Added prerequisite: {course1.name} -> {course2.name}')

            # ============================================
            # 10. GET OR CREATE TEACHER
            # ============================================
            # Get first user for teacher
            first_user = User.objects.first()
            if first_user:
                teacher, created = Teacher.objects.get_or_create(
                    user=first_user,
                    defaults={
                        'teacher_id': f'TCH-{first_user.id:04d}',
                        'first_name': first_user.first_name or 'John',
                        'last_name': first_user.last_name or 'Doe',
                        'date_of_birth': date(1980, 1, 1),
                        'gender': 'M',
                        'phone': '+1234567890',
                        'email': first_user.email or 'teacher@example.com',
                        'qualification': 'Ph.D. in Computer Science',
                        'specialization': 'Artificial Intelligence',
                        'years_of_experience': 10,
                        'position': 'professor',
                        'hired_date': date(2020, 1, 1),
                        'is_active': True
                    }
                )
                self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Teacher: {teacher.get_full_name()}')
            else:
                teacher = None
                self.stdout.write(self.style.WARNING('⚠️ No users found. Create a user first.'))

            # ============================================
            # 11. CLASS
            # ============================================
            class1, created = Class.objects.get_or_create(
                code='CS101-A',
                defaults={
                    'name': 'Programming Fundamentals',
                    'section': 'A',
                    'building': building,
                    'floor': floor1,
                    'room': room1,
                    'room_number': '101',
                    'term': term1,
                    'academic_year': '2024-2025',
                    'capacity': 30,
                    'teacher': teacher,
                    'course': course1,
                    'start_date': date(2024, 9, 1),
                    'end_date': date(2024, 12, 20),
                    'is_active': True
                }
            )
            if created:
                class1.time_slots.add(timeslot1)
                self.stdout.write(f'✅ Created Class: {class1.name}')
            else:
                self.stdout.write(f'✅ Found Class: {class1.name}')

            class2, created = Class.objects.get_or_create(
                code='CS201-A',
                defaults={
                    'name': 'Data Structures',
                    'section': 'A',
                    'building': building,
                    'floor': floor2,
                    'room': room3,
                    'room_number': '201',
                    'term': term1,
                    'academic_year': '2024-2025',
                    'capacity': 25,
                    'teacher': teacher,
                    'course': course2,
                    'start_date': date(2024, 9, 1),
                    'end_date': date(2024, 12, 20),
                    'is_active': True
                }
            )
            if created:
                class2.time_slots.add(timeslot2)
                self.stdout.write(f'✅ Created Class: {class2.name}')
            else:
                self.stdout.write(f'✅ Found Class: {class2.name}')

            # ============================================
            # 12. STUDENT
            # ============================================
            if first_user:
                student, created = Student.objects.get_or_create(
                    user=first_user,
                    defaults={
                        'student_id': f'STU-{first_user.id:04d}',
                        'first_name': first_user.first_name or 'Jane',
                        'last_name': first_user.last_name or 'Smith',
                        'date_of_birth': date(2000, 1, 1),
                        'gender': 'F',
                        'phone': '+9876543210',
                        'email': first_user.email or 'student@example.com',
                        'address': '456 Student Street, University City',
                        'guardian_name': 'John Smith',
                        'guardian_phone': '+1234567890',
                        'guardian_email': 'guardian@example.com',
                        'major': major1,
                        'class_enrolled': class1,
                        'is_active': True
                    }
                )
                self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Student: {student.get_full_name()}')

                # ============================================
                # 13. ATTENDANCE
                # ============================================
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    class_obj=class1,
                    date=date.today(),
                    defaults={
                        'status': 'present',
                        'marked_by': teacher
                    }
                )
                self.stdout.write(f'{"✅ Created" if created else "✅ Found"} Attendance for {student.get_full_name()}')

            # ============================================
            # Summary
            # ============================================
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS('✅ SAMPLE DATA ADDED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('='*50))
            self.stdout.write(f'📊 Summary:')
            self.stdout.write(f'   - Buildings: {Building.objects.count()}')
            self.stdout.write(f'   - Floors: {Floor.objects.count()}')
            self.stdout.write(f'   - Rooms: {Room.objects.count()}')
            self.stdout.write(f'   - Terms: {Term.objects.count()}')
            self.stdout.write(f'   - Time Slots: {TimeSlot.objects.count()}')
            self.stdout.write(f'   - Faculties: {Faculty.objects.count()}')
            self.stdout.write(f'   - Departments: {Department.objects.count()}')
            self.stdout.write(f'   - Majors: {Major.objects.count()}')
            self.stdout.write(f'   - Courses: {Course.objects.count()}')
            self.stdout.write(f'   - Teachers: {Teacher.objects.count()}')
            self.stdout.write(f'   - Classes: {Class.objects.count()}')
            self.stdout.write(f'   - Students: {Student.objects.count()}')
            self.stdout.write(f'   - Attendance: {Attendance.objects.count()}')
            self.stdout.write(self.style.SUCCESS('='*50))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error adding sample data: {str(e)}'))