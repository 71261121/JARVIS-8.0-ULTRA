/**
 * JARVIS API - User Management Endpoint
 * Handles user creation, updates, and profile management
 */

import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import PsychologicalEngine from '@/lib/psychological';

// Get user profile
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const email = searchParams.get('email');

    if (userId) {
      const user = await db.user.findUnique({
        where: { id: userId },
        include: {
          sessions: {
            take: 5,
            orderBy: { createdAt: 'desc' }
          },
          _count: {
            select: {
              sessions: true,
              questionResponses: true,
              topicMastery: true
            }
          }
        }
      });

      if (!user) {
        return NextResponse.json(
          { error: 'User not found' },
          { status: 404 }
        );
      }

      // Calculate level progress
      const levelProgress = PsychologicalEngine.getLevelProgress(user.totalXP);

      return NextResponse.json({
        success: true,
        user: {
          ...user,
          level: levelProgress.currentLevel,
          levelProgress: levelProgress.progress,
          xpForNextLevel: levelProgress.xpNeededForNext
        }
      });
    }

    if (email) {
      const user = await db.user.findUnique({
        where: { email }
      });

      if (!user) {
        return NextResponse.json(
          { error: 'User not found' },
          { status: 404 }
        );
      }

      return NextResponse.json({
        success: true,
        user
      });
    }

    // Get leaderboard (top users)
    const topUsers = await db.user.findMany({
      orderBy: { totalXP: 'desc' },
      take: 20,
      select: {
        id: true,
        name: true,
        totalXP: true,
        currentStreak: true,
        level: true
      }
    });

    return NextResponse.json({
      success: true,
      leaderboard: topUsers.map((u, i) => ({
        ...u,
        rank: i + 1
      }))
    });

  } catch (error) {
    console.error('Get user error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user' },
      { status: 500 }
    );
  }
}

// Create new user
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      email, 
      name, 
      targetExam = 'Loyola Academy B.Sc CS Entrance',
      examDate,
      dailyStudyHours = 8,
      wakeUpTime = '05:00',
      sleepTime = '21:00'
    } = body;

    if (!email || !name) {
      return NextResponse.json(
        { error: 'Email and name are required' },
        { status: 400 }
      );
    }

    // Check if user exists
    const existing = await db.user.findUnique({
      where: { email }
    });

    if (existing) {
      return NextResponse.json(
        { error: 'User with this email already exists' },
        { status: 400 }
      );
    }

    // Create user
    const user = await db.user.create({
      data: {
        email,
        name,
        targetExam,
        examDate: examDate ? new Date(examDate) : null,
        dailyStudyHours,
        wakeUpTime,
        sleepTime,
        // Initialize with default focus coins
        focusCoins: 100
      }
    });

    // Create initial achievements
    await initializeAchievements();

    // Calculate day 1 plan
    const dayPlan = await createDayPlan(user.id, 1);

    return NextResponse.json({
      success: true,
      user,
      dayPlan,
      message: 'User created successfully! Welcome to JARVIS.'
    });

  } catch (error) {
    console.error('Create user error:', error);
    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    );
  }
}

// Update user
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { userId, ...updateData } = body;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Remove sensitive fields
    delete updateData.id;
    delete updateData.createdAt;
    delete updateData.totalXP; // Only increment through sessions

    const user = await db.user.update({
      where: { id: userId },
      data: updateData
    });

    return NextResponse.json({
      success: true,
      user
    });

  } catch (error) {
    console.error('Update user error:', error);
    return NextResponse.json(
      { error: 'Failed to update user' },
      { status: 500 }
    );
  }
}

