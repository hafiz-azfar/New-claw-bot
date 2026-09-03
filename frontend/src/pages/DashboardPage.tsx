import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore, useCourseStore, useLiveSessionStore } from '../store';
import { courseService, liveSessionService } from '../services/api';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { courses, fetchCourses } = useCourseStore();
  const { joinSession } = useLiveSessionStore();
  const [liveSessions, setLiveSessions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      await Promise.all([fetchCourses(), loadLiveSessions()]);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadLiveSessions = async () => {
    try {
      const sessions = await liveSessionService.getLiveSessions();
      setLiveSessions(sessions);
    } catch (error) {
      console.error('Failed to load live sessions:', error);
    }
  };

  const handleJoinClass = async (sessionId: number) => {
    try {
      await joinSession(sessionId);
      navigate(`/classroom/${sessionId}`);
    } catch (error) {
      console.error('Failed to join session:', error);
    }
  };

  const handleCreateSession = async () => {
    // TODO: Open modal to create new session
    alert('Create Session Modal - To be implemented');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">🎓 Al-Uloom Academy</h1>
            <p className="text-gray-400 text-sm">Welcome back, {user?.first_name || user?.email}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 bg-blue-900 text-blue-300 rounded-full text-sm font-medium capitalize">
              {user?.role}
            </span>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Live Sessions Section */}
        <section className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-white">🔴 Live Sessions</h2>
            {user?.role === 'teacher' && (
              <button
                onClick={handleCreateSession}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                + Create Session
              </button>
            )}
          </div>

          {liveSessions.length === 0 ? (
            <div className="bg-slate-800 rounded-xl p-8 text-center border border-slate-700">
              <p className="text-gray-400">No active live sessions</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {liveSessions.map((session) => (
                <div
                  key={session.id}
                  className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-blue-500 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{session.title}</h3>
                      <p className="text-sm text-gray-400">{session.course_name}</p>
                    </div>
                    <span className="px-2 py-1 bg-red-900 text-red-300 rounded text-xs font-medium">
                      LIVE
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
                    <span>👥 {session.participant_count || 0} participants</span>
                    <span>⏰ Started {new Date(session.started_at).toLocaleTimeString()}</span>
                  </div>
                  <button
                    onClick={() => handleJoinClass(session.id)}
                    className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                  >
                    Join Class
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Courses Section */}
        <section>
          <h2 className="text-xl font-bold text-white mb-4">📚 My Courses</h2>

          {courses.length === 0 ? (
            <div className="bg-slate-800 rounded-xl p-8 text-center border border-slate-700">
              <p className="text-gray-400">No courses available</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {courses.map((course) => (
                <div
                  key={course.id}
                  className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-blue-500 transition-colors"
                >
                  <div className="mb-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      course.type === 'live' 
                        ? 'bg-green-900 text-green-300' 
                        : 'bg-purple-900 text-purple-300'
                    }`}>
                      {course.type === 'live' ? '🔴 Live Course' : '📹 Recorded'}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{course.title}</h3>
                  <p className="text-sm text-gray-400 mb-4 line-clamp-2">{course.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-400">
                    <span>{course.modules_count || 0} modules</span>
                    <span>{course.students_count || 0} students</span>
                  </div>
                  <button className="w-full mt-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-medium">
                    View Course
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
