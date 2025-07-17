'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/providers/AuthProvider';
import Navigation from '@/components/layout/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BookOpen, 
  Play, 
  CheckCircle, 
  Lock, 
  Clock, 
  Star,
  Search,
  Filter,
  TrendingUp,
  Users,
  Award,
  Zap,
  Target,
  Globe,
  MessageCircle,
  Headphones,
  FileText,
  Video
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Lesson {
  id: string;
  title: string;
  description: string;
  category: string;
  level: 'Beginner' | 'Intermediate' | 'Advanced';
  duration: number; // in minutes
  progress: number; // 0-100
  isCompleted: boolean;
  isLocked: boolean;
  rating: number;
  studentsCount: number;
  type: 'video' | 'audio' | 'text' | 'interactive';
  icon: string;
}

const lessonCategories = [
  { id: 'grammar', name: 'Grammar', icon: '📝', color: 'bg-blue-100 text-blue-800' },
  { id: 'vocabulary', name: 'Vocabulary', icon: '📚', color: 'bg-green-100 text-green-800' },
  { id: 'speaking', name: 'Speaking', icon: '🗣️', color: 'bg-red-100 text-red-800' },
  { id: 'listening', name: 'Listening', icon: '👂', color: 'bg-purple-100 text-purple-800' },
  { id: 'reading', name: 'Reading', icon: '📖', color: 'bg-yellow-100 text-yellow-800' },
  { id: 'writing', name: 'Writing', icon: '✍️', color: 'bg-indigo-100 text-indigo-800' },
];

const sampleLessons: Lesson[] = [
  {
    id: '1',
    title: 'Present Simple Tense',
    description: 'Learn the basics of present simple tense with examples and exercises',
    category: 'grammar',
    level: 'Beginner',
    duration: 15,
    progress: 100,
    isCompleted: true,
    isLocked: false,
    rating: 4.8,
    studentsCount: 1250,
    type: 'interactive',
    icon: '📝'
  },
  {
    id: '2',
    title: 'Daily Routine Vocabulary',
    description: 'Essential words and phrases for describing your daily activities',
    category: 'vocabulary',
    level: 'Beginner',
    duration: 20,
    progress: 75,
    isCompleted: false,
    isLocked: false,
    rating: 4.6,
    studentsCount: 980,
    type: 'video',
    icon: '📚'
  },
  {
    id: '3',
    title: 'Pronunciation Practice',
    description: 'Improve your English pronunciation with guided exercises',
    category: 'speaking',
    level: 'Intermediate',
    duration: 25,
    progress: 0,
    isCompleted: false,
    isLocked: false,
    rating: 4.9,
    studentsCount: 750,
    type: 'audio',
    icon: '🗣️'
  },
  {
    id: '4',
    title: 'Business English Conversations',
    description: 'Professional English for workplace communication',
    category: 'speaking',
    level: 'Advanced',
    duration: 30,
    progress: 0,
    isCompleted: false,
    isLocked: true,
    rating: 4.7,
    studentsCount: 420,
    type: 'video',
    icon: '💼'
  },
  {
    id: '5',
    title: 'Listening to News',
    description: 'Improve listening skills with real news broadcasts',
    category: 'listening',
    level: 'Intermediate',
    duration: 18,
    progress: 30,
    isCompleted: false,
    isLocked: false,
    rating: 4.5,
    studentsCount: 650,
    type: 'audio',
    icon: '📺'
  },
  {
    id: '6',
    title: 'Essay Writing Basics',
    description: 'Learn to write clear and structured essays in English',
    category: 'writing',
    level: 'Intermediate',
    duration: 35,
    progress: 0,
    isCompleted: false,
    isLocked: false,
    rating: 4.4,
    studentsCount: 380,
    type: 'text',
    icon: '✍️'
  },
  {
    id: '7',
    title: 'Reading Comprehension',
    description: 'Strategies for better understanding of English texts',
    category: 'reading',
    level: 'Beginner',
    duration: 22,
    progress: 50,
    isCompleted: false,
    isLocked: false,
    rating: 4.6,
    studentsCount: 890,
    type: 'text',
    icon: '📖'
  },
  {
    id: '8',
    title: 'Past Tense Mastery',
    description: 'Complete guide to past simple and past continuous',
    category: 'grammar',
    level: 'Intermediate',
    duration: 28,
    progress: 0,
    isCompleted: false,
    isLocked: false,
    rating: 4.8,
    studentsCount: 1100,
    type: 'interactive',
    icon: '⏰'
  }
];

