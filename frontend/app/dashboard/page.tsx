"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  FileCheck2, 
  Layers, 
  Users, 
  Award, 
  AlertTriangle, 
  PlusCircle, 
  ArrowRight, 
  Clock, 
  CheckCircle2, 
  ExternalLink,
  UploadCloud,
  FileSpreadsheet,
  RefreshCw
} from "lucide-react";
import { api, getStoredUser } from "@/lib/api";
import ScoreDistributionChart from "@/components/ScoreDistributionChart";

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Top Welcome & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Evaluation Dashboard
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time batch recognition telemetry and candidate evaluation metrics
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadStats}
            className="p-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 text-xs font-semibold shadow-sm flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
          <Link
            href="/exams/new"
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 flex items-center gap-2 transition-all hover:scale-[1.02]"
          >
            <PlusCircle className="w-4 h-4" />
            Create New Exam
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
          <p className="text-sm text-slate-500">Loading evaluation statistics...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <div>{error}</div>
        </div>
      ) : stats ? (
        <div className="space-y-8">
          
          {/* KPI Metrics Cards (5 Cards) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            
            {/* 1. Total Exams */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Exams</span>
                <span className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
                  <Layers className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">
                {stats.total_exams}
              </div>
              <div className="mt-1 text-xs text-slate-500">Configured assessments</div>
            </div>

            {/* 2. Total Sheets Processed */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">OMR Scans</span>
                <span className="p-2 rounded-xl bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400">
                  <FileCheck2 className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">
                {stats.total_sheets_processed}
              </div>
              <div className="mt-1 text-xs text-slate-500">Total sheets recognized</div>
            </div>

            {/* 3. Students Evaluated */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Students</span>
                <span className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400">
                  <Users className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">
                {stats.total_students_evaluated}
              </div>
              <div className="mt-1 text-xs text-slate-500">Evaluated candidates</div>
            </div>

            {/* 4. Overall Class Average */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Class Average</span>
                <span className="p-2 rounded-xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400">
                  <Award className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white">
                {stats.overall_average_score}%
              </div>
              <div className="mt-1 text-xs text-slate-500">Overall score percentage</div>
            </div>

            {/* 5. Pending Reviews */}
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Pending Review</span>
                <span className="p-2 rounded-xl bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400">
                  <AlertTriangle className="w-4 h-4" />
                </span>
              </div>
              <div className="mt-3 text-3xl font-extrabold text-amber-600 dark:text-amber-400">
                {stats.pending_reviews_count}
              </div>
              <div className="mt-1 text-xs text-slate-500">Ambiguous / ID review flags</div>
            </div>

          </div>

          {/* Charts & Activity Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Score Distribution Chart (7 cols) */}
            <div className="lg:col-span-7 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Score Distribution Curve
                  </h3>
                  <p className="text-xs text-slate-500">
                    Candidate performance distribution across score percentage brackets
                  </p>
                </div>
              </div>
              <ScoreDistributionChart data={stats.score_distribution} />
            </div>

            {/* Recent Processing Activity Feed (5 cols) */}
            <div className="lg:col-span-5 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Recent Evaluation Activity
                  </h3>
                  <p className="text-xs text-slate-500">Latest recognized candidate submissions</p>
                </div>
              </div>

              <div className="flex-1 divide-y divide-slate-100 dark:divide-slate-800 overflow-y-auto max-h-[280px]">
                {stats.recent_activity.length === 0 ? (
                  <div className="py-12 text-center text-xs text-slate-400">
                    No recent evaluations recorded. Upload your first batch!
                  </div>
                ) : (
                  stats.recent_activity.map((act: any) => (
                    <div key={act.id} className="py-3 flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-[10px] ${
                          act.status === "automatically_evaluated" || act.status === "evaluated"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400"
                            : act.status === "awaiting_review"
                            ? "bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400"
                            : "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400"
                        }`}>
                          {act.score}
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900 dark:text-white">
                            {act.student_name}
                          </div>
                          <div className="text-[11px] text-slate-400 font-mono">
                            ID: {act.roll_number} • {act.file_name}
                          </div>
                        </div>
                      </div>

                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        act.status === "automatically_evaluated" || act.status === "evaluated"
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                          : act.status === "awaiting_review"
                          ? "bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300"
                          : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
                      }`}>
                        {act.status.replace(/_/g, " ")}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>

          {/* Active Exams Grid */}
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Recent Exams & Assessments
                </h3>
                <p className="text-xs text-slate-500">Manage answer keys, upload scans, and export final reports</p>
              </div>
              <Link
                href="/exams"
                className="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
              >
                View All Exams <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {stats.recent_exams.map((ex: any) => (
                <div 
                  key={ex.id}
                  className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 hover:bg-slate-50 dark:hover:bg-slate-850 hover:border-brand-300 dark:hover:border-brand-700 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-semibold text-brand-700 dark:text-brand-400 uppercase tracking-wider">
                        {ex.subject}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                        {ex.status}
                      </span>
                    </div>

                    <h4 className="text-base font-bold text-slate-900 dark:text-white leading-tight mb-1">
                      {ex.title}
                    </h4>
                    
                    <div className="text-xs text-slate-500 mb-4">
                      {ex.total_questions} Questions • Max {ex.max_marks} Marks
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs py-2 px-3 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 mb-4">
                      <div>
                        <span className="text-slate-400 text-[10px] uppercase font-bold block">Evaluated</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{ex.total_submissions} Students</span>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px] uppercase font-bold block">Average</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{ex.average_score} / {ex.max_marks}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action buttons */}
                  <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200 dark:border-slate-750">
                    <Link
                      href={`/exams/${ex.id}/upload`}
                      className="py-1.5 px-2 text-center rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 dark:bg-brand-950/60 dark:hover:bg-brand-900 dark:text-brand-300 text-[11px] font-semibold transition-colors flex items-center justify-center gap-1"
                    >
                      <UploadCloud className="w-3 h-3" /> Upload
                    </Link>
                    <Link
                      href={`/exams/${ex.id}/results`}
                      className="py-1.5 px-2 text-center rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 text-[11px] font-semibold transition-colors flex items-center justify-center gap-1"
                    >
                      <FileCheck2 className="w-3 h-3" /> Results
                    </Link>
                    <Link
                      href={`/exams/${ex.id}/answer-key`}
                      className="py-1.5 px-2 text-center rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 text-[11px] font-semibold transition-colors flex items-center justify-center gap-1"
                    >
                      Key
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      ) : null}

    </div>
  );
}
