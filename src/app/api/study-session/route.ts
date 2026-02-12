/**
 * JARVIS API - Study Session Management Endpoint
 * Handles session creation, question answering with IRT, and session analytics
 */

import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import IRTEngine from '@/lib/irt';
import SM2Engine from '@/lib/sm2';
import PsychologicalEngine from '@/lib/psychological';

// Get active session or create new one
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const sessionId = searchParams.get('sessionId');

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    if (sessionId) {
      // Get specific session
      const session = await db.session.findUnique({
        where: { id: sessionId },
        include: {
          responses: {
            include: {
              question: {
                include: { topic: true, subject: true }
              }
            }
          }
        }
      });

      if (!session) {
        return NextResponse.json(
          { error: 'Session not found' },
          { status: 404 }
        );
      }

      return NextResponse.json({
        success: true,
        session
      });
    }

    // Get user's recent sessions
    const sessions = await db.session.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
      take: 10,
      include: {
        _count: {
          select: { responses: true }
        }
      }
    });

    // Get today's stats
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const todaySessions = await db.session.findMany({
      where: {
        userId,
        startTime: { gte: today }
      }
    });

    const todayStats = {
      totalMinutes: todaySessions.reduce((sum, s) => sum + s.durationMinutes, 0),
      totalQuestions: todaySessions.reduce((sum, s) => sum + s.questionsAttempted, 0),
      correctAnswers: todaySessions.reduce((sum, s) => sum + s.questionsCorrect, 0),
      sessionsCount: todaySessions.length
    };

    return NextResponse.json({
      success: true,
      sessions,
      todayStats
    });

  } catch (error) {
    console.error('Get session error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch sessions' },
      { status: 500 }
    );
  }
}

// Create new study session
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      userId, 
      sessionType = 'study',
      subjectFocus,
      topicFocus 
    } = body;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Create new session
    const session = await db.session.create({
      data: {
        userId,
        sessionType,
        subjectFocus,
        topicFocus,
        startTime: new Date()
      }
    });

    // Get user for IRT theta values
    const user = await db.user.findUnique({
      where: { id: userId }
    });

    // Get optimal questions based on IRT
    let theta = 0;
    if (subjectFocus === 'maths') theta = user?.mathsTheta || 0;
    else if (subjectFocus === 'physics') theta = user?.physicsTheta || 0;
    else if (subjectFocus === 'chemistry') theta = user?.chemistryTheta || 0;
    else if (subjectFocus === 'english') theta = user?.englishTheta || 0;

    // Get questions near user's ability for optimal learning
    const questions = await getAdaptiveQuestions(userId, subjectFocus, theta, 10);

    return NextResponse.json({
      success: true,
      session,
      theta,
      recommendedQuestions: questions,
      message: 'Session started successfully'
    });

  } catch (error) {
    console.error('Create session error:', error);
    return NextResponse.json(
      { error: 'Failed to create session' },
      { status: 500 }
    );
  }
}

// Submit answer with IRT update
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      sessionId,
      userId,
      questionId,
      selectedAnswer,
      timeTakenMs 
    } = body;

    if (!sessionId || !userId || !questionId || !selectedAnswer) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Get question
    const question = await db.question.findUnique({
      where: { id: questionId },
      include: { subject: true }
    });

    if (!question) {
      return NextResponse.json(
        { error: 'Question not found' },
        { status: 404 }
      );
    }

    // Check correctness
    const isCorrect = selectedAnswer.toUpperCase() === question.correctAnswer.toUpperCase();

    // Get user's current theta
    const user = await db.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Determine which theta to update
    let thetaField: string;
    const subjectCode = question.subject.code.toLowerCase();
    if (subjectCode === 'mathematics' || subjectCode === 'maths') thetaField = 'mathsTheta';
    else if (subjectCode === 'physics') thetaField = 'physicsTheta';
    else if (subjectCode === 'chemistry') thetaField = 'chemistryTheta';
    else thetaField = 'englishTheta';

    const currentTheta = (user as any)[thetaField] || 0;

    // IRT Update
    const irtParams = {
      difficulty: question.difficulty,
      discrimination: question.discrimination,
      guessing: 0.25
    };

    const irtResult = IRTEngine.updateTheta(currentTheta, irtParams, isCorrect);

    // Update user's theta
    await db.user.update({
      where: { id: userId },
      data: {
        [thetaField]: irtResult.thetaAfter,
        totalQuestions: { increment: 1 },
        correctAnswers: isCorrect ? { increment: 1 } : undefined
      }
    });

    // Update question stats
    await db.question.update({
      where: { id: questionId },
      data: {
        timesAsked: { increment: 1 },
        timesCorrect: isCorrect ? { increment: 1 } : undefined
      }
    });

    // Update session stats
    await db.session.update({
      where: { id: sessionId },
      data: {
        questionsAttempted: { increment: 1 },
        questionsCorrect: isCorrect ? { increment: 1 } : undefined
      }
    });

    // Save response
    const response = await db.questionResponse.create({
      data: {
        userId,
        questionId,
        sessionId,
        selectedAnswer,
        isCorrect,
        timeTakenMs: timeTakenMs || 0,
        thetaBefore: irtResult.thetaBefore,
        thetaAfter: irtResult.thetaAfter,
        thetaChange: irtResult.thetaChange
      }
    });

    // Calculate XP using psychological engine
    const xpResult = PsychologicalEngine.calculateVariableReward(
      isCorrect ? 15 : 5, // base XP
      isCorrect ? 5 : 2   // base coins
    );

    // Update user XP
    await db.user.update({
      where: { id: userId },
      data: {
        totalXP: { increment: xpResult.xp },
        focusCoins: { increment: xpResult.coins }
      }
    });

    // Get next optimal question
    const nextQuestions = await getAdaptiveQuestions(
      userId, 
      question.subject.code, 
      irtResult.thetaAfter, 
      1
    );

    return NextResponse.json({
      success: true,
      isCorrect,
      correctAnswer: question.correctAnswer,
      explanation: question.explanation,
      irtUpdate: {
        thetaBefore: irtResult.thetaBefore,
        thetaAfter: irtResult.thetaAfter,
        thetaChange: irtResult.thetaChange,
        probabilityCorrect: irtResult.probabilityCorrect
      },
      reward: xpResult,
      nextQuestion: nextQuestions[0] || null,
      abilityLevel: IRTEngine.getAbilityLevel(irtResult.thetaAfter)
    });

  } catch (error) {
    console.error('Submit answer error:', error);
    return NextResponse.json(
      { error: 'Failed to submit answer' },
      { status: 500 }
    );
  }
}

