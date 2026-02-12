/**
 * JARVIS API - Interview Preparation Endpoint
 * Handles mock interviews, feedback, and interview question management
 */

import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import ZAI from 'z-ai-web-dev-sdk';

const INTERVIEW_SYSTEM_PROMPT = `You are an experienced interview coach for college admissions in India, specializing in Loyola Academy Hyderabad.

Conduct mock interviews for B.Sc Computer Science admission with focus on:

1. Personal Introduction (2-3 minutes)
   - Background, hobbies, career goals
   - Why Computer Science?
   - Why Loyola Academy?

2. Academic Questions
   - 10+2 subjects (Maths, Physics, Chemistry)
   - Basic computer awareness
   - Current affairs (general)

3. Situational Questions
   - Problem-solving scenarios
   - Teamwork examples
   - Future plans

CRITICAL INTERVIEW INFO:
- Parents MUST accompany candidates for the actual interview (mandatory requirement)
- Interview is conducted offline at Loyola Academy campus
- Dress code: Formal attire expected
- Documents: Originals required for verification

Provide feedback in this format:
STRENGTHS: [list strengths]
WEAKNESSES: [list weaknesses]
RECOMMENDATIONS: [specific improvements]
SCORE: [0-100]
TIPS: [communication tips]`;

const QUESTION_CATEGORIES = {
  personal: [
    'Tell me about yourself and your background.',
    'What are your hobbies and interests?',
    'Why do you want to study Computer Science?',
    'Why have you chosen Loyola Academy specifically?',
    'Where do you see yourself in 5 years?',
    'What are your strengths and weaknesses?',
    'Tell me about a challenge you overcame.',
    'Who is your role model and why?'
  ],
  academic: [
    'What was your favorite subject in 10+2 and why?',
    'Explain the difference between C and Python.',
    'What is the difference between RAM and ROM?',
    'What is an algorithm? Give an example.',
    'Explain the concept of object-oriented programming.',
    'What is the Internet? How does it work?',
    'What is a database? Name some examples.',
    'What are logic gates? Name any three.'
  ],
  cs_basics: [
    'What is programming? Why is it important?',
    'What is an operating system? Name some examples.',
    'What is the difference between software and hardware?',
    'What is cloud computing?',
    'What is artificial intelligence?',
    'What is cybersecurity and why is it important?',
    'What is a programming language? Name some.',
    'What is the role of a computer scientist?'
  ],
  current_affairs: [
    'What are your thoughts on Digital India initiative?',
    'How has technology changed education in recent years?',
    'What do you know about recent developments in AI?',
    'Name some famous Indian tech entrepreneurs.',
    'What is the impact of social media on society?',
    'What do you know about 5G technology?',
    'How has COVID-19 affected the education sector?'
  ],
  situational: [
    'If you face a difficult problem in your project, how would you approach it?',
    'How would you handle a disagreement with a team member?',
    'If you had to choose between two good colleges, how would you decide?',
    'What would you do if you failed an important exam?',
    'How would you manage time between studies and other activities?'
  ]
};

// Get interview questions
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category');
    const userId = searchParams.get('userId');
    const sessionId = searchParams.get('sessionId');

    // Get specific session
    if (sessionId) {
      const session = await db.interviewSession.findUnique({
        where: { id: sessionId }
      });
      return NextResponse.json({
        success: true,
        session
      });
    }

    // Get user's interview history
    if (userId) {
      const sessions = await db.interviewSession.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        take: 10
      });

      // Get existing questions from database
      const questions = await db.interviewQuestion.findMany({
        where: { isActive: true },
        take: 50
      });

      return NextResponse.json({
        success: true,
        sessions,
        questions,
        categories: Object.keys(QUESTION_CATEGORIES)
      });
    }

    // Return available questions by category
    if (category && QUESTION_CATEGORIES[category as keyof typeof QUESTION_CATEGORIES]) {
      return NextResponse.json({
        success: true,
        category,
        questions: QUESTION_CATEGORIES[category as keyof typeof QUESTION_CATEGORIES]
      });
    }

    // Return all categories
    return NextResponse.json({
      success: true,
      categories: Object.keys(QUESTION_CATEGORIES),
      totalQuestions: Object.values(QUESTION_CATEGORIES).flat().length
    });

  } catch (error) {
    console.error('Get interview data error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch interview data' },
      { status: 500 }
    );
  }
}

