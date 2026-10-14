"use client";

import React, { useState, useEffect } from "react";
import { 
  X, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  AlertTriangle, 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  Save, 
  RefreshCw,
  UserCheck,
  Eye,
  Layers,
  History
} from "lucide-react";
import { api, ResultDetail, resolveImageUrl } from "@/lib/api";

interface ManualReviewModalProps {
  resultId: number | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdated: () => void;
}

export default function ManualReviewModal({
  resultId,
  isOpen,
  onClose,
  onUpdated,
}: ManualReviewModalProps) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<ResultDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"annotated" | "original">("annotated");
  const [zoomLevel, setZoomLevel] = useState(1);
  const [editingIdentity, setEditingIdentity] = useState(false);
  const [studentNameInput, setStudentNameInput] = useState("");
  const [studentIdInput, setStudentIdInput] = useState("");

  useEffect(() => {
    if (isOpen && resultId) {
      loadDetail(resultId);
    } else {
      setData(null);
      setEditingIdentity(false);
    }
  }, [isOpen, resultId]);

  const loadDetail = async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getResult(id);
      setData(res);
      setStudentNameInput(res.student_name || "");
      setStudentIdInput(res.student_id || "");
    } catch (err: any) {
      setError(err.message || "Failed to load result details");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = async (questionNumber: number, newChoice: string) => {
    if (!data) return;
    try {
      setSaving(true);
      const valToSave = newChoice === "BLANK" ? null : newChoice;
      await api.correctAnswer(data.id, questionNumber, valToSave, "Teacher manual correction in modal");
      await loadDetail(data.id);
      onUpdated();
    } catch (err: any) {
      alert("Failed to update answer: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveIdentity = async () => {
    if (!data) return;
    try {
      setSaving(true);
      await api.correctIdentity(data.id, {
        student_name: studentNameInput,
        student_id: studentIdInput,
        roll_number: studentIdInput,
      });
      setEditingIdentity(false);
      await loadDetail(data.id);
      onUpdated();
    } catch (err: any) {
      alert("Failed to update student identity: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/70 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 w-full max-w-7xl h-[92vh] rounded-2xl shadow-2xl flex flex-col border border-slate-200 dark:border-slate-800 overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-850">
          <div className="flex items-center space-x-3">
            <span className="p-2 rounded-lg bg-brand-100 dark:bg-brand-900/50 text-brand-700 dark:text-brand-300">
              <UserCheck className="w-5 h-5" />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  Student Evaluation Audit & Review
                </h3>
                {data && (
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider ${
                    data.review_status === "approved" || data.review_status === "automatically_evaluated"
                      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300"
                      : data.review_status === "awaiting_review"
                      ? "bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-300"
                      : "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300"
                  }`}>
                    {data.review_status.replace(/_/g, " ")}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {data?.exam_title} • {data?.exam_subject}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body: Split 2-Column */}
        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center p-12">
            <RefreshCw className="w-8 h-8 animate-spin text-brand-600 mb-3" />
            <p className="text-sm text-slate-500">Loading student OMR scan and audit data...</p>
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center p-12 text-rose-600">
            {error}
          </div>
        ) : data ? (
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
            
            {/* Left Column: Interactive Zoomable OMR Scan (7 Cols) */}
            <div className="lg:col-span-7 border-r border-slate-200 dark:border-slate-800 flex flex-col bg-slate-100 dark:bg-slate-950">
              
              {/* Scan Toolbar */}
              <div className="px-4 py-2.5 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setViewMode("annotated")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                      viewMode === "annotated"
                        ? "bg-brand-600 text-white shadow-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                    }`}
                  >
                    <Layers className="w-3.5 h-3.5" />
                    AI Overlay (Annotated)
                  </button>
                  <button
                    onClick={() => setViewMode("original")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                      viewMode === "original"
                        ? "bg-brand-600 text-white shadow-sm"
                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
                    }`}
                  >
                    <Eye className="w-3.5 h-3.5" />
                    Original Scan
                  </button>
                </div>

                {/* Zoom Controls */}
                <div className="flex items-center space-x-1.5">
                  <button
                    onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.2))}
                    className="p-1.5 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                    title="Zoom Out"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  <span className="text-xs font-mono px-1.5 text-slate-500">
                    {Math.round(zoomLevel * 100)}%
                  </span>
                  <button
                    onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.2))}
                    className="p-1.5 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                    title="Zoom In"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setZoomLevel(1)}
                    className="p-1.5 rounded text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                    title="Reset Zoom"
                  >
                    <RotateCw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Image Viewport */}
              <div className="flex-1 overflow-auto p-4 flex items-center justify-center">
                <div 
                  className="transition-transform duration-200 origin-top shadow-xl border border-slate-300 dark:border-slate-700 bg-white"
                  style={{ transform: `scale(${zoomLevel})` }}
                >
                  <img
                    src={resolveImageUrl(viewMode === "annotated" ? data.annotated_image_url : data.original_image_url)}
                    alt="OMR Scan Preview"
                    className="max-w-[700px] h-auto object-contain block"
                  />
                </div>
              </div>

              {/* Legend footer */}
              <div className="px-4 py-2 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-center gap-6 text-[11px] text-slate-600 dark:text-slate-400">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-emerald-500 border border-emerald-600"></span>
                  Correct Answer
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-rose-500 border border-rose-600"></span>
                  Incorrect Marked
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-blue-500 border border-blue-600"></span>
                  Answer Key Target
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-amber-500 border border-amber-600"></span>
                  Ambiguous / Multi-mark
                </span>
              </div>
            </div>

            {/* Right Column: Student Details, Metrics & Questions (5 Cols) */}
            <div className="lg:col-span-5 flex flex-col bg-white dark:bg-slate-900 overflow-hidden">
              
              {/* Student Metadata Card */}
              <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-850/60">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Candidate Identification</span>
                  <button
                    onClick={() => setEditingIdentity(!editingIdentity)}
                    className="text-xs text-brand-600 dark:text-brand-400 hover:underline font-medium"
                  >
                    {editingIdentity ? "Cancel" : "Edit Identity"}
                  </button>
                </div>

                {editingIdentity ? (
                  <div className="space-y-2 mt-2">
                    <div>
                      <label className="text-xs text-slate-500">Student Name</label>
                      <input
                        type="text"
                        value={studentNameInput}
                        onChange={(e) => setStudentNameInput(e.target.value)}
                        className="w-full text-xs p-1.5 border rounded border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500">Student ID / Roll No</label>
                      <input
                        type="text"
                        value={studentIdInput}
                        onChange={(e) => setStudentIdInput(e.target.value)}
                        className="w-full text-xs p-1.5 border rounded border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"
                      />
                    </div>
                    <button
                      onClick={handleSaveIdentity}
                      disabled={saving}
                      className="px-3 py-1 bg-brand-600 text-white rounded text-xs font-semibold"
                    >
                      Save Identity
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-bold text-slate-900 dark:text-white text-base">
                        {data.student_name || "Unidentified Student"}
                      </div>
                      <div className="text-xs font-mono text-slate-500 dark:text-slate-400">
                        Roll No: {data.roll_number || data.student_id || "N/A"}
                      </div>
                    </div>
                    {data.rank && (
                      <div className="px-3 py-1 bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 rounded-xl text-center">
                        <div className="text-[10px] text-brand-600 dark:text-brand-400 font-bold uppercase">Class Rank</div>
                        <div className="text-lg font-extrabold text-brand-700 dark:text-brand-300">#{data.rank}</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Score Pill Bar */}
                <div className="grid grid-cols-4 gap-2 mt-4 pt-3 border-t border-slate-200 dark:border-slate-800">
                  <div className="bg-white dark:bg-slate-800 p-2 rounded-lg border border-slate-200 dark:border-slate-700 text-center">
                    <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Score</div>
                    <div className="text-base font-bold text-slate-900 dark:text-white">
                      {data.raw_score} <span className="text-xs font-normal text-slate-400">/ {data.max_marks}</span>
                    </div>
                  </div>
                  <div className="bg-emerald-50 dark:bg-emerald-950/30 p-2 rounded-lg border border-emerald-200 dark:border-emerald-800/40 text-center">
                    <div className="text-[10px] text-emerald-600 dark:text-emerald-400 uppercase font-semibold">Correct</div>
                    <div className="text-base font-bold text-emerald-700 dark:text-emerald-300">{data.correct_count}</div>
                  </div>
                  <div className="bg-rose-50 dark:bg-rose-950/30 p-2 rounded-lg border border-rose-200 dark:border-rose-800/40 text-center">
                    <div className="text-[10px] text-rose-600 dark:text-rose-400 uppercase font-semibold">Wrong</div>
                    <div className="text-base font-bold text-rose-700 dark:text-rose-300">{data.incorrect_count}</div>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 p-2 rounded-lg border border-slate-200 dark:border-slate-700 text-center">
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">Blank</div>
                    <div className="text-base font-bold text-slate-700 dark:text-slate-300">{data.unanswered_count}</div>
                  </div>
                </div>
              </div>

              {/* Questions Comparative List Header */}
              <div className="px-4 py-2 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-850 text-xs font-bold text-slate-600 dark:text-slate-300">
                <span className="w-12">Q.No</span>
                <span className="w-20 text-center">Key</span>
                <span className="w-24 text-center">Detected</span>
                <span className="flex-1 text-center">Status</span>
                <span className="w-24 text-right">Override</span>
              </div>

              {/* Scrollable Questions List */}
              <div className="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                {data.question_breakdown.map((q) => {
                  return (
                    <div 
                      key={q.question_number}
                      className={`px-4 py-2.5 flex items-center justify-between text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40 ${
                        q.is_multi_mark || q.is_ambiguous ? "bg-amber-50/50 dark:bg-amber-950/20" : ""
                      }`}
                    >
                      <div className="w-12 font-mono font-bold text-slate-800 dark:text-slate-200">
                        #{q.question_number}
                      </div>

                      <div className="w-20 text-center">
                        <span className="inline-block px-2 py-0.5 rounded font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200">
                          {q.correct_answer || "-"}
                        </span>
                      </div>

                      <div className="w-24 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded font-mono font-bold ${
                          q.status === "correct" 
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300"
                            : q.status === "incorrect"
                            ? "bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-300"
                            : "bg-slate-100 text-slate-500 dark:bg-slate-800"
                        }`}>
                          {q.is_multi_mark ? "MULTI" : q.detected_answer || "BLANK"}
                        </span>
                      </div>

                      <div className="flex-1 flex items-center justify-center">
                        {q.status === "correct" ? (
                          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                            <CheckCircle2 className="w-4 h-4" /> Correct
                          </span>
                        ) : q.is_multi_mark ? (
                          <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400 font-medium" title="Multiple answers marked">
                            <AlertTriangle className="w-4 h-4" /> Multi
                          </span>
                        ) : q.status === "incorrect" ? (
                          <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400 font-medium">
                            <XCircle className="w-4 h-4" /> Incorrect
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-slate-400 font-medium">
                            <HelpCircle className="w-4 h-4" /> Blank
                          </span>
                        )}
                      </div>

                      {/* Manual Override dropdown */}
                      <div className="w-24 text-right">
                        <select
                          value={q.detected_answer || "BLANK"}
                          disabled={saving}
                          onChange={(e) => handleAnswerChange(q.question_number, e.target.value)}
                          className="text-xs py-1 px-1.5 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 font-mono font-semibold"
                        >
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                          <option value="E">E</option>
                          <option value="BLANK">Blank</option>
                        </select>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Audit history drawer snippet */}
              {data.corrections_history && data.corrections_history.length > 0 && (
                <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 text-xs">
                  <div className="font-bold text-slate-600 dark:text-slate-400 flex items-center gap-1.5 mb-1">
                    <History className="w-3.5 h-3.5" />
                    Teacher Override Audit Log ({data.corrections_history.length})
                  </div>
                  <div className="text-[11px] text-slate-500 max-h-16 overflow-y-auto">
                    {data.corrections_history.map((c) => (
                      <div key={c.id}>
                        • Q{c.question_number}: {c.old_answer || 'BLANK'} → {c.new_answer || 'BLANK'} by {c.corrected_by}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        ) : null}

      </div>
    </div>
  );
}
