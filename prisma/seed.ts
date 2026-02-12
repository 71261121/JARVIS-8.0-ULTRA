/**
 * JARVIS 8.0 ULTRA - Database Seed Script
 * Seeds initial data for subjects, topics, questions, and achievements
 */

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create Subjects
  const subjects = await Promise.all([
    prisma.subject.upsert({
      where: { code: 'mathematics' },
      update: {},
      create: {
        name: 'Mathematics',
        code: 'mathematics',
        totalMarks: 20,
        priority: 1
      }
    }),
    prisma.subject.upsert({
      where: { code: 'physics' },
      update: {},
      create: {
        name: 'Physics',
        code: 'physics',
        totalMarks: 15,
        priority: 2
      }
    }),
    prisma.subject.upsert({
      where: { code: 'chemistry' },
      update: {},
      create: {
        name: 'Chemistry',
        code: 'chemistry',
        totalMarks: 8,
        priority: 3
      }
    }),
    prisma.subject.upsert({
      where: { code: 'english' },
      update: {},
      create: {
        name: 'English',
        code: 'english',
        totalMarks: 7,
        priority: 4
      }
    })
  ]);

  console.log(`✅ Created ${subjects.length} subjects`);

  // Create Topics for Mathematics
  const mathsTopics = [
    { name: 'Matrices', code: 'matrices', importance: 0.9, frequency: 0.8 },
    { name: 'Determinants', code: 'determinants', importance: 0.85, frequency: 0.75 },
    { name: 'Limits and Continuity', code: 'limits', importance: 0.8, frequency: 0.7 },
    { name: 'Differentiation', code: 'differentiation', importance: 0.9, frequency: 0.85 },
    { name: 'Integration', code: 'integration', importance: 0.85, frequency: 0.8 },
    { name: 'Probability', code: 'probability', importance: 0.75, frequency: 0.7 },
    { name: 'Permutations & Combinations', code: 'pnc', importance: 0.7, frequency: 0.65 },
    { name: 'Complex Numbers', code: 'complex', importance: 0.65, frequency: 0.6 },
    { name: 'Quadratic Equations', code: 'quadratic', importance: 0.7, frequency: 0.65 },
    { name: 'Sequences and Series', code: 'sequences', importance: 0.6, frequency: 0.55 },
    { name: 'Trigonometry', code: 'trigonometry', importance: 0.75, frequency: 0.7 },
    { name: 'Coordinate Geometry', code: 'coordinate', importance: 0.8, frequency: 0.75 }
  ];

  const maths = subjects.find(s => s.code === 'mathematics')!;
  
  for (const topic of mathsTopics) {
    await prisma.topic.upsert({
      where: { 
        subjectId_code: { subjectId: maths.id, code: topic.code }
      },
      update: {},
      create: {
        name: topic.name,
        code: topic.code,
        subjectId: maths.id,
        importance: topic.importance,
        frequency: topic.frequency
      }
    });
  }

  // Create Topics for Physics
  const physicsTopics = [
    { name: 'Mechanics', code: 'mechanics', importance: 0.9, frequency: 0.85 },
    { name: 'Kinematics', code: 'kinematics', importance: 0.85, frequency: 0.8 },
    { name: 'Laws of Motion', code: 'laws-of-motion', importance: 0.9, frequency: 0.85 },
    { name: 'Work, Energy, Power', code: 'work-energy', importance: 0.8, frequency: 0.75 },
    { name: 'Thermodynamics', code: 'thermodynamics', importance: 0.85, frequency: 0.8 },
    { name: 'Waves', code: 'waves', importance: 0.7, frequency: 0.65 },
    { name: 'Optics', code: 'optics', importance: 0.75, frequency: 0.7 },
    { name: 'Electromagnetism', code: 'em', importance: 0.8, frequency: 0.75 }
  ];

  const physics = subjects.find(s => s.code === 'physics')!;
  
  for (const topic of physicsTopics) {
    await prisma.topic.upsert({
      where: { 
        subjectId_code: { subjectId: physics.id, code: topic.code }
      },
      update: {},
      create: {
        name: topic.name,
        code: topic.code,
        subjectId: physics.id,
        importance: topic.importance,
        frequency: topic.frequency
      }
    });
  }

  // Create Topics for Chemistry
  const chemistryTopics = [
    { name: 'Organic Chemistry', code: 'organic', importance: 0.8, frequency: 0.7 },
    { name: 'Inorganic Chemistry', code: 'inorganic', importance: 0.75, frequency: 0.65 },
    { name: 'Physical Chemistry', code: 'physical', importance: 0.85, frequency: 0.75 },
    { name: 'Chemical Bonding', code: 'bonding', importance: 0.8, frequency: 0.7 },
    { name: 'Electrochemistry', code: 'electro', importance: 0.7, frequency: 0.6 }
  ];

  const chemistry = subjects.find(s => s.code === 'chemistry')!;
  
  for (const topic of chemistryTopics) {
    await prisma.topic.upsert({
      where: { 
        subjectId_code: { subjectId: chemistry.id, code: topic.code }
      },
      update: {},
      create: {
        name: topic.name,
        code: topic.code,
        subjectId: chemistry.id,
        importance: topic.importance,
        frequency: topic.frequency
      }
    });
  }

  // Create Topics for English
  const englishTopics = [
    { name: 'Grammar', code: 'grammar', importance: 0.85, frequency: 0.8 },
    { name: 'Vocabulary', code: 'vocabulary', importance: 0.8, frequency: 0.75 },
    { name: 'Reading Comprehension', code: 'comprehension', importance: 0.9, frequency: 0.85 },
    { name: 'Sentence Correction', code: 'sentence', importance: 0.75, frequency: 0.7 }
  ];

  const english = subjects.find(s => s.code === 'english')!;
  
  for (const topic of englishTopics) {
    await prisma.topic.upsert({
      where: { 
        subjectId_code: { subjectId: english.id, code: topic.code }
      },
      update: {},
      create: {
        name: topic.name,
        code: topic.code,
        subjectId: english.id,
        importance: topic.importance,
        frequency: topic.frequency
      }
    });
  }

  console.log(`✅ Created topics for all subjects`);

  // Create sample questions
  const sampleQuestions = [
    // Mathematics
    {
      questionText: 'If A is a 3×3 matrix with determinant 5, what is the determinant of 2A?',
      optionA: '10',
      optionB: '30',
      optionC: '40',
      optionD: '15',
      correctAnswer: 'C',
      explanation: 'For a 3×3 matrix, det(kA) = k³ det(A). So det(2A) = 8 × 5 = 40.',
      difficulty: 0.5,
      subjectCode: 'mathematics',
      topicCode: 'matrices'
    },
    {
      questionText: 'What is the derivative of sin(x²) with respect to x?',
      optionA: 'cos(x²)',
      optionB: '2x cos(x²)',
      optionC: '2 sin(x) cos(x)',
      optionD: 'x cos(x²)',
      correctAnswer: 'B',
      explanation: 'Using chain rule: d/dx[sin(x²)] = cos(x²) × d/dx[x²] = cos(x²) × 2x = 2x cos(x²)',
      difficulty: 0.3,
      subjectCode: 'mathematics',
      topicCode: 'differentiation'
    },
    {
      questionText: 'What is the value of ∫x e^x dx?',
      optionA: 'x e^x + C',
      optionB: 'e^x + C',
      optionC: '(x-1) e^x + C',
      optionD: '(x+1) e^x + C',
      correctAnswer: 'C',
      explanation: 'Using integration by parts: ∫x e^x dx = x e^x - ∫e^x dx = x e^x - e^x + C = (x-1) e^x + C',
      difficulty: 0.4,
      subjectCode: 'mathematics',
      topicCode: 'integration'
    },
    // Physics
    {
      questionText: 'A body is projected at an angle of 45° with horizontal. The ratio of its kinetic energy at the highest point to that at the point of projection is:',
      optionA: '1:2',
      optionB: '2:1',
      optionC: '1:√2',
      optionD: '1:1',
      correctAnswer: 'A',
      explanation: 'At highest point, only horizontal component remains. KE_top/KE_initial = (v cos θ)²/v² = cos²45° = 1/2',
      difficulty: 0.2,
      subjectCode: 'physics',
      topicCode: 'kinematics'
    },
    {
      questionText: 'The first law of thermodynamics is based on:',
      optionA: 'Conservation of momentum',
      optionB: 'Conservation of energy',
      optionC: 'Conservation of mass',
      optionD: 'Conservation of entropy',
      correctAnswer: 'B',
      explanation: 'The first law of thermodynamics is a statement of conservation of energy for thermodynamic systems.',
      difficulty: -0.2,
      subjectCode: 'physics',
      topicCode: 'thermodynamics'
    },
    // Chemistry
    {
      questionText: 'Which of the following is the correct IUPAC name of CH₃-CH(OH)-CH₃?',
      optionA: '1-propanol',
      optionB: '2-propanol',
      optionC: 'propan-1-ol',
      optionD: 'propan-3-ol',
      correctAnswer: 'B',
      explanation: 'The OH group is attached to the second carbon of propane, so it is 2-propanol (or propan-2-ol).',
      difficulty: -0.3,
      subjectCode: 'chemistry',
      topicCode: 'organic'
    },
    // English
    {
      questionText: 'Choose the correct sentence:',
      optionA: 'Neither the students nor the teacher were present.',
      optionB: 'Neither the students nor the teacher was present.',
      optionC: 'Neither the students or the teacher was present.',
      optionD: 'Neither the students nor teacher were present.',
      correctAnswer: 'B',
      explanation: 'With "neither...nor", the verb agrees with the nearest subject. "Teacher" is singular, so "was" is correct.',
      difficulty: 0.1,
      subjectCode: 'english',
      topicCode: 'grammar'
    }
  ];

  for (const q of sampleQuestions) {
    const subject = subjects.find(s => s.code === q.subjectCode)!;
    const topic = await prisma.topic.findFirst({
      where: { code: q.topicCode, subjectId: subject.id }
    });

    if (topic) {
      await prisma.question.create({
        data: {
          questionText: q.questionText,
          optionA: q.optionA,
          optionB: q.optionB,
          optionC: q.optionC,
          optionD: q.optionD,
          correctAnswer: q.correctAnswer,
          explanation: q.explanation,
          difficulty: q.difficulty,
          subjectId: subject.id,
          topicId: topic.id,
          source: 'verified',
          verified: true
        }
      });
    }
  }

  console.log(`✅ Created ${sampleQuestions.length} sample questions`);

  // Create achievements
  const achievements = [
    { code: 'first_session', name: 'First Steps', description: 'Complete your first study session', icon: '🎯', xpReward: 50, coinReward: 20, conditionType: 'sessions', conditionValue: 1 },
    { code: 'streak_3', name: 'Triple Threat', description: 'Maintain a 3-day streak', icon: '🔥', xpReward: 100, coinReward: 30, conditionType: 'streak', conditionValue: 3 },
    { code: 'streak_7', name: 'Week Warrior', description: 'Maintain a 7-day streak', icon: '💪', xpReward: 200, coinReward: 50, conditionType: 'streak', conditionValue: 7 },
    { code: 'streak_14', name: 'Fortnight Fighter', description: 'Maintain a 14-day streak', icon: '⚔️', xpReward: 400, coinReward: 100, conditionType: 'streak', conditionValue: 14 },
    { code: 'streak_30', name: 'Monthly Master', description: 'Maintain a 30-day streak', icon: '👑', xpReward: 1000, coinReward: 200, conditionType: 'streak', conditionValue: 30 },
    { code: 'questions_50', name: 'Half Century', description: 'Answer 50 questions', icon: '📊', xpReward: 50, coinReward: 20, conditionType: 'questions', conditionValue: 50 },
    { code: 'questions_100', name: 'Century', description: 'Answer 100 questions', icon: '💯', xpReward: 100, coinReward: 30, conditionType: 'questions', conditionValue: 100 },
    { code: 'questions_500', name: 'Knowledge Seeker', description: 'Answer 500 questions', icon: '📚', xpReward: 300, coinReward: 100, conditionType: 'questions', conditionValue: 500 },
    { code: 'accuracy_80', name: 'Sharp Mind', description: 'Achieve 80%+ accuracy', icon: '🎯', xpReward: 100, coinReward: 40, conditionType: 'accuracy', conditionValue: 80 },
    { code: 'accuracy_90', name: 'Sharp Shooter', description: 'Achieve 90%+ accuracy', icon: '🎖️', xpReward: 150, coinReward: 50, conditionType: 'accuracy', conditionValue: 90 },
    { code: 'level_5', name: 'Rising Star', description: 'Reach Level 5', icon: '⭐', xpReward: 200, coinReward: 75, conditionType: 'level', conditionValue: 5 },
    { code: 'level_10', name: 'Elite Scholar', description: 'Reach Level 10', icon: '🌟', xpReward: 500, coinReward: 150, conditionType: 'level', conditionValue: 10 },
    { code: 'level_15', name: 'Master Mind', description: 'Reach Level 15', icon: '🏆', xpReward: 800, coinReward: 250, conditionType: 'level', conditionValue: 15 },
    { code: 'level_20', name: 'Legendary', description: 'Reach Level 20', icon: '💎', xpReward: 1500, coinReward: 500, conditionType: 'level', conditionValue: 20 }
  ];

  for (const achievement of achievements) {
    await prisma.achievement.upsert({
      where: { code: achievement.code },
      update: achievement,
      create: achievement
    });
  }

  console.log(`✅ Created ${achievements.length} achievements`);

  // Create interview questions
  const interviewQuestions = [
    { category: 'personal', question: 'Tell me about yourself and your background.', modelAnswer: 'Give a brief introduction covering your education, interests, and career goals.', difficulty: 1 },
    { category: 'personal', question: 'Why do you want to study Computer Science?', modelAnswer: 'Explain your interest in technology, problem-solving abilities, and career aspirations.', difficulty: 2 },
    { category: 'personal', question: 'Why have you chosen Loyola Academy specifically?', modelAnswer: 'Mention the reputation, faculty, facilities, and values of the institution.', difficulty: 2 },
    { category: 'academic', question: 'What was your favorite subject in 10+2 and why?', modelAnswer: 'Explain your interest and achievements in that subject.', difficulty: 1 },
    { category: 'cs_basics', question: 'What is an algorithm? Give an example.', modelAnswer: 'An algorithm is a step-by-step procedure for solving a problem. Example: Recipe for cooking.', difficulty: 2 },
    { category: 'cs_basics', question: 'What is the difference between software and hardware?', modelAnswer: 'Hardware is physical components; software is programs that run on hardware.', difficulty: 1 },
    { category: 'current_affairs', question: 'What are your thoughts on Digital India initiative?', modelAnswer: 'Discuss the impact of digitalization on governance, economy, and society.', difficulty: 3 },
    { category: 'situational', question: 'If you face a difficult problem in your project, how would you approach it?', modelAnswer: 'Break it down, research, seek help, and persist until solved.', difficulty: 2 }
  ];

  for (const iq of interviewQuestions) {
    await prisma.interviewQuestion.create({
      data: {
        category: iq.category,
        question: iq.question,
        modelAnswer: iq.modelAnswer,
        difficulty: iq.difficulty
      }
    });
  }

  console.log(`✅ Created ${interviewQuestions.length} interview questions`);

  console.log('\n✅ Database seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
