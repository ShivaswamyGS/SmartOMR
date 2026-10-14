"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell
} from "recharts";

interface ScoreDistributionChartProps {
  data: Array<{ range: string; count: number }>;
}

const COLORS = ["#EF4444", "#F97316", "#F59E0B", "#3B82F6", "#10B981"];

export default function ScoreDistributionChart({ data }: ScoreDistributionChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        No evaluation data available yet
      </div>
    );
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
          <XAxis 
            dataKey="range" 
            tick={{ fontSize: 12, fill: "#64748B" }} 
            axisLine={{ stroke: "#CBD5E1" }}
            tickLine={false}
          />
          <YAxis 
            allowDecimals={false} 
            tick={{ fontSize: 12, fill: "#64748B" }} 
            axisLine={{ stroke: "#CBD5E1" }}
            tickLine={false}
          />
          <Tooltip 
            cursor={{ fill: "rgba(99, 102, 241, 0.05)" }}
            contentStyle={{ 
              backgroundColor: "#0F172A", 
              borderRadius: "8px", 
              border: "none", 
              color: "#F8FAFC",
              fontSize: "12px",
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.2)"
            }}
            formatter={(value: any) => [`${value} Students`, "Count"]}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