// End session
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

    // Get session
    const session = await db.session.findUnique({
      where: { id: sessionId },
      include: {
        responses: true
      }
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      );
    }

    // Calculate session duration
    const endTime = new Date();
    const durationMinutes = Math.round(
      (endTime.getTime() - new Date(session.startTime).getTime()) / (1000 * 60)
    );

    // Calculate average time per question
    const avgTimePerQ = session.responses.length > 0
      ? session.responses.reduce((sum, r) => sum + (r.timeTakenMs || 0), 0) / session.responses.length / 1000
      : 0;

    // Calculate XP for session completion
    const xpResult = PsychologicalEngine.calculateSessionXP(
      session.questionsAttempted,
      session.questionsCorrect,
      durationMinutes,
      120, // target 2 hours
      session.distractions === 0
    );

    // Update session
    const updatedSession = await db.session.update({
      where: { id: sessionId },
      data: {
        endTime,
        durationMinutes,
        averageTimePerQ: avgTimePerQ,
        notes,
        xpEarned: xpResult.totalXP,
        focusScore: Math.max(0, 100 - session.distractions * 10)
      }
    });

    // Update user stats
    await db.user.update({
      where: { id: session.userId },
      data: {
        totalStudyMinutes: { increment: durationMinutes },
        totalSessions: { increment: 1 },
        totalXP: { increment: xpResult.totalXP }
      }
    });

    // Check for streak update
    const user = await db.user.findUnique({
      where: { id: session.userId }
    });

    if (user) {
      const streakResult = PsychologicalEngine.updateStreak(
        user.currentStreak,
        user.longestStreak,
        true // studied today
      );

      await db.user.update({
        where: { id: session.userId },
        data: {
          currentStreak: streakResult.currentStreak,
          longestStreak: streakResult.longestStreak
        }
      });
    }

    return NextResponse.json({
      success: true,
      session: updatedSession,
      xpEarned: xpResult.totalXP,
      xpBreakdown: xpResult.reason,
      message: 'Session completed successfully'
    });

  } catch (error) {
    console.error('End session error:', error);
    return NextResponse.json(
      { error: 'Failed to end session' },
      { status: 500 }
    );
  }
}

// Helper: Get adaptive questions based on IRT
async function getAdaptiveQuestions(
  userId: string, 
  subject: string | null, 
  theta: number, 
  limit: number
) {
  try {
    // Build filter
    const where: any = { isActive: true };
    
    if (subject) {
      const subjectRecord = await db.subject.findFirst({
        where: { 
          OR: [
            { code: subject.toLowerCase() },
            { name: { equals: subject, mode: 'insensitive' } }
          ]
        }
      });
      if (subjectRecord) {
        where.subjectId = subjectRecord.id;
      }
    }

    // Get questions
    const allQuestions = await db.question.findMany({
      where,
      include: {
        topic: true,
        subject: true
      }
    });

    if (allQuestions.length === 0) return [];

    // Get already answered questions
    const answered = await db.questionResponse.findMany({
      where: { userId },
      select: { questionId: true }
    });
    const answeredIds = new Set(answered.map(a => a.questionId));

    // Filter out answered and calculate information
    const available = allQuestions.filter(q => !answeredIds.has(q.id));

    // Select questions with maximum information near user's ability
    const scored = available.map(q => {
      const params = {
        difficulty: q.difficulty,
        discrimination: q.discrimination,
        guessing: 0.25
      };
      const info = IRTEngine.fisherInformation(theta, params);
      return { question: q, info };
    });

    // Sort by information (highest first) and take limit
    scored.sort((a, b) => b.info - a.info);

    return scored.slice(0, limit).map(s => s.question);

  } catch (error) {
    console.error('Get adaptive questions error:', error);
    return [];
  }
}
