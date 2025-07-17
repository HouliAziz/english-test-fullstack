'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import Navigation from '@/components/layout/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BookOpen, 
  Brain, 
  Target, 
  Trophy, 
  Clock, 
  Play,
  Star,
  TrendingUp,
  Zap
} from 'lucide-react';
import { apiClient } from '@/lib/api';

const topics = [
  { name: 'Sports', icon: '⚽', color: 'bg-blue-100 text-blue-800' },
  { name: 'Food', icon: '🍕', color: 'bg-green-100 text-green-800' },
  { name: 'Colors', icon: '🎨', color: 'bg-purple-100 text-purple-800' },
  { name: 'Money', icon: '💰', color: 'bg-yellow-100 text-yellow-800' },
  { name: 'Travel', icon: '✈️', color: 'bg-indigo-100 text-indigo-800' },
  { name: 'Animals', icon: '🐱', color: 'bg-pink-100 text-pink-800' },
];

const levels = [
  { name: 'Easy', description: 'Perfect for beginners', color: 'bg-green-500' },
  { name: 'Medium', description: 'Challenge yourself', color: 'bg-yellow-500' },
  { name: 'Hard', description: 'Expert level', color: 'bg-red-500' },
];

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    const fetchDashboard = async () => {
      if (!user) return;
      setLoading(true);
      try {
        const dash = await apiClient.getDashboard();
        setDashboard(dash);
      } catch (error) {
        console.error('Failed to fetch dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [user]);

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  if (!user) return null;

  // Extract real stats from dashboard
  const stats = dashboard?.user_statistics || {};
  const weeklyProgress = dashboard?.weekly_progress || {};
  // Calculate today's progress
  const today = new Date().toISOString().slice(0, 10);
  const todayStats = weeklyProgress[today] || { quizzes_taken: 0, average_score: 0, time_spent: 0 };
  // Example: lessons completed today (if available)
  const lessonsCompleted = stats.total_lessons_completed || 0;
  const quizzesCompleted = stats.total_quizzes_taken || 0;
  // Example: weekly goal (quizzes taken this week)
  const quizzesThisWeek = Object.values(weeklyProgress).reduce((sum: number, day: any) => sum + (day.quizzes_taken || 0), 0);
  // Example: next milestone (e.g., next 100 points)
  const xp = stats.experience_points || 0;
  const nextMilestone = Math.ceil((xp + 1) / 100) * 100;
  const pointsToGo = nextMilestone - xp;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8 animate-fade-in">
          <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-xl p-6 text-white">
            <h1 className="text-3xl font-bold mb-2">Welcome back, {user.name}! 👋</h1>
            <p className="text-red-100 text-lg">Ready to continue your English learning journey?</p>
            <div className="mt-4 flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Trophy className="w-5 h-5" />
                <span className="font-semibold">{stats.experience_points || 0} points</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5" />
                <span className="font-semibold">{stats.current_streak_days || 0} day streak</span>
              </div>
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5" />
                <span className="font-semibold capitalize">{stats.current_level || user.level}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="animate-slide-up">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{todayStats.quizzes_taken || 0} quizzes</div>
              <Progress value={todayStats.average_score || 0} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">Avg Score: {Math.round(todayStats.average_score || 0)}%</p>
            </CardContent>
          </Card>

          <Card className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Weekly Goal</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{quizzesThisWeek} quizzes</div>
              <Progress value={Math.min(100, (quizzesThisWeek / 15) * 100)} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">Goal: 15 quizzes/week</p>
            </CardContent>
          </Card>

          <Card className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Next Milestone</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{nextMilestone}</div>
              <Progress value={Math.min(100, (xp / nextMilestone) * 100)} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-2">{pointsToGo} points to go</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Start Quiz */}
          <Card className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-red-600" />
                <span>Start a Quiz</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">Test your knowledge with our adaptive AI-powered quizzes</p>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Choose a Topic</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {topics.map((topic) => (
                      <Badge key={topic.name} variant="outline" className={`${topic.color} cursor-pointer hover:opacity-80 transition-opacity justify-start p-2`}>
                        <span className="mr-2">{topic.icon}</span>
                        {topic.name}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Select Difficulty</h4>
                  <div className="space-y-2">
                    {levels.map((level) => (
                      <div key={level.name} className="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-50 cursor-pointer">
                        <div className={`w-3 h-3 rounded-full ${level.color}`}></div>
                        <div>
                          <span className="font-medium">{level.name}</span>
                          <p className="text-sm text-gray-600">{level.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <Button className="w-full gradient-red text-white hover:opacity-90" onClick={() => router.push('/ai')}>
                  <Play className="w-4 h-4 mr-2" />
                  Start Quiz
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Start Lesson */}
          <Card className="animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-red-600" />
                <span>Start a Lesson</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">Learn new words and improve your vocabulary</p>
              
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Recommended for You</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span>Business English</span>
                      <Badge variant="outline">Intermediate</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Daily Conversations</span>
                      <Badge variant="outline">Easy</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Grammar Basics</span>
                      <Badge variant="outline">Easy</Badge>
                    </div>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full border-red-200 text-red-600 hover:bg-red-50">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Browse All Lessons
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="animate-slide-up" style={{ animationDelay: '0.5s' }}>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-3 bg-green-50 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="font-medium">Food Quiz - Hard Level</p>
                  <p className="text-sm text-gray-600">Scored 85 points • 2 hours ago</p>
                </div>
                <Badge className="bg-green-100 text-green-800">+85 points</Badge>
              </div>
              
              <div className="flex items-center space-x-4 p-3 bg-blue-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="font-medium">Sports Vocabulary Lesson</p>
                  <p className="text-sm text-gray-600">Completed • Yesterday</p>
                </div>
                <Badge className="bg-blue-100 text-blue-800">Completed</Badge>
              </div>
              
              <div className="flex items-center space-x-4 p-3 bg-yellow-50 rounded-lg">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="font-medium">Colors Quiz - Medium Level</p>
                  <p className="text-sm text-gray-600">Scored 70 points • 2 days ago</p>
                </div>
                <Badge className="bg-yellow-100 text-yellow-800">+70 points</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}