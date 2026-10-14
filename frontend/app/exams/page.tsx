"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  PlusCircle, 
  Search, 
  Layers, 
  FileCheck2, 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  RefreshCw,
  Sliders,
  ChevronRight,
  BookOpen
} from "lucide-react";
import { api, Exam, getStoredUser } from "@/lib/api";

export default function ExamsIndexPage() {
  const router = useRouter();
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listExams();
      setExams(data);
    } catch (err: any) {
      setError(err.message || "Failed to load exams list");
    } finally {
      setLoading(false);
    }
  };

  const filteredExams = exams.filter(
    (e) =>
      e.title.toLowerCase().includes(search.toLowerCase()) ||
      e.subject.toLowerCase().includes(search.toLowerCase()) ||
      (e.code && e.code.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Exams & Assessments
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage your multiple-choice tests, configure answer keys, and evaluate submissions
          </p>
        </div>

        <Link
          href="/exams/new"
          className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 flex items-center gap-2 transition-all hover:scale-[1.02] self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          Create New Exam
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by title, subject, or code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <button
          onClick={loadExams}
          className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 text-xs font-medium flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Exams Grid */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
          <p className="text-sm text-slate-500">Loading exams...</p>
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700">
          {error}
        </div>
      ) : filteredExams.length === 0 ? (
        <div className="py-20 text-center rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-8">
          <BookOpen className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No exams found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            {search ? "No exams matched your search query." : "Get started by creating your first multiple-choice exam assessment."}
          </p>
          <Link
            href="/exams/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600 text-white text-xs font-semibold shadow"
          >
            <PlusCircle className="w-4 h-4" />
            Create Exam
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredExams.map((exam) => (
            <div
              key={exam.id}
              className="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:shadow-md hover:border-brand-300 dark:hover:border-brand-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-brand-700 dark:text-brand-400 uppercase tracking-wider">
                    {exam.subject}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 capitalize">
                    {exam.status}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-slate-900 dark:text-white leading-tight mb-1">
                  {exam.title}
                </h3>
                
                {exam.code && (
                  <div className="text-xs font-mono text-slate-400 mb-3">
                    Code: {exam.code}
                  </div>
                )}

                {/* Badges Info */}
                <div className="grid grid-cols-3 gap-2 p-3 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 my-4 text-center">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Questions</span>
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{exam.total_questions}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Max Marks</span>
                    <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{exam.max_marks}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">Negative</span>
                    <span className="text-sm font-bold text-rose-600 dark:text-rose-400">-{exam.negative_marks_per_incorrect}</span>
                  </div>
                </div>

                {/* Submissions & Answer Key Status */}
                <div className="space-y-1.5 mb-6 text-xs text-slate-600 dark:text-slate-400">
                  <div className="flex items-center justify-between">
                    <span>Evaluated Candidates:</span>
                    <span className="font-bold text-slate-900 dark:text-white">{exam.total_submissions}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Answer Key:</span>
                    <span className={`font-semibold ${exam.has_answer_key ? "text-emerald-600" : "text-amber-600"}`}>
                      {exam.has_answer_key ? "✓ Configured" : "⚠️ Key Missing"}
                    </span>
                  </div>
                  {exam.total_submissions > 0 && (
                    <div className="flex items-center justify-between">
                      <span>Class Average:</span>
                      <span className="font-bold text-brand-600 dark:text-brand-400">{exam.average_score} / {exam.max_marks}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons Grid */}
              <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
                <Link
                  href={`/exams/${exam.id}/upload`}
                  className="py-2 px-2 text-center rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 dark:bg-brand-950/60 dark:hover:bg-brand-900 dark:text-brand-300 text-xs font-semibold transition-colors flex items-center justify-center gap-1"
                >
                  <UploadCloud className="w-3.5 h-3.5" /> Upload
                </Link>
                <Link
                  href={`/exams/${exam.id}/results`}
                  className="py-2 px-2 text-center rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 text-xs font-semibold transition-colors flex items-center justify-center gap-1"
                >
                  <FileCheck2 className="w-3.5 h-3.5" /> Results
                </Link>
                <Link
                  href={`/exams/${exam.id}/answer-key`}
                  className="py-2 px-2 text-center rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 text-xs font-semibold transition-colors flex items-center justify-center gap-1"
                >
                  <Sliders className="w-3.5 h-3.5" /> Key
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
