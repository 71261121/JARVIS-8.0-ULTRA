/**
 * JARVIS API - Analytics Endpoint
 * Provides comprehensive analytics for user performance tracking
 */

import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import IRTEngine from '@/lib/irt';

// Get analytics data
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const period = searchParams.get('period') || 'all'; // daily, weekly, monthly, all
    const detailed = searchParams.get('detailed') === 'true';

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Get user
    const user = await db.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Calculate date range
    const now = new Date();
    let startDate = new Date();
    
    switch (period) {
      case 'daily':
        startDate.setHours(0, 0, 0, 0);
        break;
      case 'weekly':
        startDate.setDate(startDate.getDate() - 7);
        break;
      case 'monthly':
        startDate.setMonth(startDate.getMonth() - 1);
        break;
      default:
        startDate = new Date(0); // All time
    }

    // Get sessions in period
    const sessions = await db.session.findMany({
      where: {
        userId,
        startTime: { gte: startDate }
      },
      include: {
        responses: {
          include: {
            question: {
              include: { subject: true, topic: true }
            }
          }
        }
      }
    });

    // Get all responses for accurate stats
    const allResponses = await db.questionResponse.findMany({
      where: {
        userId,
        createdAt: { gte: startDate }
      },
      include: {
        question: {
          include: { subject: true, topic: true }
        }
      }
    });

    // Calculate basic stats
    const totalStudyMinutes = sessions.reduce((sum, s) => sum + s.durationMinutes, 0);
    const totalQuestions = allResponses.length;
    const correctAnswers = allResponses.filter(r => r.isCorrect).length;
    const accuracy = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;

    // Calculate average time per question
    const avgTimeMs = totalQuestions > 0
      ? allResponses.reduce((sum, r) => sum + (r.timeTakenMs || 0), 0) / totalQuestions
      : 0;
    const avgTimePerQuestion = avgTimeMs / 1000; // Convert to seconds

    // Subject-wise performance
    const subjectStats = await calculateSubjectStats(allResponses);

    // Topic mastery
    const topicMastery = await db.topicMastery.findMany({
      where: { userId },
      include: { topic: { include: { subject: true } } },
      orderBy: { masteryLevel: 'asc' }
    });

    // IRT ability levels
    const thetaScores = {
      maths: user.mathsTheta,
      physics: user.physicsTheta,
      chemistry: user.chemistryTheta,
      english: user.englishTheta
    };

    const abilityLevels = {
      maths: IRTEngine.getAbilityLevel(user.mathsTheta),
      physics: IRTEngine.getAbilityLevel(user.physicsTheta),
      chemistry: IRTEngine.getAbilityLevel(user.chemistryTheta),
      english: IRTEngine.getAbilityLevel(user.englishTheta)
    };

    // Progress over time
    const progressOverTime = await calculateProgressOverTime(userId, period);

    // Weak areas
    const weakAreas = topicMastery
      .filter(t => t.masteryLevel < 50)
      .slice(0, 5)
      .map(t => ({
        topic: t.topic.name,
        subject: t.topic.subject?.name,
        mastery: t.masteryLevel,
        theta: t.topicTheta
      }));

    // Strong areas
    const strongAreas = topicMastery
      .filter(t => t.masteryLevel >= 70)
      .slice(0, 5)
      .map(t => ({
        topic: t.topic.name,
        subject: t.topic.subject?.name,
        mastery: t.masteryLevel,
        theta: t.topicTheta
      }));

    // Predicted score
    const predictedScore = calculatePredictedScore(thetaScores);

    // Build response
    const analytics = {
      period,
      overview: {
        totalStudyMinutes,
        totalSessions: sessions.length,
        totalQuestions,
        correctAnswers,
        accuracy: Math.round(accuracy * 10) / 10,
        avgTimePerQuestion: Math.round(avgTimePerQuestion * 10) / 10,
        currentStreak: user.currentStreak,
        longestStreak: user.longestStreak,
        totalXP: user.totalXP,
        level: IRTEngine.getLevelProgress(user.totalXP).currentLevel
      },
      theta: {
        scores: thetaScores,
        abilityLevels
      },
      subjectStats,
      topicMastery: {
        weakAreas,
        strongAreas,
        totalTopics: topicMastery.length,
        masteredTopics: topicMastery.filter(t => t.masteryLevel >= 70).length
      },
      progressOverTime,
      predictions: {
        estimatedScore: predictedScore,
        readinessLevel: getReadinessLevel(predictedScore, user.currentStreak),
        daysUntilExam: user.examDate 
          ? Math.ceil((new Date(user.examDate).getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
          : null
      }
    };

    // Add detailed info if requested
    if (detailed) {
      const dailyBreakdown = await calculateDailyBreakdown(userId, period);
      const recentSessions = sessions.slice(0, 10);
      const spacedReviews = await db.spacedReview.findMany({
        where: { userId, status: 'pending' },
        include: { topic: true },
        orderBy: { nextReviewDate: 'asc' },
        take: 10
      });

      (analytics as any).detailed = {
        dailyBreakdown,
        recentSessions,
        upcomingReviews: spacedReviews.map(r => ({
          topic: r.topic?.name,
          dueDate: r.nextReviewDate
        }))
      };
    }

    return NextResponse.json({
      success: true,
      analytics
    });

  } catch (error) {
    console.error('Analytics error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics' },
      { status: 500 }
    );
  }
}

