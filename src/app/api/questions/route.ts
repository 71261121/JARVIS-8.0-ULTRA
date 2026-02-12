/**
 * JARVIS API - Question Generation & Management Endpoint
 * Generates MCQs using AI and manages question bank
 */

import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import ZAI from 'z-ai-web-dev-sdk';

const QUESTION_GEN_PROMPT = `You are an expert question setter for Telangana State Intermediate level exams, specifically for Loyola Academy B.Sc CS entrance.

Generate multiple choice questions following these rules:
1. Exactly 4 options (A, B, C, D)
2. Only ONE correct answer
3. Difficulty level appropriate for 10+2 students
4. Questions should match the actual exam style - practical and conceptual
5. Include a clear explanation for the correct answer
6. Difficulty rating: -3 (very easy) to +3 (very hard)

Format your response EXACTLY as:
QUESTION: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
ANSWER: [A/B/C/D]
EXPLANATION: [why this answer is correct]
DIFFICULTY: [number between -3 and +3]
TOPIC: [specific topic name]`;

// Get questions from database
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const subject = searchParams.get('subject');
    const topic = searchParams.get('topic');
    const difficulty = searchParams.get('difficulty');
    const limit = parseInt(searchParams.get('limit') || '10');
    const random = searchParams.get('random') === 'true';

    // Build query
    const where: any = { isActive: true };
    
    if (subject) {
      const subjectRecord = await db.subject.findFirst({
        where: { code: subject.toLowerCase() }
      });
      if (subjectRecord) {
        where.subjectId = subjectRecord.id;
      }
    }

    if (topic) {
      const topicRecord = await db.topic.findFirst({
        where: { code: topic.toLowerCase() }
      });
      if (topicRecord) {
        where.topicId = topicRecord.id;
      }
    }

    if (difficulty) {
      const diff = parseFloat(difficulty);
      where.difficulty = {
        gte: diff - 0.5,
        lte: diff + 0.5
      };
    }

    let questions;
    if (random) {
      // Get random questions (SQLite specific)
      questions = await db.$queryRaw`
        SELECT * FROM Question 
        WHERE isActive = 1
        ${subject ? db.$queryRaw`AND subjectId = ${subject}` : db.$queryRaw``}
        ORDER BY RANDOM() 
        LIMIT ${limit}
      `;
    } else {
      questions = await db.question.findMany({
        where,
        take: limit,
        include: {
          topic: true,
          subject: true
        }
      });
    }

    return NextResponse.json({
      success: true,
      count: Array.isArray(questions) ? questions.length : 0,
      questions
    });

  } catch (error) {
    console.error('Get questions error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch questions' },
      { status: 500 }
    );
  }
}

// Generate new question using AI
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic, subject, difficulty = 0, count = 1, save = false } = body;

    if (!topic || !subject) {
      return NextResponse.json(
        { error: 'Topic and subject are required' },
        { status: 400 }
      );
    }

    const zai = await ZAI.create();
    const generatedQuestions: any[] = [];

    for (let i = 0; i < count; i++) {
      const userPrompt = `Generate a ${subject} question on topic "${topic}" with difficulty around ${difficulty}.`;

      const completion = await zai.chat.completions.create({
        messages: [
          { role: 'system', content: QUESTION_GEN_PROMPT },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.8,
        max_tokens: 600
      });

      const response = completion.choices[0]?.message?.content;
      if (response) {
        const parsed = parseQuestionResponse(response, topic, subject);
        if (parsed) {
          generatedQuestions.push(parsed);
        }
      }

      // Small delay between generations
      if (i < count - 1) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
    }

    // Save to database if requested
    if (save && generatedQuestions.length > 0) {
      for (const q of generatedQuestions) {
        // Find or create subject
        let subjectRecord = await db.subject.findFirst({
          where: { code: subject.toLowerCase() }
        });

        if (!subjectRecord) {
          subjectRecord = await db.subject.create({
            data: {
              name: subject.charAt(0).toUpperCase() + subject.slice(1),
              code: subject.toLowerCase()
            }
          });
        }

        // Find or create topic
        let topicRecord = await db.topic.findFirst({
          where: { 
            code: topic.toLowerCase(),
            subjectId: subjectRecord.id
          }
        });

        if (!topicRecord) {
          topicRecord = await db.topic.create({
            data: {
              name: topic,
              code: topic.toLowerCase(),
              subjectId: subjectRecord.id
            }
          });
        }

        // Save question
        await db.question.create({
          data: {
            questionText: q.questionText,
            optionA: q.optionA,
            optionB: q.optionB,
            optionC: q.optionC,
            optionD: q.optionD,
            correctAnswer: q.correctAnswer,
            explanation: q.explanation,
            difficulty: q.difficulty,
            topicId: topicRecord.id,
            subjectId: subjectRecord.id,
            source: 'generated',
            verified: false
          }
        });
      }
    }

    return NextResponse.json({
      success: true,
      count: generatedQuestions.length,
      questions: generatedQuestions,
      saved: save
    });

  } catch (error) {
    console.error('Question generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate questions' },
      { status: 500 }
    );
  }
}

function parseQuestionResponse(response: string, topic: string, subject: string) {
  try {
    const lines = response.split('\n').filter(l => l.trim());
    
    const getLine = (prefix: string): string => {
      const line = lines.find(l => l.startsWith(prefix) || l.toUpperCase().startsWith(prefix.toUpperCase()));
      if (!line) return '';
      // Handle both "PREFIX: value" and "PREFIX value" formats
      return line.replace(new RegExp(`^${prefix}:?\\s*`, 'i'), '').trim();
    };

    const questionText = getLine('QUESTION:');
    const optionA = getLine('A)').replace(/^A\)\s*/i, '').trim();
    const optionB = getLine('B)').replace(/^B\)\s*/i, '').trim();
    const optionC = getLine('C)').replace(/^C\)\s*/i, '').trim();
    const optionD = getLine('D)').replace(/^D\)\s*/i, '').trim();
    const correctAnswer = getLine('ANSWER:').toUpperCase() as 'A' | 'B' | 'C' | 'D';
    const explanation = getLine('EXPLANATION:');
    const difficulty = parseFloat(getLine('DIFFICULTY:')) || 0;

    if (!questionText || !optionA || !optionB || !correctAnswer) {
      return null;
    }

    return {
      questionText,
      optionA,
      optionB,
      optionC: optionC || 'None of the above',
      optionD: optionD || 'All of the above',
      correctAnswer,
      explanation,
      difficulty: Math.max(-3, Math.min(3, difficulty)),
      topic,
      subject
    };
  } catch (error) {
    return null;
  }
}