export default function LessonsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const { toast } = useToast();
  
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [lessons, setLessons] = useState<Lesson[]>(sampleLessons);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, isLoading, router]);

  const filteredLessons = lessons.filter(lesson => {
    const matchesCategory = selectedCategory === 'all' || lesson.category === selectedCategory;
    const matchesLevel = selectedLevel === 'all' || lesson.level.toLowerCase() === selectedLevel;
    const matchesSearch = lesson.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         lesson.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesCategory && matchesLevel && matchesSearch;
  });

  const startLesson = (lessonId: string) => {
    const lesson = lessons.find(l => l.id === lessonId);
    if (lesson?.isLocked) {
      toast({
        title: "Lesson Locked",
        description: "Complete previous lessons to unlock this one.",
        variant: "destructive",
      });
      return;
    }
    
    toast({
      title: "Starting Lesson",
      description: `Opening "${lesson?.title}"...`,
    });
    // Here you would navigate to the actual lesson content
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <Video className="w-4 h-4" />;
      case 'audio': return <Headphones className="w-4 h-4" />;
      case 'text': return <FileText className="w-4 h-4" />;
      case 'interactive': return <Zap className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Beginner': return 'bg-green-100 text-green-800';
      case 'Intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'Advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">English Lessons</h1>
          <p className="text-gray-600">Structured learning path to improve your English skills</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="animate-fade-in">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Lessons</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {lessons.filter(l => l.isCompleted).length}
              </div>
              <p className="text-xs text-muted-foreground">
                of {lessons.length} total lessons
              </p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {lessons.filter(l => l.progress > 0 && !l.isCompleted).length}
              </div>
              <p className="text-xs text-muted-foreground">lessons started</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Study Time</CardTitle>
              <Clock className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(lessons.filter(l => l.isCompleted).reduce((acc, l) => acc + l.duration, 0) / 60)}h
              </div>
              <p className="text-xs text-muted-foreground">total completed</p>
            </CardContent>
          </Card>

          <Card className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
              <Star className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">4.7</div>
              <p className="text-xs text-muted-foreground">across all lessons</p>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card className="mb-8 animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-red-600" />
              <span>Find Your Perfect Lesson</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search lessons..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Category Filter */}
              <div>
                <h4 className="font-medium mb-2">Categories</h4>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={selectedCategory === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory('all')}
                    className={selectedCategory === 'all' ? 'bg-red-600 hover:bg-red-700' : ''}
                  >
                    All Categories
                  </Button>
                  {lessonCategories.map((category) => (
                    <Button
                      key={category.id}
                      variant={selectedCategory === category.id ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedCategory(category.id)}
                      className={selectedCategory === category.id ? 'bg-red-600 hover:bg-red-700' : ''}
                    >
                      <span className="mr-1">{category.icon}</span>
                      {category.name}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Level Filter */}
              <div>
                <h4 className="font-medium mb-2">Difficulty Level</h4>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={selectedLevel === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedLevel('all')}
                    className={selectedLevel === 'all' ? 'bg-red-600 hover:bg-red-700' : ''}
                  >
                    All Levels
                  </Button>
                  {['beginner', 'intermediate', 'advanced'].map((level) => (
                    <Button
                      key={level}
                      variant={selectedLevel === level ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedLevel(level)}
                      className={selectedLevel === level ? 'bg-red-600 hover:bg-red-700' : ''}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lessons Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredLessons.map((lesson, index) => (
            <Card 
              key={lesson.id} 
              className={`animate-slide-up hover:shadow-lg transition-shadow ${
                lesson.isLocked ? 'opacity-60' : ''
              }`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{lesson.icon}</span>
                    <div>
                      <CardTitle className="text-lg">{lesson.title}</CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge className={getLevelColor(lesson.level)}>
                          {lesson.level}
                        </Badge>
                        <Badge variant="outline" className="flex items-center space-x-1">
                          {getTypeIcon(lesson.type)}
                          <span className="capitalize">{lesson.type}</span>
                        </Badge>
                      </div>
                    </div>
                  </div>
                  {lesson.isLocked && <Lock className="w-5 h-5 text-gray-400" />}
                  {lesson.isCompleted && <CheckCircle className="w-5 h-5 text-green-600" />}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm mb-4">{lesson.description}</p>
                
                {/* Progress Bar */}
                {lesson.progress > 0 && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{lesson.progress}%</span>
                    </div>
                    <Progress value={lesson.progress} className="h-2" />
                  </div>
                )}

                {/* Lesson Stats */}
                <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{lesson.duration} min</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{lesson.studentsCount}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-500" />
                    <span>{lesson.rating}</span>
                  </div>
                </div>

                {/* Action Button */}
                <Button
                  onClick={() => startLesson(lesson.id)}
                  disabled={lesson.isLocked}
                  className={`w-full ${
                    lesson.isCompleted 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : lesson.progress > 0
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : 'gradient-red hover:opacity-90'
                  } text-white`}
                >
                  {lesson.isLocked ? (
                    <>
                      <Lock className="w-4 h-4 mr-2" />
                      Locked
                    </>
                  ) : lesson.isCompleted ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Review
                    </>
                  ) : lesson.progress > 0 ? (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Continue
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Start Lesson
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* No Results */}
        {filteredLessons.length === 0 && (
          <Card className="text-center py-12">
            <CardContent>
              <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No lessons found</h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your filters or search terms to find more lessons.
              </p>
              <Button 
                onClick={() => {
                  setSelectedCategory('all');
                  setSelectedLevel('all');
                  setSearchQuery('');
                }}
                variant="outline"
              >
                Clear Filters
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}