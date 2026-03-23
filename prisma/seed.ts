// @ts-nocheck
import { PrismaClient } from '@prisma/client';
import { faker } from '@faker-js/faker';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('⏳ Starting Matrix Population... Please wait.');

  // Shared secure password for all dummy users to speed up seeding
  const defaultPassword = await bcrypt.hash('password123', 10);

  // 1. GENERATE 50 TEACHERS
  console.log('👨‍🏫 Generating 50 Teachers...');
  const teachers = [];
  for (let i = 0; i < 50; i++) {
    const tUser = await prisma.user.create({
      data: {
        email: faker.internet.email({ provider: 'faculty.school.os' }),
        password: defaultPassword,
        role: 'TEACHER',
        teacher: { create: { name: faker.person.fullName() } }
      },
      include: { teacher: true }
    });
    // @ts-ignore
    teachers.push(tUser.teacher);
  }

  // 2. GENERATE 20 CLASSES
  console.log('🏫 Generating 20 Classes...');
  const classes = [];
  const grades = ['10', '11', '12', 'CS', 'ENG', 'BIO', 'ART'];
  for (let i = 0; i < 20; i++) {
    const randomTeacher = faker.helpers.arrayElement(teachers);
    const cls = await prisma.class.create({
      data: {
        name: `${faker.helpers.arrayElement(grades)}-${faker.string.numeric(3)}`,
        teacherId: randomTeacher.id
      }
    });
    classes.push(cls);
  }

  // 3. GENERATE SUBJECTS FOR EACH CLASS
  console.log('📚 Generating Subjects & Curriculum...');
  const subjects = [];
  const subjectNames = ['Advanced Physics', 'Calculus', 'World History', 'Literature', 'Computer Science', 'Organic Chemistry', 'Art History'];
  for (const c of classes) {
    // 3 subjects per class
    for (let i = 0; i < 3; i++) {
      const sub = await prisma.subject.create({
        data: {
          name: faker.helpers.arrayElement(subjectNames),
          code: faker.string.alphanumeric(6).toUpperCase(),
          classId: c.id,
          teacherId: faker.helpers.arrayElement(teachers).id
        }
      });
      subjects.push(sub);
    }
  }

  // 4. GENERATE 110 STUDENTS (Multi-Class Assigned)
  console.log('🎓 Generating 110 Students...');
  const students = [];
  for (let i = 0; i < 110; i++) {
    // Randomly assign 2 to 4 classes per student
    const numClasses = faker.number.int({ min: 2, max: 4 });
    const assignedClasses = faker.helpers.arrayElements(classes, numClasses).map(c => ({ id: c.id }));

    const sUser = await prisma.user.create({
      data: {
        email: faker.internet.email({ provider: 'student.school.os' }),
        password: defaultPassword,
        role: 'STUDENT',
        student: {
          create: {
            name: faker.person.fullName(),
            classes: { connect: assignedClasses }
          }
        }
      },
      include: { student: true }
    });
    // @ts-ignore
    students.push(sUser.student);
  }

  // 5. GENERATE EXAMINATIONS AND GRADES
  console.log('📝 Generating Exams and Grading Matrix...');
  for (const sub of subjects) {
    // Create an exam for this subject
    const exam = await prisma.exam.create({
      data: {
        title: `${sub.name} Mid-Term Assessment`,
        date: faker.date.recent({ days: 45 }),
        subjectId: sub.id
      }
    });

    // Find all students enrolled in the class that holds this subject
    const enrolledStudents = await prisma.student.findMany({
      where: { classes: { some: { id: sub.classId } } }
    });

    // Generate grades for these students
    const gradesData = enrolledStudents.map(st => ({
      studentId: st.id,
      examId: exam.id,
      score: faker.number.float({ min: 45, max: 100, fractionDigits: 1 }),
      remarks: faker.helpers.arrayElement(['Excellent', 'Good progress', 'Needs focus', 'Outstanding'])
    }));

    if (gradesData.length > 0) {
      await prisma.grade.createMany({ data: gradesData });
    }
  }

  // 6. GENERATE 30-DAY ATTENDANCE HISTORY (Approx 3,300 Records)
  console.log('📅 Generating 30-Day Attendance Logs (This might take a moment)...');
  const attendanceData = [];
  const statuses = ['PRESENT', 'PRESENT', 'PRESENT', 'PRESENT', 'PRESENT', 'ABSENT', 'LEAVE']; // High probability of being Present
  
  for (const st of students) {
    for (let i = 0; i < 30; i++) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      d.setHours(12, 0, 0, 0);

      attendanceData.push({
        studentId: st.id,
        date: d,
        status: faker.helpers.arrayElement(statuses),
        confidence: 1.0
      });
    }
  }

  // Chunk inserts for database safety
  const chunkSize = 1000;
  for (let i = 0; i < attendanceData.length; i += chunkSize) {
    await prisma.attendance.createMany({ data: attendanceData.slice(i, i + chunkSize) });
  }

  console.log('✅ MATRIX FULLY POPULATED! System Ready.');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
