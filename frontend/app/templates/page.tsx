"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Download, 
  Layers, 
  Printer, 
  FileCheck2, 
  CheckCircle2, 
  Sliders, 
  Eye, 
  RefreshCw,
  ExternalLink
} from "lucide-react";
import { api } from "@/lib/api";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTemplate, setSelectedTemplate] = useState<any | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const data = await api.listTemplates();
      setTemplates(data);
      if (data && data.length > 0) {
        setSelectedTemplate(data[0]);
      }
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadBlank = (tplId: number) => {
    const url = api.getBlankTemplateUrl(tplId);
    window.open(url, "_blank");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            OMR Sheet Templates & Printable Sheets
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Standard high-precision bubble layouts with 4-corner fiducials and roll number matrices
          </p>
        </div>

        {selectedTemplate && (
          <button
            onClick={() => handleDownloadBlank(selectedTemplate.id)}
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-md shadow-brand-500/20 flex items-center gap-2 transition-all hover:scale-[1.02]"
          >
            <Printer className="w-4 h-4" />
            Download Blank Printable Sheet (PNG)
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Templates Selector List (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Available Sheet Designs
          </h3>

          {loading ? (
            <div className="py-12 flex justify-center">
              <RefreshCw className="w-6 h-6 animate-spin text-brand-600" />
            </div>
          ) : (
            templates.map((tpl) => {
              const isSelected = selectedTemplate?.id === tpl.id;
              return (
                <div
                  key={tpl.id}
                  onClick={() => setSelectedTemplate(tpl)}
                  className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-white dark:bg-slate-900 border-brand-500 shadow-md ring-2 ring-brand-500/20"
                      : "bg-slate-50/50 dark:bg-slate-850/50 border-slate-200 dark:border-slate-800 hover:bg-white dark:hover:bg-slate-900"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-brand-600 dark:text-brand-400">
                      {tpl.total_questions} Questions
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600">
                      {tpl.columns_count} Columns
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-slate-900 dark:text-white mb-1">
                    {tpl.name}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
                    {tpl.description}
                  </p>

                  <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
                    <span className="text-slate-400 text-[11px]">Options: A, B, C, D</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownloadBlank(tpl.id);
                      }}
                      className="text-brand-600 dark:text-brand-400 hover:underline font-semibold flex items-center gap-1"
                    >
                      <Download className="w-3.5 h-3.5" /> Download
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Template Detail & Technical Specifications (8 Cols) */}
        <div className="lg:col-span-8">
          {selectedTemplate ? (
            <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                    {selectedTemplate.name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Canonical Resolution: 1600 × 2200 pixels • Standard A4 Proportion
                  </p>
                </div>

                <button
                  onClick={() => handleDownloadBlank(selectedTemplate.id)}
                  className="px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-sm flex items-center gap-1.5 self-start sm:self-auto"
                >
                  <Download className="w-4 h-4" /> Download Blank Template
                </button>
              </div>

              {/* Specs Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Total MCQs</span>
                  <span className="text-lg font-bold text-slate-900 dark:text-white">{selectedTemplate.total_questions} Questions</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Options per MCQ</span>
                  <span className="text-lg font-bold text-slate-900 dark:text-white">A, B, C, D (4)</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Roll Number Matrix</span>
                  <span className="text-lg font-bold text-slate-900 dark:text-white">6 Digits (0-9)</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-850 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Fiducial Markers</span>
                  <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">4 Corners (60px)</span>
                </div>
              </div>

              {/* Template Architecture Explanation */}
              <div className="space-y-4 pt-4">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Layout Architecture & Registration
                </h4>

                <div className="space-y-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
                    <span className="font-bold text-slate-900 dark:text-white block mb-1">
                      1. Homography Corner Fiducials
                    </span>
                    The template embeds 60×60 solid black square markers at coordinates (80,80), (1520,80), (1520,2120), and (80,2120). The OpenCV preprocessor uses these markers to de-skew photos taken with smartphones or angled flatbed scans.
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
                    <span className="font-bold text-slate-900 dark:text-white block mb-1">
                      2. Numeric Roll Number Grid
                    </span>
                    Candidates fill their 6-digit student roll number into a 6-column matrix with rows 0 through 9. Each digit is independently extracted using inner circular masks and cross-referenced with your class roster.
                  </div>

                  <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850">
                    <span className="font-bold text-slate-900 dark:text-white block mb-1">
                      3. Two-Column Question Layout
                    </span>
                    Questions 1 to 25 are arranged in Column 1 (X: 160px), and Questions 26 to 50 are in Column 2 (X: 880px). Bubble centers have 68px horizontal spacing and 54px vertical row gap with 15px radius.
                  </div>
                </div>
              </div>

            </div>
          ) : null}
        </div>

      </div>

    </div>
  );
}
