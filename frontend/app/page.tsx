"use client";

import React from "react";
import Link from "next/link";
import { 
  FileCheck2, 
  UploadCloud, 
  Sparkles, 
  BarChart3, 
  FileSpreadsheet, 
  ShieldCheck, 
  ArrowRight, 
  CheckCircle, 
  Layers, 
  FileText,
  Sliders,
  Users
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 bg-gradient-to-b from-brand-50/50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-950 dark:to-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-brand-100 dark:bg-brand-950/80 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800 mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            Next-Gen Computer Vision OMR Evaluation
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-950 dark:text-white max-w-4xl mx-auto leading-[1.15]">
            Evaluate Hundreds of <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-700 via-brand-600 to-indigo-500 dark:from-brand-400 dark:to-indigo-300">
              OMR Sheets in Minutes
            </span>
          </h1>

          {/* Description */}
          <p className="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Eliminate manual grading errors. SmartOMR automatically detects marked answers, resolves student identities, calculates scores with negative marking, and generates instant reports.
          </p>

          {/* Call to Actions */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold text-base shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
            >
              Get Started Free
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-semibold text-base hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center justify-center gap-2 transition-all shadow-sm"
            >
              Explore Live Dashboard
            </Link>
          </div>

          {/* Social Proof / Stats */}
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto pt-8 border-t border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">99.8%</div>
              <div className="text-xs uppercase font-medium mt-1">Bubble Detection Rate</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">&lt;0.2s</div>
              <div className="text-xs uppercase font-medium mt-1">Per Sheet Processing</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">ZIP & PDF</div>
              <div className="text-xs uppercase font-medium mt-1">Bulk Upload Formats</div>
            </div>
            <div>
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">1-Click</div>
              <div className="text-xs uppercase font-medium mt-1">Excel & PDF Export</div>
            </div>
          </div>
        </div>

        {/* Dashboard Preview Graphic */}
        <div className="mt-14 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-2 sm:p-4 shadow-2xl overflow-hidden ring-1 ring-slate-900/5">
            <div className="rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-slate-950 p-6 text-white font-sans">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                  <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                  <span className="text-xs font-mono text-slate-400 ml-2">SmartOMR Evaluation Hub — CSE Internal Assessment (50 Questions)</span>
                </div>
                <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 text-xs font-semibold border border-emerald-500/30">
                  Batch Evaluation Complete (100%)
                </span>
              </div>

              {/* Mock Dashboard Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400">Total Evaluated</div>
                  <div className="text-2xl font-bold mt-1 text-white">48 Sheets</div>
                </div>
                <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400">Class Average Score</div>
                  <div className="text-2xl font-bold mt-1 text-brand-400">42.4 / 50</div>
                </div>
                <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400">Top Candidate Score</div>
                  <div className="text-2xl font-bold mt-1 text-emerald-400">49.0 (98%)</div>
                </div>
                <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
                  <div className="text-xs text-slate-400">Ambiguity Flags</div>
                  <div className="text-2xl font-bold mt-1 text-amber-400">1 Review Req</div>
                </div>
              </div>

              {/* Table snippet */}
              <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden text-xs">
                <div className="grid grid-cols-6 p-3 bg-slate-850 font-semibold text-slate-400 border-b border-slate-800">
                  <span>Rank</span>
                  <span>Student ID</span>
                  <span>Candidate Name</span>
                  <span>Score (Max 50)</span>
                  <span>Accuracy</span>
                  <span>AI Verification</span>
                </div>
                <div className="divide-y divide-slate-800/60 font-mono">
                  <div className="grid grid-cols-6 p-3 items-center">
                    <span className="text-amber-400 font-bold">#1</span>
                    <span>10101</span>
                    <span className="font-sans font-medium text-white">Alex Johnson</span>
                    <span className="text-emerald-400 font-bold">47.50</span>
                    <span>96.0%</span>
                    <span className="text-emerald-400 font-sans font-semibold">✓ Verified (0.98)</span>
                  </div>
                  <div className="grid grid-cols-6 p-3 items-center">
                    <span className="text-slate-300 font-bold">#2</span>
                    <span>10102</span>
                    <span className="font-sans font-medium text-white">Sophia Martinez</span>
                    <span className="text-emerald-400 font-bold">43.75</span>
                    <span>91.5%</span>
                    <span className="text-emerald-400 font-sans font-semibold">✓ Verified (0.97)</span>
                  </div>
                  <div className="grid grid-cols-6 p-3 items-center">
                    <span className="text-slate-300 font-bold">#3</span>
                    <span>10103</span>
                    <span className="font-sans font-medium text-white">Liam Chen</span>
                    <span className="text-brand-400 font-bold">39.25</span>
                    <span>84.0%</span>
                    <span className="text-emerald-400 font-sans font-semibold">✓ Verified (0.95)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="py-20 bg-white dark:bg-slate-900 border-y border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs uppercase font-bold tracking-widest text-brand-600 dark:text-brand-400 mb-2">
              Engineered For Accuracy
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
              Everything Teachers & Institutions Need
            </h3>
            <p className="mt-3 text-slate-600 dark:text-slate-400 text-base">
              From mobile phone camera snapshots to high-speed scanner PDFs, SmartOMR handles perspective skew, uneven lighting, and faint marks with ease.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Feature 1 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-brand-600 text-white flex items-center justify-center mb-6 shadow-md shadow-brand-500/20">
                <UploadCloud className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Bulk Multi-Format Upload
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Drag and drop single or multiple PNG, JPG, or PDF files. Upload an entire batch in a single ZIP file for seamless evaluation of hundreds of candidates at once.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center mb-6 shadow-md shadow-indigo-500/20">
                <Layers className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Computer Vision Alignment
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Uses 4-corner fiducial marker recognition and homography warping to correct rotation, skew, perspective distortions, and contrast imperfections automatically.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-emerald-600 text-white flex items-center justify-center mb-6 shadow-md shadow-emerald-500/20">
                <Users className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Automated Student Identification
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Reads bubbled roll number grids and barcode identifiers. Cross-references with your uploaded student roster to prevent misattribution.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-amber-600 text-white flex items-center justify-center mb-6 shadow-md shadow-amber-500/20">
                <Sliders className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Scoring Rules & Negative Marking
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Configure custom marks per correct answer, negative marking for incorrect choices, and specific question weightings. Negative marking is never applied to blanks.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-rose-600 text-white flex items-center justify-center mb-6 shadow-md shadow-rose-500/20">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Audit Trail & Manual Review
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Flag uncertain scans or multiple-marked answers for teacher review. Zoom into high-res scans, override answers with live recalculation, and maintain audit logs.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 rounded-xl bg-violet-600 text-white flex items-center justify-center mb-6 shadow-md shadow-violet-500/20">
                <FileSpreadsheet className="w-6 h-6" />
              </div>
              <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                Excel, CSV & PDF Exports
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                Export class rank lists, question-wise item analyses, and summary statistics to styled Excel spreadsheets, CSV data, or printable PDF scorecards.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* How It Works (4-Step Workflow) */}
      <section className="py-20 bg-slate-50 dark:bg-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs uppercase font-bold tracking-widest text-brand-600 dark:text-brand-400 mb-2">
              Simple 4-Step Process
            </h2>
            <h3 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
              How SmartOMR Works
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
            
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900/60 text-brand-700 dark:text-brand-300 font-bold flex items-center justify-center text-sm mb-4">
                01
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">Create Exam</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Set question count, marks per question, and negative marking penalty. Configure the answer key via interactive grid or CSV.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900/60 text-brand-700 dark:text-brand-300 font-bold flex items-center justify-center text-sm mb-4">
                02
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">Upload OMR Sheets</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Upload scans, camera photos, or a single ZIP archive. Optionally attach an Excel roster to map student roll numbers to names.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900/60 text-brand-700 dark:text-brand-300 font-bold flex items-center justify-center text-sm mb-4">
                03
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">Automated Evaluation</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Computer vision engine normalizes contrast, extracts bubble fills, detects ambiguous choices, and calculates student scores instantly.
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm relative">
              <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900/60 text-brand-700 dark:text-brand-300 font-bold flex items-center justify-center text-sm mb-4">
                04
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">Review & Export</h4>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Inspect uncertain scans side-by-side, approve corrections, and download official Excel grade sheets or PDF scorecards with 1 click.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-xs uppercase font-bold tracking-widest text-brand-600 dark:text-brand-400 mb-2">
              Common Inquiries
            </h2>
            <h3 className="text-3xl font-extrabold text-slate-900 dark:text-white">
              Frequently Asked Questions
            </h3>
          </div>

          <div className="space-y-6">
            <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                Can SmartOMR evaluate sheets photographed with a smartphone?
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Yes. Our computer vision pipeline detects corner registration fiducials and applies perspective homography to warp and straighten mobile photos, correcting rotation and lighting variations automatically.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                What happens if a student marks two bubbles for the same question?
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                SmartOMR calculates fill ratios across all options. If two options exceed the threshold, it flags the question as &quot;Multiple Marked&quot;, applies configured incorrect penalties, and highlights the question for teacher manual audit.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
              <h4 className="text-base font-bold text-slate-900 dark:text-white mb-2">
                How does student identification work?
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Students bubble their roll number in a designated numeric grid. SmartOMR decodes the bubbles and matches the ID against your uploaded roster to automatically fetch the candidate&apos;s name and class.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-500 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <FileCheck2 className="w-4 h-4 text-brand-600" />
            <span className="font-bold text-slate-900 dark:text-white">SmartOMR</span>
            <span>— AI-Powered OMR Sheet Evaluation System</span>
          </div>
          <div>
            Built for universities, schools, and competitive exam administrators.
          </div>
        </div>
      </footer>

    </div>
  );
}