// Start mock interview or submit response
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, userId, category, question, answer, sessionId } = body;

    // Start new interview session
    if (action === 'start') {
      if (!userId) {
        return NextResponse.json(
          { error: 'User ID is required' },
          { status: 400 }
        );
      }

      const session = await db.interviewSession.create({
        data: {
          userId,
          sessionType: 'mock_interview',
          startTime: new Date()
        }
      });

      // Generate first question
      const firstQuestion = await generateInterviewQuestion('personal');

      return NextResponse.json({
        success: true,
        session,
        firstQuestion,
        message: 'Interview session started. Answer the question to continue.'
      });
    }

    // Submit answer and get feedback
    if (action === 'answer') {
      if (!sessionId || !question || !answer) {
        return NextResponse.json(
          { error: 'Session ID, question, and answer are required' },
          { status: 400 }
        );
      }

      const zai = await ZAI.create();

      // Get AI feedback
      const completion = await zai.chat.completions.create({
        messages: [
          { role: 'system', content: INTERVIEW_SYSTEM_PROMPT },
          { role: 'user', content: `Question: ${question}\nStudent's Answer: ${answer}\n\nProvide detailed feedback.` }
        ],
        temperature: 0.7,
        max_tokens: 500
      });

      const feedbackText = completion.choices[0]?.message?.content || '';

      // Parse feedback
      const feedback = parseInterviewFeedback(feedbackText);

      // Update session
      const session = await db.interviewSession.update({
        where: { id: sessionId },
        data: {
          questionsAsked: { increment: 1 },
          confidenceScore: feedback.confidenceScore,
          clarityScore: feedback.clarityScore,
          technicalScore: feedback.technicalScore,
          strengths: JSON.stringify(feedback.strengths),
          weaknesses: JSON.stringify(feedback.weaknesses),
          recommendations: JSON.stringify(feedback.recommendations)
        }
      });

      // Generate next question
      const nextCategory = getNextCategory(session.questionsAsked);
      const nextQuestion = await generateInterviewQuestion(nextCategory);

      return NextResponse.json({
        success: true,
        feedback,
        rawFeedback: feedbackText,
        nextQuestion,
        questionsRemaining: 10 - session.questionsAsked
      });
    }

    // Generate question for specific category
    if (action === 'generate_question') {
      const question = await generateInterviewQuestion(category || 'personal');
      return NextResponse.json({
        success: true,
        question,
        category: category || 'personal'
      });
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    );

  } catch (error) {
    console.error('Interview POST error:', error);
    return NextResponse.json(
      { error: 'Failed to process interview request' },
      { status: 500 }
    );
  }
}

// End interview session
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { sessionId, notes } = body;

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    const session = await db.interviewSession.findUnique({
      where: { id: sessionId }
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    const endTime = new Date();
    const durationMinutes = Math.round(
      (endTime.getTime() - new Date(session.startTime).getTime()) / (1000 * 60)
    );

    // Calculate overall score
    const overallScore = Math.round(
      ((session.confidenceScore || 0) + 
       (session.clarityScore || 0) + 
       (session.technicalScore || 0)) / 3
    );

    const updatedSession = await db.interviewSession.update({
      where: { id: sessionId },
      data: {
        endTime,
        durationMinutes,
        notes,
        technicalScore: overallScore // Store overall score
      }
    });

    // Award XP for interview practice
    const xpEarned = 50 + Math.round(overallScore / 2);
    await db.user.update({
      where: { id: session.userId },
      data: {
        totalXP: { increment: xpEarned }
      }
    });

    // Generate final recommendations
    const strengths = session.strengths ? JSON.parse(session.strengths) : [];
    const weaknesses = session.weaknesses ? JSON.parse(session.weaknesses) : [];
    const recommendations = session.recommendations ? JSON.parse(session.recommendations) : [];

    return NextResponse.json({
      success: true,
      session: updatedSession,
      xpEarned,
      summary: {
        questionsAnswered: session.questionsAsked,
        duration: durationMinutes,
        overallScore,
        strengths,
        weaknesses,
        recommendations
      },
      message: 'Interview session completed!'
    });

  } catch (error) {
    console.error('End interview error:', error);
    return NextResponse.json(
      { error: 'Failed to end interview session' },
      { status: 500 }
    );
  }
}

// Helper: Generate interview question
async function generateInterviewQuestion(category: string): Promise<string> {
  try {
    const zai = await ZAI.create();

    const completion = await zai.chat.completions.create({
      messages: [
        { role: 'system', content: INTERVIEW_SYSTEM_PROMPT },
        { 
          role: 'user', 
          content: `Generate ONE interview question in the "${category}" category for B.Sc Computer Science admission at Loyola Academy. Just the question, nothing else.` 
        }
      ],
      temperature: 0.9,
      max_tokens: 100
    });

    return completion.choices[0]?.message?.content || 
           QUESTION_CATEGORIES[category as keyof typeof QUESTION_CATEGORIES]?.[0] ||
           'Tell me about yourself.';
  } catch (error) {
    // Fallback to predefined questions
    const questions = QUESTION_CATEGORIES[category as keyof typeof QUESTION_CATEGORIES];
    return questions?.[Math.floor(Math.random() * questions.length)] || 
           'Tell me about yourself.';
  }
}

// Helper: Parse interview feedback
function parseInterviewFeedback(feedback: string) {
  const getLines = (prefix: string): string[] => {
    const regex = new RegExp(`${prefix}:?\\s*(.+?)(?=\\n[A-Z]+:|$)`, 'i');
    const match = feedback.match(regex);
    if (!match) return [];
    return match[1].split(',').map(s => s.trim()).filter(s => s);
  };

  const scoreMatch = feedback.match(/SCORE:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : 70;

  return {
    strengths: getLines('STRENGTHS'),
    weaknesses: getLines('WEAKNESSES'),
    recommendations: getLines('RECOMMENDATIONS'),
    confidenceScore: Math.min(100, score + 5),
    clarityScore: Math.min(100, score),
    technicalScore: Math.min(100, score - 5),
    communicationTips: getLines('TIPS')
  };
}

// Helper: Get next category based on progress
function getNextCategory(questionsAsked: number): string {
  const sequence = ['personal', 'academic', 'academic', 'cs_basics', 'cs_basics', 'current_affairs', 'situational', 'situational', 'personal', 'academic'];
  return sequence[questionsAsked % sequence.length];
}
