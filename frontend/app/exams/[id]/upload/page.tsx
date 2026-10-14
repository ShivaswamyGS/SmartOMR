"use client";

import React, { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  UploadCloud, 
  FileUp, 
  FileCheck2, 
  ArrowLeft, 
  File, 
  Trash2, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  Sparkles, 
  Layers, 
  Archive,
  ArrowRight,
  Users
} from "lucide-react";
import { api, Exam, getStoredUser } from "@/lib/api";

export default function OMRUploadPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const rosterInputRef = useRef<HTMLInputElement>(null);

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [rosterFile, setRosterFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [batchId, setBatchId] = useState<number | null>(null);
  const [batchStatus, setBatchStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [generatingDemo, setGeneratingDemo] = useState(false);

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

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArr = Array.from(e.dataTransfer.files);
      addValidFiles(filesArr);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArr = Array.from(e.target.files);
      addValidFiles(filesArr);
    }
  };

  const addValidFiles = (files: File[]) => {
    const valid = files.filter((f) => {
      const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase();
      return [".png", ".jpg", ".jpeg", ".pdf", ".zip"].includes(ext);
    });
    setSelectedFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUploadAndEvaluate = async () => {
    if (selectedFiles.length === 0) {
      setError("Please select at least one OMR image, PDF, or ZIP archive.");
      return;
    }
    if (!exam?.has_answer_key) {
      setError("This exam does not have an Answer Key configured yet. Please configure it first.");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setProgress(10);

      // 1. Upload roster if attached
      if (rosterFile) {
        await api.uploadRoster(examId, rosterFile);
      }

      // 2. Upload OMR sheets
      setProgress(30);
      const res = await api.uploadOMRSheets(examId, selectedFiles);
      setBatchId(res.batch_id);
      setProgress(50);

      // 3. Poll batch status until completed
      pollBatchStatus(res.batch_id);
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setUploading(false);
    }
  };

  const pollBatchStatus = async (bId: number) => {
    const interval = setInterval(async () => {
      try {
        const status = await api.getBatchStatus(bId);
        setBatchStatus(status);
        setProgress(Math.max(50, Math.min(95, status.progress_percentage)));

        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          setUploading(false);
          setProgress(100);
          setSuccessMsg(`Successfully processed ${status.processed_files} sheets!`);
        }
      } catch {
        clearInterval(interval);
        setUploading(false);
      }
    }, 1200);
  };

  const handleGenerateSyntheticDemo = async () => {
    if (!exam?.has_answer_key) {
      setError("Please configure the Answer Key first before generating sample sheets.");
      return;
    }

    try {
      setGeneratingDemo(true);
      setError(null);
      await api.generateDemoSamples(examId, 5);
      setSuccessMsg("Successfully generated 5 realistic filled candidate sheets and scored them!");
      setTimeout(() => {
        router.push(`/exams/${examId}/results`);
      }, 1500);
    } catch (err: any) {
      setError(err.message || "Demo generation failed");
    } finally {
      setGeneratingDemo(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
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
            Bulk OMR Sheet Upload & Recognition
          </h1>
          {exam && (
            <p className="text-xs text-slate-500 mt-1">
              {exam.title} • {exam.subject} ({exam.total_questions} Questions)
            </p>
          )}
        </div>

        {/* 1-Click Demo Generator Pill */}
        <button
          onClick={handleGenerateSyntheticDemo}
          disabled={generatingDemo || uploading}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white text-xs font-bold shadow-md shadow-orange-500/20 flex items-center gap-2 transition-all hover:scale-[1.02] disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {generatingDemo ? "Generating 5 Test Sheets..." : "⚡ 1-Click Generate Demo Sheets"}
        </button>
      </div>

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
            href={`/exams/${examId}/results`}
            className="font-bold underline text-emerald-700 hover:text-emerald-900 flex items-center gap-1"
          >
            View Evaluation Results <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Answer Key Warning if missing */}
      {exam && !exam.has_answer_key && (
        <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              <b>Answer Key Required:</b> You must set up the correct answer key before evaluating sheets.
            </span>
          </div>
          <Link
            href={`/exams/${examId}/answer-key`}
            className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold"
          >
            Configure Answer Key →
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload Zone (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Drag & Drop Card */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="p-10 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand-500 dark:hover:border-brand-500 bg-white dark:bg-slate-900 text-center cursor-pointer transition-all hover:bg-brand-50/20 group"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              multiple
              accept=".png,.jpg,.jpeg,.pdf,.zip"
              className="hidden"
            />
            <div className="w-16 h-16 rounded-2xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 mx-auto flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Drag & Drop OMR Sheets or Archives Here
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
              Supports individual scans (PNG, JPG, JPEG), PDF exam packets, or a single ZIP archive containing hundreds of sheets.
            </p>
            <button
              type="button"
              className="mt-4 px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 rounded-xl text-xs font-semibold"
            >
              Browse Files from Computer
            </button>
          </div>

          {/* Selected Files List */}
          {selectedFiles.length > 0 && (
            <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-3">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  Ready for Evaluation ({selectedFiles.length} files)
                </span>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="text-xs text-rose-600 hover:underline"
                >
                  Clear all
                </button>
              </div>

              <div className="max-h-48 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="py-2 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2 truncate pr-2">
                      {file.name.endsWith(".zip") ? (
                        <Archive className="w-4 h-4 text-amber-500 shrink-0" />
                      ) : (
                        <File className="w-4 h-4 text-brand-500 shrink-0" />
                      )}
                      <span className="truncate text-slate-800 dark:text-slate-200">{file.name}</span>
                      <span className="text-[10px] text-slate-400">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="text-slate-400 hover:text-rose-600 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Progress Bar when uploading */}
          {uploading && (
            <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-brand-200 dark:border-brand-900 shadow-md">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-brand-700 dark:text-brand-300 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  {batchStatus ? `Evaluating batch: ${batchStatus.processed_files} / ${batchStatus.total_files} sheets...` : "Uploading & initializing CV pipeline..."}
                </span>
                <span className="text-xs font-mono font-bold text-brand-600">{progress}%</span>
              </div>
              <div className="w-full bg-slate-100 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-brand-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Evaluate Action Button */}
          <button
            onClick={handleUploadAndEvaluate}
            disabled={uploading || selectedFiles.length === 0}
            className="w-full py-3.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-bold shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            <FileCheck2 className="w-5 h-5" />
            {uploading ? "Evaluating Sheets..." : `Start Bulk Evaluation (${selectedFiles.length} Files)`}
          </button>
        </div>

        {/* Sidebar Info & Roster Upload (1 Col) */}
        <div className="space-y-6">
          
          {/* Optional Roster Card */}
          <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="w-4 h-4 text-brand-600" />
              <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Student Roster Mapping (Optional)
              </h4>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Upload a CSV or Excel sheet with columns: <code>Student ID, Student Name, Roll Number</code>. When sheets are evaluated, candidate names will automatically populate!
            </p>

            <input
              type="file"
              ref={rosterInputRef}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setRosterFile(e.target.files[0]);
                }
              }}
              accept=".csv,.xlsx"
              className="hidden"
            />

            {rosterFile ? (
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-between text-xs">
                <span className="truncate font-semibold text-slate-800 dark:text-slate-200">{rosterFile.name}</span>
                <button onClick={() => setRosterFile(null)} className="text-rose-500">
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => rosterInputRef.current?.click()}
                className="w-full py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-center justify-center gap-1.5"
              >
                <FileUp className="w-3.5 h-3.5" /> Attach Student Roster
              </button>
            )}
          </div>

          {/* How Recognition Works Info Card */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800 text-xs space-y-3">
            <h4 className="font-bold text-slate-900 dark:text-white">
              Recognition Standards
            </h4>
            <div className="space-y-2 text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
              <p>• <b>4-Point Registration:</b> Solid black square markers in 4 corners auto-align perspective skew.</p>
              <p>• <b>Adaptive Illumination:</b> Shadows and gradient lighting are normalized automatically.</p>
              <p>• <b>Roll Number Grid:</b> Reads 6-digit bubbled IDs 0 through 9.</p>
              <p>• <b>Duplicate Guard:</b> SHA-256 hash checks prevent duplicate submissions.</p>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