// Helper: Calculate subject-wise stats
async function calculateSubjectStats(responses: any[]) {
  const subjectData: Record<string, { total: number; correct: number; time: number }> = {};

  for (const response of responses) {
    const subjectName = response.question?.subject?.name || 'Unknown';
    
    if (!subjectData[subjectName]) {
      subjectData[subjectName] = { total: 0, correct: 0, time: 0 };
    }

    subjectData[subjectName].total++;
    if (response.isCorrect) subjectData[subjectName].correct++;
    subjectData[subjectName].time += response.timeTakenMs || 0;
  }

  return Object.entries(subjectData).map(([name, data]) => ({
    subject: name,
    total: data.total,
    correct: data.correct,
    accuracy: data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0,
    avgTime: data.total > 0 ? Math.round(data.time / data.total / 1000) : 0
  }));
}

// Helper: Calculate progress over time
async function calculateProgressOverTime(userId: string, period: string) {
  const now = new Date();
  const data: Array<{ date: string; questions: number; accuracy: number; minutes: number }> = [];

  let days = 7;
  if (period === 'monthly') days = 30;
  if (period === 'all') days = 90;

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    date.setHours(0, 0, 0, 0);

    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);

    const responses = await db.questionResponse.findMany({
      where: {
        userId,
        createdAt: { gte: date, lt: nextDate }
      }
    });

    const sessions = await db.session.findMany({
      where: {
        userId,
        startTime: { gte: date, lt: nextDate }
      }
    });

    const correct = responses.filter(r => r.isCorrect).length;
    const total = responses.length;

    data.push({
      date: date.toISOString().split('T')[0],
      questions: total,
      accuracy: total > 0 ? Math.round((correct / total) * 100) : 0,
      minutes: sessions.reduce((sum, s) => sum + s.durationMinutes, 0)
    });
  }

  return data;
}

