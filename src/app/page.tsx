'use client'

import { useState, useEffect, useCallback } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Brain, BookOpen, Target, Trophy, MessageCircle, Settings, 
  Play, Pause, RotateCcw, Zap, Flame, Star, Clock, 
  CheckCircle, XCircle, ChevronRight, Award, TrendingUp,
  Users, Calendar, BarChart3, Send, Loader2, AlertCircle
} from 'lucide-react'

// Types
interface User {
  id: string
  name: string
  email: string
  totalXP: number
  currentStreak: number
  longestStreak: number
  focusCoins: number
  level: number
  mathsTheta: number
  physicsTheta: number
  chemistryTheta: number
  englishTheta: number
  totalStudyMinutes: number
  totalQuestions: number
  correctAnswers: number
}

interface Question {
  id: string
  questionText: string
  optionA: string
  optionB: string
  optionC: string
  optionD: string
  correctAnswer: string
  explanation: string
  difficulty: number
  topic?: { name: string }
  subject?: { name: string }
}

interface Session {
  id: string
  startTime: string
  endTime?: string
  durationMinutes: number
  questionsAttempted: number
  questionsCorrect: number
  xpEarned: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function JARVISDashboard() {
  // State
  const [user, setUser] = useState<User | null>(null)
  const [currentTab, setCurrentTab] = useState('dashboard')
  const [loading, setLoading] = useState(true)
  const [sessionActive, setSessionActive] = useState(false)
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionStats, setSessionStats] = useState({ questions: 0, correct: 0, xp: 0 })
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [chatMessages, setChatMessages] = useState<Message[]>([])
  const [chatInput, setChatInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [timer, setTimer] = useState(0)
  const [timerRunning, setTimerRunning] = useState(false)

  // Initialize user
  useEffect(() => {
    let mounted = true
    
    const init = async () => {
      try {
        // Try to get existing user
        const res = await fetch('/api/user?userId=demo-user')
        if (res.ok) {
          const data = await res.json()
          if (data.user && mounted) {
            setUser(data.user)
            setLoading(false)
            return
          }
        }
        
        // Create demo user
        const createRes = await fetch('/api/user', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'demo@jarvis.ai',
            name: 'JARVIS User',
            targetExam: 'Loyola Academy B.Sc CS Entrance',
            examDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString()
          })
        })
        
        if (createRes.ok) {
          const data = await createRes.json()
          if (mounted) setUser(data.user)
        }
      } catch (error) {
        console.error('Init error:', error)
        // Create mock user for demo
        if (mounted) {
          setUser({
            id: 'demo-user',
            name: 'Demo User',
            email: 'demo@jarvis.ai',
            totalXP: 1250,
            currentStreak: 7,
            longestStreak: 12,
            focusCoins: 350,
            level: 5,
            mathsTheta: 0.5,
            physicsTheta: 0.2,
            chemistryTheta: -0.3,
            englishTheta: 0.8,
            totalStudyMinutes: 2400,
            totalQuestions: 450,
            correctAnswers: 315
          })
        }
      }
      if (mounted) setLoading(false)
    }
    
    init()
    
