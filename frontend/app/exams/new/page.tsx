"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Layers, 
  CheckCircle2, 
  AlertCircle, 
  Sliders, 
  FileCheck2, 
  Sparkles,
  HelpCircle
} from "lucide-react";
import { api, getStoredUser } from "@/lib/api";

export default function NewExamPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [code, setCode] = useState("");
  const [totalQuestions, setTotalQuestions] = useState(50);
  const [marksPerCorrect, setMarksPerCorrect] = useState(1.0);
  const [negativeMarks, setNegativeMarks] = useState(0.25);
  const [maxMarks, setMaxMarks] = useState(50.0);
  const [templateId, setTemplateId] = useState<number | undefined>(undefined);
  const [templates, setTemplates] = useState<any[]>([]);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await api.listTemplates();
      setTemplates(data);
      if (data && data.length > 0) {
        setTemplateId(data[0].id);
      }
    } catch {
      // Ignore
    }
  };

  // Auto-calculate max marks when total questions or marks per correct changes
  useEffect(() => {
    setMaxMarks(Number((totalQuestions * marksPerCorrect).toFixed(2)));
  }, [totalQuestions, marksPerCorrect]);

  const handlePresetQuestions = (qCount: number) => {
    setTotalQuestions(qCount);
    // Auto select matching template if available
    const matched = templates.find((t) => t.total_questions === qCount);
    if (matched) {
      setTemplateId(matched.id);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !subject.trim()) {
      setError("Please fill in Exam Title and Subject.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const newExam = await api.createExam({
        title,
        subject,
        code: code.trim() || undefined,
        total_questions: totalQuestions,
        marks_per_correct: marksPerCorrect,
        negative_marks_per_incorrect: negativeMarks,
        max_marks: maxMarks,
        template_id: templateId,
      });

      // Redirect immediately to Answer Key setup
      router.push(`/exams/${newExam.id}/answer-key?firstTime=true`);
    } catch (err: any) {
      setError(err.message || "Failed to create exam");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Back button */}
      <Link
        href="/exams"
        className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Exams
      </Link>

      <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        
        {/* Header */}
        <div className="p-8 border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850/60">
          <div className="flex items-center space-x-3 mb-2">
            <span className="p-2.5 rounded-xl bg-brand-600 text-white shadow-md shadow-brand-500/20">
              <FileCheck2 className="w-5 h-5" />
            </span>
            <div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white">
                Create New Assessment
              </h1>
              <p className="text-xs text-slate-500">
                Step 1 of 2: Define exam details, scoring rules, and sheet layout
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="m-8 mb-0 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          
          {/* General Information */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs border-b border-slate-100 dark:border-slate-800 pb-2">
              General Information
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Exam Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CSE Midterm Examination 2026"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Subject / Course <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Data Structures & Algorithms"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Exam Code / Reference
                </label>
                <input
                  type="text"
                  placeholder="e.g. CS-301"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  OMR Sheet Template
                </label>
                <select
                  value={templateId || ""}
                  onChange={(e) => setTemplateId(Number(e.target.value))}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-brand-500 focus:outline-none"
                >
                  {templates.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({t.total_questions} Questions)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Question Configuration */}
          <div className="space-y-4 pt-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs border-b border-slate-100 dark:border-slate-800 pb-2">
              Question Count & Scoring Rules
            </h3>

            {/* Quick Presets */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                Quick Question Presets:
              </label>
              <div className="flex items-center gap-3">
                {[20, 50, 100].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => handlePresetQuestions(preset)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
                      totalQuestions === preset
                        ? "bg-brand-600 text-white border-brand-600 shadow-md shadow-brand-500/20"
                        : "bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100"
                    }`}
                  >
                    {preset} Questions
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Total Questions
                </label>
                <input
                  type="number"
                  min="1"
                  max="200"
                  required
                  value={totalQuestions}
                  onChange={(e) => setTotalQuestions(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Marks per Correct
                </label>
                <input
                  type="number"
                  step="0.25"
                  min="0.1"
                  required
                  value={marksPerCorrect}
                  onChange={(e) => setMarksPerCorrect(Math.max(0.1, parseFloat(e.target.value) || 1.0))}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Negative Mark (Incorrect)
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  required
                  value={negativeMarks}
                  onChange={(e) => setNegativeMarks(Math.max(0, parseFloat(e.target.value) || 0))}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Maximum Marks
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="1"
                  required
                  value={maxMarks}
                  onChange={(e) => setMaxMarks(parseFloat(e.target.value) || 1.0)}
                  className="w-full text-xs p-2.5 border rounded-xl border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono font-bold"
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400">
              <span className="font-bold text-slate-800 dark:text-slate-200 block mb-1">
                Standard Scoring Formula:
              </span>
              <code>Score = (Correct × {marksPerCorrect}) − (Incorrect × {negativeMarks})</code>
              <p className="mt-1 text-[11px] text-slate-400">
                * Note: Unanswered / blank questions do not receive negative penalties unless configured.
              </p>
            </div>
          </div>

          {/* Form Actions */}
          <div className="pt-6 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <Link
              href="/exams"
              className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900"
            >
              Cancel
            </Link>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
            >
              {loading ? "Creating Exam..." : "Save & Configure Answer Key →"}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
