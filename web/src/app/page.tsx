"use client";
import React, { useState } from "react";

export default function Home() {
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setResult("Running pipeline...");
    const form = e.currentTarget;
    const formData = new FormData(form);

    try {
      const response = await fetch("http://localhost:8000/run-pipeline", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setResult(
            `Pipeline complete! <br/><a href="${data.gen_notebook_url}" download>Download Non executed notebook</a><br/><a href="${data.exe_notebook_url}" download>Download Executed notebook</a>`
          );
        } else {
          setResult("Pipeline failed: " + data.error);
        }
      } else {
        setResult("Server error.");
      }
    } catch {
      setResult("Network error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-[#f5f6fa] font-sans flex items-center justify-center">
      <main className="max-w-md w-full mx-auto text-left p-4 sm:p-8">
        <div className="inline-block bg-[#23233a] text-[#7d8cff] rounded-full px-4 py-1 text-base mb-6 tracking-wide">Notebook Innovation</div>
        <h1 className="text-4xl font-bold mb-1 tracking-tight">
          <span className="text-[#4f7cff]">Notebook</span> Maker
        </h1>
        <p className="text-[#b0b3c6] text-lg mb-8">Generate smart notebooks from your data</p>
        <form id="uploadForm" className="bg-[#181824] rounded-2xl p-6 shadow-lg flex flex-col gap-5 mb-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="dataset" className="block text-[#b0b3c6] mb-1">Upload Dataset</label>
            <input type="file" id="dataset" name="dataset" required className="bg-[#23233a] text-white rounded-lg p-2 w-full" />
          </div>
          <div>
            <label htmlFor="style" className="block text-[#b0b3c6] mb-1">Dataset Style</label>
            <select id="style" name="style" className="bg-[#23233a] text-white rounded-lg p-2 w-full">
              <option value="A_1_one_csv">A_1_one_csv</option>
              <option value="B_2_joinable_csvs">B_2_joinable_csvs</option>
              <option value="C_1_csv_time_series">C_1_csv_time_series</option>
            </select>
          </div>
          <div className="flex gap-4 mt-2">
            <button type="submit" className="px-6 py-2 rounded-xl font-semibold bg-[#4f7cff] text-white hover:bg-[#7d8cff] hover:text-[#23233a] transition" disabled={loading}>
              {loading ? "Running..." : "Run Pipeline"}
            </button>
          </div>
        </form>
        <div id="result" className="mt-6 text-[#7dffb0] text-lg min-h-[2em]" dangerouslySetInnerHTML={{ __html: result }} />
      </main>
    </div>
  );
}
