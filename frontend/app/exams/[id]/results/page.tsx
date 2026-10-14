"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Search, 
  Download, 
  FileSpreadsheet, 
  FileText, 
  Printer, 
  UploadCloud, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  UserCheck, 
  SlidersHorizontal,
  ChevronDown,
  ArrowUpDown,
  FileCheck2,
  HelpCircle,
  XCircle,
  Award
} from "lucide-react";
import { api, Exam, EvaluationItem, getStoredUser } from "@/lib/api";
import ManualReviewModal from "@/components/ManualReviewModal";

export default function ExamResultsPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;

  const [exam, setExam] = useState<Exam | null>(null);
  const [results, setResults] = useState<EvaluationItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("rank");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);

  // Review modal state
  const [selectedResultId, setSelectedResultId] = useState<number | null>(null);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadData();
  }, [examId, search, statusFilter, sortBy, sortDir, page]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [ex, res] = await Promise.all([
        api.getExam(examId),
        api.listResults(examId, {
          search,
          status: statusFilter,
          sort_by: sortBy,
          sort_dir: sortDir,
          page,
          limit: 50,
        }),
      ]);
      setExam(ex);
      setResults(res.items || []);
      setTotal(res.total || 0);
    } catch (err: any) {
      setError(err.message || "Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: "xlsx" | "csv" | "pdf") => {
    const url = api.getExportUrl(examId, format);
    window.open(url, "_blank");
  };

  const handleOpenReview = (resultId: number) => {
    setSelectedResultId(resultId);
    setReviewModalOpen(true);
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortDir("asc");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <Link
            href={`/exams`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Exams
          </Link>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            Evaluation Results & Rank List
            {exam && (
              <span className="text-sm font-normal text-slate-500">
                — {exam.title} ({exam.subject})
              </span>
            )}
          </h1>
        </div>

        {/* Export Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <Link
            href={`/exams/${examId}/upload`}
            className="px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 text-xs font-semibold flex items-center gap-1.5 shadow-sm"
          >
            <UploadCloud className="w-3.5 h-3.5 text-brand-600" /> Upload More
          </Link>

          <button
            onClick={() => handleExport("xlsx")}
            className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Excel (.xlsx)
          </button>

          <button
            onClick={() => handleExport("csv")}
            className="px-3 py-2 rounded-xl bg-slate-700 hover:bg-slate-800 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <FileText className="w-3.5 h-3.5" /> CSV
          </button>

          <button
            onClick={() => handleExport("pdf")}
            className="px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
          >
            <Printer className="w-3.5 h-3.5" /> Summary PDF
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search candidate name or student ID..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center space-x-1 text-xs w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          {[
            { id: "all", label: "All Results" },
            { id: "automatically_evaluated", label: "Auto Verified" },
            { id: "evaluated_with_warnings", label: "Warnings" },
            { id: "awaiting_review", label: "Review Required" },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => { setStatusFilter(f.id); setPage(1); }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-colors whitespace-nowrap ${
                statusFilter === f.id
                  ? "bg-brand-600 text-white"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
              }`}
            >
              {f.label}
            </button>
          ))}

          <button
            onClick={loadData}
            className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50"
            title="Refresh results"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Results Table */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
          <p className="text-sm text-slate-500">Loading student evaluations...</p>
        </div>
      ) : results.length === 0 ? (
        <div className="py-20 text-center rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800 p-8">
          <FileCheck2 className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No evaluation results found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Upload student OMR sheets or generate demo sheets to see real-time scores.
          </p>
          <Link
            href={`/exams/${examId}/upload`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-600 text-white text-xs font-semibold shadow"
          >
            <UploadCloud className="w-4 h-4" />
            Upload OMR Sheets
          </Link>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
          
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-850 text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th onClick={() => handleSort("rank")} className="py-3 px-4 cursor-pointer hover:text-slate-900">
                    <span className="flex items-center gap-1">Rank <ArrowUpDown className="w-3 h-3" /></span>
                  </th>
                  <th onClick={() => handleSort("id")} className="py-3 px-4 cursor-pointer hover:text-slate-900">
                    <span className="flex items-center gap-1">Student ID <ArrowUpDown className="w-3 h-3" /></span>
                  </th>
                  <th onClick={() => handleSort("name")} className="py-3 px-4 cursor-pointer hover:text-slate-900">
                    <span className="flex items-center gap-1">Candidate Name <ArrowUpDown className="w-3 h-3" /></span>
                  </th>
                  <th onClick={() => handleSort("score")} className="py-3 px-4 cursor-pointer hover:text-slate-900 text-right">
                    <span className="flex items-center justify-end gap-1">Score <ArrowUpDown className="w-3 h-3" /></span>
                  </th>
                  <th className="py-3 px-4 text-right">Percentage</th>
                  <th className="py-3 px-4 text-center">Correct</th>
                  <th className="py-3 px-4 text-center">Wrong</th>
                  <th className="py-3 px-4 text-center">Blank</th>
                  <th className="py-3 px-4 text-center">AI Status</th>
                  <th className="py-3 px-4 text-center">Audit Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {results.map((r) => {
                  return (
                    <tr 
                      key={r.id}
                      className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="py-3 px-4 font-bold font-mono text-slate-800 dark:text-slate-200">
                        {r.rank ? (
                          <span className={r.rank === 1 ? "text-amber-500 font-extrabold" : ""}>
                            #{r.rank}
                          </span>
                        ) : "-"}
                      </td>

                      <td className="py-3 px-4 font-mono font-semibold text-slate-700 dark:text-slate-300">
                        {r.roll_number || r.student_id || "N/A"}
                      </td>

                      <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">
                        {r.student_name || "Unidentified Student"}
                      </td>

                      <td className="py-3 px-4 font-extrabold text-sm text-right font-mono text-brand-600 dark:text-brand-400">
                        {r.raw_score} <span className="text-[10px] font-normal text-slate-400">/ {exam?.max_marks}</span>
                      </td>

                      <td className="py-3 px-4 font-mono text-right font-bold text-slate-800 dark:text-slate-200">
                        {r.percentage}%
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span className="inline-block px-2 py-0.5 rounded font-mono font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300">
                          {r.correct_count}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded font-mono font-bold ${
                          r.incorrect_count > 0 
                            ? "bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300" 
                            : "text-slate-400"
                        }`}>
                          {r.incorrect_count}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span className="inline-block px-2 py-0.5 rounded font-mono text-slate-500">
                          {r.unanswered_count}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          r.review_status === "approved" || r.review_status === "automatically_evaluated"
                            ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800"
                            : r.review_status === "awaiting_review"
                            ? "bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400 border border-rose-200 dark:border-rose-800"
                            : "bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400 border border-amber-200 dark:border-amber-800"
                        }`}>
                          {r.review_status.replace(/_/g, " ")}
                        </span>
                      </td>

                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => handleOpenReview(r.id)}
                          className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-brand-50 text-slate-700 hover:text-brand-700 dark:bg-slate-800 dark:hover:bg-brand-950/60 dark:text-slate-300 text-xs font-semibold transition-colors flex items-center justify-center gap-1 mx-auto"
                        >
                          <UserCheck className="w-3.5 h-3.5" />
                          Review Scan
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Footer info */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 flex items-center justify-between text-xs text-slate-500">
            <span>Showing {results.length} of {total} evaluated candidates</span>
            <span>Sorted by: {sortBy.toUpperCase()} ({sortDir.toUpperCase()})</span>
          </div>

        </div>
      )}

      {/* Student Audit Modal */}
      <ManualReviewModal
        resultId={selectedResultId}
        isOpen={reviewModalOpen}
        onClose={() => setReviewModalOpen(false)}
        onUpdated={loadData}
      />

    </div>
  );
}