// Reset daily streak (called by cron job)
export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, userId } = body;

    if (action === 'check_streak') {
      // Check if user studied yesterday, if not reset streak
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      yesterday.setHours(0, 0, 0, 0);

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const sessions = await db.session.findMany({
        where: {
          userId,
          startTime: { gte: yesterday, lt: today }
        }
      });

      if (sessions.length === 0) {
        // No session yesterday, reset streak
        await db.user.update({
          where: { id: userId },
          data: { currentStreak: 0 }
        });

        return NextResponse.json({
          success: true,
          streakReset: true,
          message: 'Streak reset due to missed day'
        });
      }

      return NextResponse.json({
        success: true,
        streakReset: false
      });
    }

    if (action === 'update_level') {
      const user = await db.user.findUnique({
        where: { id: userId }
      });

      if (!user) {
        return NextResponse.json(
          { error: 'User not found' },
          { status: 404 }
        );
      }

      const newLevel = PsychologicalEngine.calculateLevel(user.totalXP);

      if (newLevel !== user.level) {
        await db.user.update({
          where: { id: userId },
          data: { level: newLevel }
        });

        return NextResponse.json({
          success: true,
          levelUp: true,
          newLevel,
          message: `Congratulations! You reached Level ${newLevel}!`
        });
      }

      return NextResponse.json({
        success: true,
        levelUp: false
      });
    }

    return NextResponse.json(
      { error: 'Invalid action' },
      { status: 400 }
    );

  } catch (error) {
    console.error('User patch error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}

// Helper: Initialize achievements in database
async function initializeAchievements() {
  const achievements = [
    { code: 'first_session', name: 'First Steps', description: 'Complete your first study session', icon: '🎯', xpReward: 50, coinReward: 20, conditionType: 'sessions', conditionValue: 1 },
    { code: 'streak_3', name: 'Triple Threat', description: 'Maintain a 3-day streak', icon: '🔥', xpReward: 100, coinReward: 30, conditionType: 'streak', conditionValue: 3 },
    { code: 'streak_7', name: 'Week Warrior', description: 'Maintain a 7-day streak', icon: '💪', xpReward: 200, coinReward: 50, conditionType: 'streak', conditionValue: 7 },
    { code: 'streak_14', name: 'Fortnight Fighter', description: 'Maintain a 14-day streak', icon: '⚔️', xpReward: 400, coinReward: 100, conditionType: 'streak', conditionValue: 14 },
    { code: 'streak_30', name: 'Monthly Master', description: 'Maintain a 30-day streak', icon: '👑', xpReward: 1000, coinReward: 200, conditionType: 'streak', conditionValue: 30 },
    { code: 'questions_50', name: 'Half Century', description: 'Answer 50 questions', icon: '📊', xpReward: 50, coinReward: 20, conditionType: 'questions', conditionValue: 50 },
    { code: 'questions_100', name: 'Century', description: 'Answer 100 questions', icon: '💯', xpReward: 100, coinReward: 30, conditionType: 'questions', conditionValue: 100 },
    { code: 'questions_500', name: 'Knowledge Seeker', description: 'Answer 500 questions', icon: '📚', xpReward: 300, coinReward: 100, conditionType: 'questions', conditionValue: 500 },
    { code: 'accuracy_80', name: 'Sharp Mind', description: 'Achieve 80%+ accuracy in a session', icon: '🎯', xpReward: 100, coinReward: 40, conditionType: 'accuracy', conditionValue: 80 },
    { code: 'accuracy_90', name: 'Sharp Shooter', description: 'Achieve 90%+ accuracy in a session', icon: '🎖️', xpReward: 150, coinReward: 50, conditionType: 'accuracy', conditionValue: 90 },
    { code: 'level_5', name: 'Rising Star', description: 'Reach Level 5', icon: '⭐', xpReward: 200, coinReward: 75, conditionType: 'level', conditionValue: 5 },
    { code: 'level_10', name: 'Elite Scholar', description: 'Reach Level 10', icon: '🌟', xpReward: 500, coinReward: 150, conditionType: 'level', conditionValue: 10 },
    { code: 'level_15', name: 'Master Mind', description: 'Reach Level 15', icon: '🏆', xpReward: 800, coinReward: 250, conditionType: 'level', conditionValue: 15 },
    { code: 'level_20', name: 'Legendary', description: 'Reach Level 20', icon: '💎', xpReward: 1500, coinReward: 500, conditionType: 'level', conditionValue: 20 }
  ];

  for (const achievement of achievements) {
    await db.achievement.upsert({
      where: { code: achievement.code },
      update: achievement,
      create: achievement
    });
  }
}

// Helper: Create day plan
async function createDayPlan(userId: string, dayNumber: number) {
  const date = new Date();
  date.setDate(date.getDate() + dayNumber - 1);

  // Determine phase
  let phase = 1;
  if (dayNumber > 60) phase = 4;
  else if (dayNumber > 45) phase = 3;
  else if (dayNumber > 30) phase = 2;

  const plan = await db.dailyPlan.create({
    data: {
      userId,
      dayNumber,
      date,
      phase,
      targetHours: phase === 1 ? 6 : phase === 2 ? 8 : 10,
      targetQuestions: 50 + (phase * 10)
    }
  });

  return plan;
}