    return () => { mounted = false }
  }, [])

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (timerRunning) {
      interval = setInterval(() => {
        setTimer(t => t + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [timerRunning])

  const startSession = async () => {
    try {
      const res = await fetch('/api/study-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user?.id,
          sessionType: 'practice',
          subjectFocus: 'maths'
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        setSessionId(data.session.id)
        setSessionActive(true)
        setTimerRunning(true)
        setTimer(0)
        setSessionStats({ questions: 0, correct: 0, xp: 0 })
        if (data.recommendedQuestions?.[0]) {
          setCurrentQuestion(data.recommendedQuestions[0])
        } else {
          await loadNextQuestion()
        }
      }
    } catch (error) {
      console.error('Start session error:', error)
      // Start mock session
      setSessionActive(true)
      setTimerRunning(true)
      setTimer(0)
      loadMockQuestion()
    }
  }

  const loadNextQuestion = async () => {
    try {
      const res = await fetch('/api/questions?subject=maths&limit=1&random=true')
      if (res.ok) {
        const data = await res.json()
        if (data.questions?.[0]) {
          setCurrentQuestion(data.questions[0])
          setSelectedAnswer(null)
          setShowResult(false)
        }
      }
    } catch (error) {
      loadMockQuestion()
    }
  }

  const loadMockQuestion = () => {
    setCurrentQuestion({
      id: 'mock-1',
      questionText: 'If A is a 3×3 matrix with determinant 5, what is the determinant of 2A?',
      optionA: '10',
      optionB: '30',
      optionC: '40',
      optionD: '15',
      correctAnswer: 'C',
      explanation: 'For a 3×3 matrix, det(kA) = k³ det(A). So det(2A) = 8 × 5 = 40.',
      difficulty: 0.5,
      topic: { name: 'Matrices' },
      subject: { name: 'Mathematics' }
    })
    setSelectedAnswer(null)
    setShowResult(false)
  }

  const submitAnswer = async (answer: string) => {
    if (!currentQuestion || showResult) return
    
    setSelectedAnswer(answer)
    setShowResult(true)
    
    const isCorrect = answer === currentQuestion.correctAnswer
    
    // Update local stats
    setSessionStats(prev => ({
      questions: prev.questions + 1,
      correct: prev.correct + (isCorrect ? 1 : 0),
      xp: prev.xp + (isCorrect ? 15 : 5)
    }))

    // Submit to API
    if (sessionId) {
      try {
        await fetch('/api/study-session', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId,
            userId: user?.id,
            questionId: currentQuestion.id,
            selectedAnswer: answer,
            timeTakenMs: timer * 1000
          })
        })
      } catch (error) {
        console.error('Submit error:', error)
      }
    }
  }

  const nextQuestion = () => {
    loadNextQuestion()
  }

  const endSession = async () => {
    setSessionActive(false)
    setTimerRunning(false)
    if (sessionId) {
      try {
        await fetch('/api/study-session', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sessionId })
        })
      } catch (error) {
        console.error('End session error:', error)
      }
    }
    setSessionId(null)
  }

  const sendChat = async () => {
    if (!chatInput.trim() || isTyping) return
    
    const userMessage = chatInput.trim()
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setChatInput('')
    setIsTyping(true)
    
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          subject: 'maths',
          context: chatMessages.slice(-4)
        })
      })
      
      if (res.ok) {
        const data = await res.json()
        setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      } else {
        // Mock response
        setTimeout(() => {
          setChatMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `Great question! Let me explain this concept for your Loyola Academy entrance preparation.\n\nThis topic is important because it appears frequently in the exam. Focus on understanding the core principles rather than memorizing formulas.\n\nKya aap aur kuchh puchhna chahte ho?` 
          }])
        }, 1000)
      }
    } catch (error) {
      setTimeout(() => {
        setChatMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Main aapki madad ke liye hazir hoon! Yeh topic B.Sc CS entrance ke liye bahut important hai.\n\nAap is concept ko practice karein aur daily questions solve karein.` 
        }])
      }, 1000)
    }
    
    setIsTyping(false)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getThetaColor = (theta: number) => {
    if (theta < -1) return 'text-red-500'
    if (theta < 0) return 'text-orange-500'
    if (theta < 1) return 'text-yellow-500'
    if (theta < 2) return 'text-green-500'
    return 'text-blue-500'
  }

  const getThetaLabel = (theta: number) => {
    if (theta < -2) return 'Beginner'
    if (theta < -1) return 'Developing'
    if (theta < 0) return 'Competent'
    if (theta < 1) return 'Proficient'
    if (theta < 2) return 'Advanced'
    return 'Expert'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-purple-300 text-lg">JARVIS Initializing...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-purple-800/50 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">JARVIS 8.0 ULTRA</h1>
              <p className="text-xs text-purple-300">Loyola Academy B.Sc CS Entrance</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            {/* XP & Level */}
            <div className="flex items-center gap-2 bg-purple-900/50 px-4 py-2 rounded-full">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="text-yellow-400 font-bold">{user?.totalXP || 0} XP</span>
              <Badge variant="secondary" className="bg-purple-700">Lv.{user?.level || 1}</Badge>
            </div>
            
            {/* Streak */}
            <div className="flex items-center gap-2 bg-orange-900/50 px-4 py-2 rounded-full">
              <Flame className="w-4 h-4 text-orange-400" />
              <span className="text-orange-400 font-bold">{user?.currentStreak || 0} days</span>
            </div>
            
            {/* Coins */}
            <div className="flex items-center gap-2 bg-yellow-900/50 px-4 py-2 rounded-full">
              <Zap className="w-4 h-4 text-yellow-300" />
              <span className="text-yellow-300 font-bold">{user?.focusCoins || 0}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="space-y-6">
          <TabsList className="bg-purple-900/30 border border-purple-700/50 grid grid-cols-6 w-full max-w-2xl mx-auto">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-purple-700">
              <BarChart3 className="w-4 h-4 mr-2" /> Dashboard
            </TabsTrigger>
            <TabsTrigger value="study" className="data-[state=active]:bg-purple-700">
              <BookOpen className="w-4 h-4 mr-2" /> Study
            </TabsTrigger>
            <TabsTrigger value="chat" className="data-[state=active]:bg-purple-700">
              <MessageCircle className="w-4 h-4 mr-2" /> AI Tutor
            </TabsTrigger>
            <TabsTrigger value="interview" className="data-[state=active]:bg-purple-700">
              <Users className="w-4 h-4 mr-2" /> Interview
            </TabsTrigger>
            <TabsTrigger value="analytics" className="data-[state=active]:bg-purple-700">
              <TrendingUp className="w-4 h-4 mr-2" /> Analytics
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-purple-700">
              <Settings className="w-4 h-4 mr-2" /> Settings
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 border-purple-700/50">
                <CardHeader className="pb-2">
                  <CardDescription className="text-purple-300">Total Study Time</CardDescription>
                  <CardTitle className="text-2xl text-white">
                    {Math.floor((user?.totalStudyMinutes || 0) / 60)}h {(user?.totalStudyMinutes || 0) % 60}m
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-green-400 text-sm">
                    <TrendingUp className="w-4 h-4 mr-1" /> +15% this week
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 border-blue-700/50">
                <CardHeader className="pb-2">
                  <CardDescription className="text-blue-300">Questions Solved</CardDescription>
                  <CardTitle className="text-2xl text-white">{user?.totalQuestions || 0}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-blue-300 text-sm">
                    Accuracy: {user?.totalQuestions ? Math.round(((user?.correctAnswers || 0) / user.totalQuestions) * 100) : 0}%
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-900/50 to-green-800/30 border-green-700/50">
                <CardHeader className="pb-2">
                  <CardDescription className="text-green-300">Current Level</CardDescription>
                  <CardTitle className="text-2xl text-white">Level {user?.level || 1}</CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress value={((user?.totalXP || 0) % 500) / 5} className="h-2" />
                  <p className="text-green-300 text-xs mt-1">
                    {500 - ((user?.totalXP || 0) % 500)} XP to next level
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-900/50 to-orange-800/30 border-orange-700/50">
                <CardHeader className="pb-2">
                  <CardDescription className="text-orange-300">Current Streak</CardDescription>
                  <CardTitle className="text-2xl text-white flex items-center gap-2">
                    <Flame className="w-6 h-6 text-orange-400" />
                    {user?.currentStreak || 0} days
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-orange-300 text-sm">
                    Best: {user?.longestStreak || 0} days
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Subject Abilities (IRT Theta) */}
            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Target className="w-5 h-5 text-purple-400" />
                  Subject Ability (IRT Theta Scores)
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Your adaptive learning progress based on Item Response Theory
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {[
                    { name: 'Mathematics', theta: user?.mathsTheta || 0, marks: 20 },
                    { name: 'Physics', theta: user?.physicsTheta || 0, marks: 15 },
                    { name: 'Chemistry', theta: user?.chemistryTheta || 0, marks: 8 },
                    { name: 'English', theta: user?.englishTheta || 0, marks: 7 }
                  ].map(subject => (
                    <div key={subject.name} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-white font-medium">{subject.name}</span>
                        <span className={`font-bold ${getThetaColor(subject.theta)}`}>
                          {getThetaLabel(subject.theta)}
                        </span>
                      </div>
                      <Progress 
                        value={((subject.theta + 3) / 6) * 100} 
                        className="h-3"
                      />
                      <div className="flex justify-between text-xs text-slate-400">
                        <span>θ = {subject.theta.toFixed(2)}</span>
                        <span>{subject.marks} marks</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                onClick={() => { setCurrentTab('study'); startSession(); }}
                className="h-24 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-lg"
              >
                <Play className="w-6 h-6 mr-3" /> Start Study Session
              </Button>
              <Button 
                onClick={() => setCurrentTab('chat')}
                className="h-24 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-lg"
              >
                <MessageCircle className="w-6 h-6 mr-3" /> Ask AI Tutor
              </Button>
              <Button 
                onClick={() => setCurrentTab('interview')}
                className="h-24 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-lg"
              >
                <Users className="w-6 h-6 mr-3" /> Practice Interview
              </Button>
            </div>
          </TabsContent>

          {/* Study Tab */}
          <TabsContent value="study" className="space-y-6">
            {!sessionActive ? (
              <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
                <CardContent className="pt-6 text-center">
                  <BookOpen className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-white mb-2">Ready to Study?</h2>
                  <p className="text-slate-400 mb-6">
                    Start an adaptive practice session. JARVIS will select questions based on your IRT theta scores.
                  </p>
                  <Button 
                    onClick={startSession}
                    size="lg"
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  >
                    <Play className="w-5 h-5 mr-2" /> Start Session
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {/* Session Header */}
                <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-700/50">
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-3xl font-mono text-white">{formatTime(timer)}</div>
                          <div className="text-purple-300 text-sm">Time</div>
                        </div>
                        <Separator orientation="vertical" className="h-12 bg-purple-700" />
                        <div className="text-center">
                          <div className="text-2xl font-bold text-white">{sessionStats.questions}</div>
                          <div className="text-purple-300 text-sm">Questions</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">{sessionStats.correct}</div>
                          <div className="text-purple-300 text-sm">Correct</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-yellow-400">{sessionStats.xp}</div>
                          <div className="text-purple-300 text-sm">XP Earned</div>
                        </div>
                      </div>
                      <Button 
                        onClick={endSession}
                        variant="destructive"
                        className="bg-red-600 hover:bg-red-700"
                      >
                        End Session
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Question Card */}
                {currentQuestion && (
                  <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <Badge className="mb-2">{currentQuestion.subject?.name || 'Mathematics'}</Badge>
                          <Badge variant="outline" className="ml-2">{currentQuestion.topic?.name || 'Topic'}</Badge>
                        </div>
                        <Badge variant="secondary">
                          Difficulty: {currentQuestion.difficulty.toFixed(1)}
                        </Badge>
                      </div>
                      <CardTitle className="text-white text-xl mt-4">
                        {currentQuestion.questionText}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {['A', 'B', 'C', 'D'].map(opt => {
                        const optionText = currentQuestion[`option${opt}` as keyof Question] as string
                        if (!optionText) return null
                        
                        let buttonClass = "w-full p-4 text-left rounded-lg border-2 transition-all "
                        
                        if (showResult) {
                          if (opt === currentQuestion.correctAnswer) {
                            buttonClass += "border-green-500 bg-green-900/30 text-green-300"
                          } else if (opt === selectedAnswer) {
                            buttonClass += "border-red-500 bg-red-900/30 text-red-300"
                          } else {
                            buttonClass += "border-slate-700 bg-slate-800/50 text-slate-400"
                          }
                        } else if (selectedAnswer === opt) {
                          buttonClass += "border-purple-500 bg-purple-900/30 text-white"
                        } else {
                          buttonClass += "border-slate-700 bg-slate-800/50 text-white hover:border-purple-500 hover:bg-purple-900/20"
                        }
                        
                        return (
                          <button
                            key={opt}
                            onClick={() => submitAnswer(opt)}
                            disabled={showResult}
                            className={buttonClass}
                          >
                            <span className="font-bold mr-3">{opt}.</span>
                            {optionText}
                            {showResult && opt === currentQuestion.correctAnswer && (
                              <CheckCircle className="w-5 h-5 inline-block ml-2 text-green-400" />
                            )}
                            {showResult && opt === selectedAnswer && opt !== currentQuestion.correctAnswer && (
                              <XCircle className="w-5 h-5 inline-block ml-2 text-red-400" />
                            )}
                          </button>
                        )
                      })}
                      
                      {showResult && (
                        <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                          <h4 className="font-bold text-purple-300 mb-2">Explanation:</h4>
                          <p className="text-slate-300">{currentQuestion.explanation}</p>
                          <Button 
                            onClick={nextQuestion}
                            className="mt-4 bg-purple-600 hover:bg-purple-700"
                          >
                            Next Question <ChevronRight className="w-4 h-4 ml-1" />
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50 h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <MessageCircle className="w-5 h-5 text-green-400" />
                  AI Tutor - Ask Anything
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Get instant explanations for Maths, Physics, Chemistry & English
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <ScrollArea className="flex-1 pr-4">
                  {chatMessages.length === 0 ? (
                    <div className="text-center text-slate-400 py-12">
                      <Brain className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                      <p>Main JARVIS hoon. Aapka AI tutor.</p>
                      <p className="text-sm mt-2">Koi bhi question poocho - Maths, Physics, Chemistry, English!</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {chatMessages.map((msg, i) => (
                        <div 
                          key={i}
                          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-[80%] p-4 rounded-lg ${
                            msg.role === 'user' 
                              ? 'bg-purple-600 text-white' 
                              : 'bg-slate-700 text-slate-100'
                          }`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                          </div>
                        </div>
                      ))}
                      {isTyping && (
                        <div className="flex justify-start">
                          <div className="bg-slate-700 p-4 rounded-lg">
                            <Loader2 className="w-5 h-5 animate-spin text-purple-400" />
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </ScrollArea>
                
                <div className="mt-4 flex gap-2">
                  <Input
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Type your question..."
                    className="bg-slate-800 border-slate-700 text-white"
                    onKeyPress={(e) => e.key === 'Enter' && sendChat()}
                  />
                  <Button onClick={sendChat} className="bg-green-600 hover:bg-green-700">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Interview Tab */}
          <TabsContent value="interview" className="space-y-6">
            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Users className="w-5 h-5 text-orange-400" />
                  Interview Preparation
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Practice mock interviews for Loyola Academy admission. Parents MUST accompany for actual interview.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Interview Categories */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-white">Question Categories</h3>
                    {[
                      { name: 'Personal Introduction', icon: '👤', count: 8 },
                      { name: 'Academic Questions', icon: '📚', count: 8 },
                      { name: 'CS Basics', icon: '💻', count: 8 },
                      { name: 'Current Affairs', icon: '📰', count: 7 },
                      { name: 'Situational', icon: '🎯', count: 5 }
                    ].map((cat, i) => (
                      <Button 
                        key={i}
                        variant="outline"
                        className="w-full justify-start text-left bg-slate-800/50 border-slate-700 hover:bg-slate-700"
                      >
                        <span className="text-2xl mr-3">{cat.icon}</span>
                        <span className="text-white">{cat.name}</span>
                        <Badge variant="secondary" className="ml-auto">{cat.count}</Badge>
                      </Button>
                    ))}
                  </div>
                  
                  {/* Interview Tips */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-white">Interview Tips</h3>
                    <div className="bg-orange-900/30 border border-orange-700/50 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-orange-400 mt-0.5" />
                        <div>
                          <h4 className="font-bold text-orange-300">Important Notice</h4>
                          <p className="text-sm text-orange-200 mt-1">
                            Parents MUST accompany candidates for the interview at Loyola Academy. This is mandatory.
                          </p>
                        </div>
                      </div>
                    </div>
                    <ul className="space-y-2 text-slate-300 text-sm">
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                        Dress formally for the interview
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                        Bring original documents for verification
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                        Practice common questions about CS
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                        Be ready to explain why Loyola Academy
                      </li>
                    </ul>
                    <Button className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700">
                      Start Mock Interview
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Performance Chart */}
              <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-400" />
                    Performance Overview
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { day: 'Mon', accuracy: 75, questions: 45 },
                      { day: 'Tue', accuracy: 80, questions: 50 },
                      { day: 'Wed', accuracy: 72, questions: 40 },
                      { day: 'Thu', accuracy: 85, questions: 55 },
                      { day: 'Fri', accuracy: 78, questions: 48 },
                      { day: 'Sat', accuracy: 82, questions: 52 },
                      { day: 'Sun', accuracy: 88, questions: 60 }
                    ].map((day, i) => (
                      <div key={i} className="flex items-center gap-4">
                        <span className="text-slate-400 w-10">{day.day}</span>
                        <Progress value={day.accuracy} className="flex-1 h-2" />
                        <span className="text-white w-16 text-right">{day.accuracy}%</span>
                        <span className="text-slate-400 w-12 text-right">{day.questions}Q</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Topic Mastery */}
              <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-purple-400" />
                    Topic Mastery
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { name: 'Matrices', mastery: 85, subject: 'Maths' },
                      { name: 'Calculus', mastery: 70, subject: 'Maths' },
                      { name: 'Mechanics', mastery: 65, subject: 'Physics' },
                      { name: 'Thermodynamics', mastery: 55, subject: 'Physics' },
                      { name: 'Organic Chemistry', mastery: 45, subject: 'Chemistry' }
                    ].map((topic, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between">
                          <span className="text-white">{topic.name}</span>
                          <span className={`font-bold ${
                            topic.mastery >= 70 ? 'text-green-400' :
                            topic.mastery >= 50 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {topic.mastery}%
                          </span>
                        </div>
                        <Progress value={topic.mastery} className="h-2" />
                        <span className="text-xs text-slate-400">{topic.subject}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Predicted Score */}
            <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-700/50">
              <CardContent className="pt-6">
                <div className="text-center">
                  <h3 className="text-lg font-bold text-purple-300 mb-2">Predicted Exam Score</h3>
                  <div className="text-5xl font-bold text-white mb-2">
                    {Math.round((
                      ((user?.mathsTheta || 0) + 3) / 6 * 20 +
                      ((user?.physicsTheta || 0) + 3) / 6 * 15 +
                      (((user?.chemistryTheta || 0) + (user?.englishTheta || 0)) / 2 + 3) / 6 * 15
                    ))}/50
                  </div>
                  <p className="text-purple-300">
                    Based on IRT theta scores • Exam: 50 questions in 50 minutes
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <Card className="bg-gradient-to-br from-slate-900/80 to-slate-800/50 border-slate-700/50">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Settings className="w-5 h-5 text-slate-400" />
                  Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-bold text-white">Profile</h3>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Name</Label>
                      <Input defaultValue={user?.name} className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Email</Label>
                      <Input defaultValue={user?.email} className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Target Exam</Label>
                      <Input defaultValue="Loyola Academy B.Sc CS Entrance" className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="font-bold text-white">Study Preferences</h3>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Daily Study Hours</Label>
                      <Input type="number" defaultValue="8" className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Wake Up Time</Label>
                      <Input type="time" defaultValue="05:00" className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-slate-300">Sleep Time</Label>
                      <Input type="time" defaultValue="21:00" className="bg-slate-800 border-slate-700 text-white" />
                    </div>
                  </div>
                </div>
                
                <Separator className="bg-slate-700" />
                
                <div className="space-y-4">
                  <h3 className="font-bold text-white">Root Commands (Termux)</h3>
                  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-sm text-slate-300">
                    <p className="mb-2">For rooted Android devices, JARVIS can:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Force-stop distracting apps during study sessions</li>
                      <li>Block network access to social media</li>
                      <li>Monitor foreground app usage 24/7</li>
                      <li>Send input events (tap, swipe) automatically</li>
                    </ul>
                  </div>
                  <Button variant="outline" className="border-purple-700 text-purple-300 hover:bg-purple-900/30">
                    Configure Root Permissions
                  </Button>
                </div>
                
                <Button className="bg-purple-600 hover:bg-purple-700">
                  Save Settings
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-purple-800/50 bg-black/20 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-slate-400 text-sm">
          <p>JARVIS 8.0 ULTRA • Loyola Academy B.Sc CS Entrance Preparation</p>
          <p className="mt-1">Exam Pattern: 50 Questions • 50 Minutes • 1 Min/Question</p>
          <p className="mt-1 text-purple-400">
            IRT Adaptive Testing • SM-2 Spaced Repetition • Psychology-Backed Learning
          </p>
        </div>
      </footer>
    </div>
  )
}
