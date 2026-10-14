"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, 
  Save, 
  Sparkles, 
  Trash2, 
  FileUp, 
  CheckCircle2, 
  AlertCircle, 
  Sliders, 
  UploadCloud,
  FileCheck2,
  RefreshCw
} from "lucide-react";
import { api, Exam, getStoredUser } from "@/lib/api";

function AnswerKeyContent() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const isFirstTime = searchParams.get("firstTime") === "true";
  const examId = params.id as string;

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [optionsCount, setOptionsCount] = useState(4); // 4 for A-D, 5 for A-E

  const optionsList = ["A", "B", "C", "D", "E"].slice(0, optionsCount);

  useEffect(() => {
    const user = getStoredUser();
    if (!user) {
      router.push("/login");
      return;
    }
    loadData();
  }, [examId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const ex = await api.getExam(examId);
      setExam(ex);

      // Try loading existing answer key
      try {
        const keyData = await api.getAnswerKey(examId);
        if (keyData && keyData.answers) {
          setAnswers(keyData.answers);
        }
      } catch {
        // If no key exists yet, initialize blank
        const initAnswers: Record<string, string> = {};
        for (let i = 1; i <= ex.total_questions; i++) {
          initAnswers[i.toString()] = "";
        }
        setAnswers(initAnswers);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load exam details");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (qNum: number, opt: string) => {
    setAnswers((prev) => ({
      ...prev,
      [qNum.toString()]: prev[qNum.toString()] === opt ? "" : opt,
    }));
  };

  const handleQuickPatternFill = () => {
    if (!exam) return;
    const pattern = ["A", "B", "C", "D"];
    const filled: Record<string, string> = {};
    for (let i = 1; i <= exam.total_questions; i++) {
      filled[i.toString()] = pattern[(i * 3 + 1) % pattern.length];
    }
    setAnswers(filled);
  };

  const handleQuickRandomFill = () => {
    if (!exam) return;
    const filled: Record<string, string> = {};
    for (let i = 1; i <= exam.total_questions; i++) {
      filled[i.toString()] = optionsList[Math.floor(Math.random() * optionsList.length)];
    }
    setAnswers(filled);
  };

  const handleClearAll = () => {
    if (!exam) return;
    const cleared: Record<string, string> = {};
    for (let i = 1; i <= exam.total_questions; i++) {
      cleared[i.toString()] = "";
    }
    setAnswers(cleared);
  };

  const handleSave = async () => {
    if (!exam) return;
    
    // Validate missing answers
    const missing: number[] = [];
    for (let i = 1; i <= exam.total_questions; i++) {
      if (!answers[i.toString()]) {
        missing.push(i);
      }
    }

    if (missing.length > 0) {
      const confirmSave = confirm(
        `Warning: Questions ${missing.slice(0, 5).join(", ")}${
          missing.length > 5 ? "..." : ""
        } have no correct answer assigned. Are you sure you want to save?`
      );
      if (!confirmSave) return;
    }

    setSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      await api.saveAnswerKey(exam.id, {
        total_questions: exam.total_questions,
        answers,
      });
      setSuccessMsg("Answer key saved successfully!");
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || "Failed to save answer key");
    } finally {
      setSaving(false);
    }
  };

  const filledCount = Object.values(answers).filter(Boolean).length;
  const totalCount = exam?.total_questions || 50;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Top Breadcrumb & Actions */}
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
            Answer Key Configurator
            {exam && (
              <span className="text-sm font-normal text-slate-500">
                — {exam.title} ({exam.subject})
              </span>
            )}
          </h1>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href={`/exams/${examId}/upload`}
            className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <UploadCloud className="w-3.5 h-3.5" />
            OMR Upload Hub
          </Link>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-brand-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? "Saving..." : "Save Answer Key"}
          </button>
        </div>
      </div>

      {isFirstTime && (
        <div className="mb-6 p-4 rounded-xl bg-brand-50 dark:bg-brand-950/50 border border-brand-200 dark:border-brand-800 text-xs text-brand-800 dark:text-brand-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-600 shrink-0" />
            <span>
              <b>Exam created!</b> Now configure the correct answers below. You can select bubbles individually, apply a pattern fill, or randomize for instant testing.
            </span>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <Link
            href={`/exams/${examId}/upload`}
            className="font-bold underline text-emerald-700 hover:text-emerald-900"
          >
            Proceed to Upload OMR Sheets →
          </Link>
        </div>
      )}

      {/* Control Toolbar */}
      <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="text-xs font-bold text-slate-700 dark:text-slate-300">
            Assigned:{" "}
            <span className={filledCount === totalCount ? "text-emerald-600 font-extrabold" : "text-brand-600 font-extrabold"}>
              {filledCount}
            </span>{" "}
            / {totalCount} Questions
          </div>

          <div className="flex items-center space-x-1.5 pl-4 border-l border-slate-200 dark:border-slate-800 text-xs">
            <span className="text-slate-500">Options:</span>
            <button
              onClick={() => setOptionsCount(4)}
              className={`px-2 py-1 rounded text-xs font-bold ${
                optionsCount === 4 ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
              }`}
            >
              A-D
            </button>
            <button
              onClick={() => setOptionsCount(5)}
              className={`px-2 py-1 rounded text-xs font-bold ${
                optionsCount === 5 ? "bg-brand-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
              }`}
            >
              A-E
            </button>
          </div>
        </div>

        {/* Quick Action Tools */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleQuickPatternFill}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-center gap-1"
          >
            <Sliders className="w-3 h-3 text-brand-600" />
            Pattern Fill (A-B-C-D)
          </button>

          <button
            onClick={handleQuickRandomFill}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3 text-amber-500" />
            Random Fill
          </button>

          <button
            onClick={handleClearAll}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors flex items-center gap-1"
          >
            <Trash2 className="w-3 h-3" />
            Clear
          </button>
        </div>
      </div>

      {/* Visual Answer Grid */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
          <p className="text-sm text-slate-500">Loading answer grid...</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {Array.from({ length: totalCount }, (_, i) => i + 1).map((qNum) => {
              const qKey = qNum.toString();
              const currentChoice = answers[qKey] || "";

              return (
                <div
                  key={qNum}
                  className={`p-2.5 rounded-xl border transition-all ${
                    currentChoice
                      ? "bg-slate-50/80 dark:bg-slate-850 border-brand-200 dark:border-brand-900/60"
                      : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-slate-800 dark:text-slate-200">
                      Q{qNum < 10 ? `0${qNum}` : qNum}
                    </span>
                    {currentChoice ? (
                      <span className="text-[10px] font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/80 px-1.5 py-0.5 rounded">
                        {currentChoice}
                      </span>
                    ) : (
                      <span className="text-[9px] text-amber-500 font-semibold">Unset</span>
                    )}
                  </div>

                  {/* Bubbles */}
                  <div className="flex items-center justify-between gap-1">
                    {optionsList.map((opt) => {
                      const isSelected = currentChoice === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => handleSelectOption(qNum, opt)}
                          className={`w-7 h-7 rounded-full text-xs font-bold font-mono transition-all flex items-center justify-center ${
                            isSelected
                              ? "bg-brand-600 text-white shadow-md shadow-brand-500/30 scale-105"
                              : "bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-brand-400 hover:bg-brand-50/50"
                          }`}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Sticky Bottom Save Action */}
          <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Changes must be saved before uploading student OMR sheets.
            </span>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md shadow-brand-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              {saving ? "Saving..." : "Save Answer Key"}
            </button>
          </div>

        </div>
      )}

    </div>
  );
}

export default function AnswerKeyEditorPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-xs text-slate-500">Loading answer key grid...</div>}>
      <AnswerKeyContent />
    </Suspense>
  );
}
