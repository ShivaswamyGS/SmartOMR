"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  UploadCloud, 
  FileCheck2, 
  Sliders, 
  FileSpreadsheet, 
  FileText, 
  Printer, 
  Users, 
  Award, 
  CheckCircle2, 
  AlertCircle,
  RefreshCw,
  Sparkles
} from "lucide-react";
import { api, Exam, getStoredUser } from "@/lib/api";

export default function ExamDetailPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadExam();
  }, [examId]);

  const loadExam = async () => {
    try {
      setLoading(true);
      const ex = await api.getExam(examId);
      setExam(ex);
    } catch (err: any) {
      setError(err.message || "Failed to load exam details");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: "xlsx" | "csv" | "pdf") => {
    const url = api.getExportUrl(examId, format);
    window.open(url, "_blank");
  };

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
        <p className="text-sm text-slate-500">Loading assessment overview...</p>
      </div>
    );
  }

  if (!exam) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Back button */}
      <Link
        href="/exams"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 mb-4 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        Back to Exams
      </Link>

      {/* Main Header Banner */}
      <div className="p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-bold text-brand-600 dark:text-brand-400 uppercase tracking-wider">
              {exam.subject}
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 capitalize">
              {exam.status}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            {exam.title}
          </h1>

          {exam.code && (
            <p className="text-xs font-mono text-slate-400 mt-1">
              Assessment Code: {exam.code}
            </p>
          )}
        </div>

        {/* Quick Links */}
        <div className="flex flex-wrap items-center gap-3">
          <Link
            href={`/exams/${exam.id}/upload`}
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 flex items-center gap-2 transition-all hover:scale-[1.02]"
          >
            <UploadCloud className="w-4 h-4" />
            Upload Scans
          </Link>

          <Link
            href={`/exams/${exam.id}/results`}
            className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-800 dark:text-slate-200 text-xs font-semibold flex items-center gap-2 transition-colors"
          >
            <FileCheck2 className="w-4 h-4 text-emerald-600" />
            View Results
          </Link>

          <Link
            href={`/exams/${exam.id}/answer-key`}
            className="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-800 dark:text-slate-200 text-xs font-semibold flex items-center gap-2 transition-colors"
          >
            <Sliders className="w-4 h-4 text-brand-600" />
            Answer Key
          </Link>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-bold block">Total Questions</span>
          <span className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1 block">
            {exam.total_questions}
          </span>
          <span className="text-xs text-slate-500">Max {exam.max_marks} marks</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-bold block">Marking Scheme</span>
          <span className="text-2xl font-extrabold text-slate-900 dark:text-white mt-1 block">
            +{exam.marks_per_correct} / -{exam.negative_marks_per_incorrect}
          </span>
          <span className="text-xs text-slate-500">Correct / Wrong penalty</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-bold block">Evaluated Candidates</span>
          <span className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 block">
            {exam.total_submissions}
          </span>
          <span className="text-xs text-slate-500">Submissions graded</span>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-bold block">Class Average</span>
          <span className="text-2xl font-extrabold text-brand-600 dark:text-brand-400 mt-1 block">
            {exam.average_score}
          </span>
          <span className="text-xs text-slate-500">Out of {exam.max_marks} marks</span>
        </div>
      </div>

      {/* Export Reports Box */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">
          Export Official Assessment Reports
        </h3>
        <p className="text-xs text-slate-500 mb-6">
          Generate formatted spreadsheets with question-level item analysis or printable PDF scorecards
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => handleExport("xlsx")}
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors"
          >
            <FileSpreadsheet className="w-4 h-4" /> Download Excel Report (.xlsx)
          </button>

          <button
            onClick={() => handleExport("csv")}
            className="px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors"
          >
            <FileText className="w-4 h-4" /> Download CSV Export
          </button>

          <button
            onClick={() => handleExport("pdf")}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors"
          >
            <Printer className="w-4 h-4" /> Generate Class PDF Summary
          </button>
        </div>
      </div>

    </div>
  );
}
