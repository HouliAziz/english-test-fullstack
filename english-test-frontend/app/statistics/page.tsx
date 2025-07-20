'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import { apiClient } from '@/lib/api';
import Navigation from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Trophy, 
  Target, 
  TrendingUp, 
  Clock, 
  Star, 
  Brain,
  BookOpen,
  Zap,
  Award,
  Calendar
} from 'lucide-react';

interface Statistics {
  total_points: number;
  quizzes_completed: number;
  lessons_completed: number;
  average_score: number;
  current_streak: number;
  total_time_spent: number;
  level_progress: {
    beginner: number;
    intermediate: number;
    advanced: number;
  };
  topic_performance: Array<{
    topic: string;
    average_score: number;
    attempts: number;
    best_score: number;
  }>;
  recent_activities: Array<{
    activity_type: string;
    topic: string;
    score: number;
    level: string;
    created_at: string;
  }>;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  earned: boolean;
  earned_date: string | null;
}
interface AchievementProgress {
  [key: string]: {
    name: string;
    description: string;
    icon: string;
    current: number;
    target: number;
    percentage: number;
  };
}

export default function StatisticsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [dashboard, setDashboard] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [progress, setProgress] = useState<AchievementProgress>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    const fetchAll = async () => {
      if (!user) return;
      setLoading(true);
      try {
        const dash = await apiClient.getDashboard();
        setDashboard(dash);
        setStatistics(dash.user_statistics);
        const ach = await apiClient.getAchievements();
        setAchievements(ach.achievements || []);
        setProgress(ach.progress || {});
      } catch (error) {
        console.error('Failed to fetch statistics or achievements:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [user]);

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  if (!user) return null;

  const topicIcons: { [key: string]: string } = {
    'Sports': '⚽',
    'Food': '🍕',
    'Colors': '🎨',
    'Money': '💰',
    'Travel': '✈️',
    'Animals': '🐱',
    'Business': '💼',
    'Grammar': '📝',
    'Vocabulary': '📚',
  };

  // Map backend fields to frontend expected fields, using type guards
  const statsRaw = statistics as any;
  const mappedStats = statsRaw ? {
    total_points: typeof statsRaw.experience_points === 'number' ? statsRaw.experience_points : 0,
    quizzes_completed: typeof statsRaw.total_quizzes_taken === 'number' ? statsRaw.total_quizzes_taken : 0,
    lessons_completed: typeof statsRaw.total_lessons_completed === 'number' ? statsRaw.total_lessons_completed : 0,
    average_score: typeof statsRaw.average_score === 'number' ? statsRaw.average_score : 0,
    current_streak: typeof statsRaw.current_streak_days === 'number' ? statsRaw.current_streak_days : 0,
    total_time_spent: typeof statsRaw.total_study_time_minutes === 'number' ? statsRaw.total_study_time_minutes : 0,
    level_progress: statsRaw.level_progress || {},
    topic_performance: Array.isArray(statsRaw.topic_scores)
      ? statsRaw.topic_scores
      : statsRaw.topic_scores && typeof statsRaw.topic_scores === 'object'
        ? Object.entries(statsRaw.topic_scores).map(([topic, score]) => ({ topic, average_score: Number(score), attempts: 0, best_score: Number(score) }))
        : [],
    recent_activities: Array.isArray(statsRaw.recent_attempts) ? statsRaw.recent_attempts : []
  } : null;

  if (!mappedStats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500 text-xl">Loading statistics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Statistics</h1>
          <p className="text-gray-600">Track your progress and achievements</p>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="animate-fade-in">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Points</CardTitle>
              <Trophy className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{mappedStats?.total_points || 0}</div>
              <p className="text-xs text-muted-foreground">Keep learning to earn more!</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Streak</CardTitle>
              <Zap className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{mappedStats?.current_streak || 0}</div>
              <p className="text-xs text-muted-foreground">days in a row</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{Math.round(mappedStats?.average_score || 0)}%</div>
              <p className="text-xs text-muted-foreground">across all quizzes</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Quizzes Completed</CardTitle>
              <BookOpen className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{mappedStats?.quizzes_completed || 0}</div>
              <p className="text-xs text-muted-foreground">total attempts</p>
            </CardContent>
          </Card>
        </div>

        {/* Topic Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card className="animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-red-600" />
                <span>Topic Performance</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {statistics?.topic_performance?.length ? statistics.topic_performance.map((topic: any, index: any) => (
                  <div key={topic.topic} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">{topicIcons[topic.topic.charAt(0).toUpperCase() + topic.topic.slice(1)] || '📚'}</span>
                        <span className="font-medium">{topic.topic}</span>
                      </div>
                      <div className="text-right text-sm text-gray-600">
                        <div>Avg: {Math.round(topic.average_score)}%</div>
                        <div>Best: {Math.round(topic.best_score)}%</div>
                      </div>
                    </div>
                    <Progress value={topic.average_score} className="h-2" />
                    <div className="text-xs text-gray-500">{topic.attempts} attempts</div>
                  </div>
                )) : (
                  <div className="text-center text-gray-500 py-8">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No quiz data yet. Start taking quizzes to see your performance!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-red-600" />
                <span>Achievements</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {achievements.length === 0 && (
                  <div className="text-gray-500">No achievements yet. Keep learning!</div>
                )}
                {achievements.map((achievement, index) => (
                  <div key={achievement.id} className={`flex items-center space-x-3 p-3 rounded-lg ${achievement.earned ? 'bg-green-50' : 'bg-gray-50'}`}>
                    <span className="text-2xl">{achievement.icon}</span>
                    <div className="flex-1">
                      <div className="font-medium">{achievement.name}</div>
                      <div className="text-sm text-gray-600">{achievement.description}</div>
                      {achievement.earned && achievement.earned_date && (
                        <div className="text-xs text-green-600 mt-1">Earned on {new Date(achievement.earned_date).toLocaleDateString()}</div>
                      )}
                    </div>
                    {achievement.earned && (
                      <Badge className="bg-green-100 text-green-800">Earned</Badge>
                    )}
                  </div>
                ))}
                {/* Show progress for unearned achievements */}
                {Object.values(progress).map((prog, idx) => (
                  <div key={prog.name} className="flex items-center space-x-3 p-3 rounded-lg bg-yellow-50">
                    <span className="text-2xl">{prog.icon}</span>
                    <div className="flex-1">
                      <div className="font-medium">{prog.name}</div>
                      <div className="text-sm text-gray-600">{prog.description}</div>
                      <div className="text-xs text-yellow-700 mt-1">Progress: {prog.current} / {prog.target} ({Math.round(prog.percentage)}%)</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activities */}
        <Card className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-red-600" />
              <span>Recent Activities</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Array.isArray(mappedStats.recent_activities) && mappedStats.recent_activities.length ? mappedStats.recent_activities.map((activity: any, index: any) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="text-sm text-gray-600">
                      {activity.created_at ? new Date(activity.created_at).toLocaleDateString() : ''}
                    </div>
                    <div className="font-medium">{activity.topic} {activity.activity_type}</div>
                    <Badge variant="outline" className={
                      activity.level === 'beginner' ? 'bg-green-100 text-green-800' :
                      activity.level === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }>
                      {activity.level}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-lg">{Math.round(activity.score)}%</div>
                    <div className="text-sm text-gray-600">
                      {activity.score >= 90 ? 'Excellent' :
                       activity.score >= 80 ? 'Good' :
                       activity.score >= 70 ? 'Average' : 'Needs Improvement'}
                    </div>
                  </div>
                </div>
              )) : (
                <div className="text-center text-gray-500 py-8">
                  <Clock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No recent activities. Start learning to see your progress here!</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}