// Helper: Calculate daily breakdown
async function calculateDailyBreakdown(userId: string, period: string) {
  const now = new Date();
  const breakdown: Array<{ 
    date: string; 
    sessions: number; 
    questions: number; 
    accuracy: number;
    xpEarned: number;
    minutes: number;
  }> = [];

  let days = 7;
  if (period === 'monthly') days = 30;
  if (period === 'all') days = 90;

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    date.setHours(0, 0, 0, 0);

    const nextDate = new Date(date);
    nextDate.setDate(nextDate.getDate() + 1);

    const sessions = await db.session.findMany({
      where: {
        userId,
        startTime: { gte: date, lt: nextDate }
      }
    });

    const responses = await db.questionResponse.findMany({
      where: {
        userId,
        createdAt: { gte: date, lt: nextDate }
      }
    });

    const correct = responses.filter(r => r.isCorrect).length;
    const total = responses.length;

    breakdown.push({
      date: date.toISOString().split('T')[0],
      sessions: sessions.length,
      questions: total,
      accuracy: total > 0 ? Math.round((correct / total) * 100) : 0,
      xpEarned: sessions.reduce((sum, s) => sum + s.xpEarned, 0),
      minutes: sessions.reduce((sum, s) => sum + s.durationMinutes, 0)
    });
  }

  return breakdown;
}

// Helper: Calculate predicted exam score
function calculatePredictedScore(theta: { maths: number; physics: number; chemistry: number; english: number }) {
  // Weight by exam marks distribution: Maths 20, Physics 15, Chem+English 15
  const mathsWeight = 20 / 50;
  const physicsWeight = 15 / 50;
  const chemEngWeight = 15 / 50;

  // Convert theta to expected percentage correct
  const mathsPercent = IRTEngine.thetaToPercentage(theta.maths);
  const physicsPercent = IRTEngine.thetaToPercentage(theta.physics);
  const avgChemEng = (theta.chemistry + theta.english) / 2;
  const chemEngPercent = IRTEngine.thetaToPercentage(avgChemEng);

  // Weighted prediction
  const predictedPercent = 
    mathsPercent * mathsWeight +
    physicsPercent * physicsWeight +
    chemEngPercent * chemEngWeight;

  return Math.round(predictedPercent * 50 / 100); // Out of 50 marks
}

// Helper: Get readiness level
function getReadinessLevel(predictedScore: number, streak: number): string {
  if (predictedScore >= 40 && streak >= 7) {
    return 'Excellent - Ready for exam!';
  } else if (predictedScore >= 35) {
    return 'Good - Continue consistent practice';
  } else if (predictedScore >= 25) {
    return 'Moderate - Focus on weak areas';
  } else if (predictedScore >= 15) {
    return 'Needs improvement - Increase study hours';
  } else {
    return 'Early stage - Build foundations first';
  }
}

// Store analytics record
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, period = 'daily' } = body;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Get user
    const user = await db.user.findUnique({
      where: { id: userId }
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Calculate today's stats
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const sessions = await db.session.findMany({
      where: {
        userId,
        startTime: { gte: today }
      }
    });

    const responses = await db.questionResponse.findMany({
      where: {
        userId,
        createdAt: { gte: today }
      }
    });

    const correct = responses.filter(r => r.isCorrect).length;

    // Store analytics record
    const record = await db.analyticsRecord.create({
      data: {
        userId,
        date: today,
        period,
        totalMinutes: sessions.reduce((sum, s) => sum + s.durationMinutes, 0),
        sessionsCount: sessions.length,
        questionsAnswered: responses.length,
        correctAnswers: correct,
        averageAccuracy: responses.length > 0 ? (correct / responses.length) * 100 : 0,
        focusScore: 100 - sessions.reduce((sum, s) => sum + s.distractions, 0) * 5,
        streakDays: user.currentStreak,
        xpEarned: sessions.reduce((sum, s) => sum + s.xpEarned, 0),
        thetaProgress: JSON.stringify({
          maths: user.mathsTheta,
          physics: user.physicsTheta,
          chemistry: user.chemistryTheta,
          english: user.englishTheta
        })
      }
    });

    return NextResponse.json({
      success: true,
      record
    });

  } catch (error) {
    console.error('Store analytics error:', error);
    return NextResponse.json(
      { error: 'Failed to store analytics' },
      { status: 500 }
    );
  }
}
