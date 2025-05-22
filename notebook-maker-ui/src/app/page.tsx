"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectItem, SelectTrigger, SelectValue, SelectContent } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Download, BookOpen, CheckCircle, UploadCloud } from "lucide-react"
import React from "react"

const DATASET_CHOICES = [
  { value: "A_1_one_csv", label: "A_1_one_csv" },
  { value: "B_2_joinable_csvs", label: "B_2_joinable_csvs" },
  { value: "C_1_csv_time_series", label: "C_1_csv_time_series" },
]

const DEFAULT_ANSWERS = {
  target_column: "",
  num_classes: 2,
  modelling_type: "Neural network",
  Target_type: "Binary classification",
  wants_pytorch: true,
  Natural_language: ""
}

export default function Home() {
  const [choice, setChoice] = useState(DATASET_CHOICES[0].value)
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)
  const [genNotebookUrl, setGenNotebookUrl] = useState<string | null>(null)
  const [exeNotebookUrl, setExeNotebookUrl] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [answers, setAnswers] = useState(DEFAULT_ANSWERS)
  const [jsonPreview, setJsonPreview] = useState<string>(JSON.stringify(DEFAULT_ANSWERS, null, 2))
  const [loadingAnswers, setLoadingAnswers] = useState(false)
  const [genNotebookUrlAnswers, setGenNotebookUrlAnswers] = useState<string | null>(null)
  const [errorAnswers, setErrorAnswers] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setGenNotebookUrl(null)
    setExeNotebookUrl(null)
    const formData = new FormData()
    formData.append("dataset_style", choice)
    files.forEach(file => formData.append("files", file))
    try {
      const res = await fetch("http://localhost:8000/generate-notebook/", {
        method: "POST",
        body: formData,
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        setGenNotebookUrl(url)
        // Exécuté
        const exeRes = await fetch(`http://localhost:8000/download-executed-notebook/?dataset_style=${choice}`)
        if (exeRes.ok) {
          const exeBlob = await exeRes.blob()
          const exeUrl = window.URL.createObjectURL(exeBlob)
          setExeNotebookUrl(exeUrl)
        } else {
          setErrorAnswers("Erreur lors du téléchargement du notebook exécuté.")
        }
      } else {
        setErrorAnswers("Erreur lors de la génération du notebook.")
      }
    } catch (error) {
      console.log(error)
      setErrorAnswers("Erreur de connexion au backend.")
    }
    setLoading(false)
  }

  const handleAnswersChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    let newVal: string | boolean = value
    if (type === "checkbox" && e.target instanceof HTMLInputElement) {
      newVal = e.target.checked
    }
    setAnswers(prev => {
      const updated = { ...prev, [name]: type === "number" ? Number(newVal) : newVal }
      setJsonPreview(JSON.stringify(updated, null, 2))
      return updated
    })
  }

  const handleSubmitAnswers = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoadingAnswers(true)
    setGenNotebookUrlAnswers(null)
    setErrorAnswers(null)
    const formData = new FormData()
    formData.append("dataset_style", choice)
    files.forEach(file => formData.append("files", file))
    formData.append("answers", JSON.stringify(answers))
    try {
      const res = await fetch("http://localhost:8000/submit-answers/", {
        method: "POST",
        body: formData,
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        setGenNotebookUrlAnswers(url)
      } else {
        setErrorAnswers("Erreur lors de la génération du notebook (answers).")
      }
    } catch (error) {
      console.log(error)
      setErrorAnswers("Erreur de connexion au backend (answers).")
    }
    setLoadingAnswers(false)
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-xs">
        <label className="block mb-2 font-semibold">Choisissez un style de dataset :</label>
        <Select value={choice} onValueChange={setChoice}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Theme" />
          </SelectTrigger>
          <SelectContent>
            {DATASET_CHOICES.map(opt => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div>
          <label className="block mb-2 font-semibold">Import your files :</label>
          <Input type="file" multiple onChange={handleFileChange} />
          {files.length > 0 && (
            <ul className="mt-2 text-xs text-gray-500">
              {files.map((file, idx) => (
                <li key={idx}>{file.name}</li>
              ))}
            </ul>
          )}
        </div>
        <Button type="submit" disabled={loading || files.length === 0} className="w-full mt-4 flex items-center gap-2">
          <UploadCloud className="mr-2" />
          {loading ? "Génération en cours..." : "Générer le notebook"}
        </Button>
      </form>
      {genNotebookUrl && (
        <div className="w-full max-w-5xl mx-auto mt-8">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center gap-3">
              <BookOpen className="text-blue-500" />
              <CardTitle>Notebook généré</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              <Button asChild variant="outline" className="flex items-center gap-2">
                <a href={genNotebookUrl} download={`gen_${choice}.ipynb`}>
                  <Download className="mr-2" /> Télécharger le notebook généré
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
      {exeNotebookUrl && (
        <div className="w-full max-w-5xl mx-auto mt-4">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center gap-3">
              <CheckCircle className="text-green-500" />
              <CardTitle>Notebook exécuté</CardTitle>
            </CardHeader>
            <CardContent>
              <Button asChild variant="outline" className="flex items-center gap-2">
                <a href={exeNotebookUrl} download={`exe_${choice}.ipynb`}>
                  <Download className="mr-2" /> Télécharger le notebook exécuté
                </a>
              </Button>
              <Button
                type="button"
                variant="ghost"
                className="flex items-center gap-2 mt-2"
                onClick={() => setPreviewUrl(previewUrl ? null : `http://localhost:8000/preview-notebook/?dataset_style=${choice}&executed=true`)}
              >
                <BookOpen className="mr-2" />
                {previewUrl ? "Masquer la prévisualisation" : "Prévisualiser le notebook exécuté"}
              </Button>
              {previewUrl && (
                <div className="mt-4 w-full h-[400px] border rounded overflow-hidden">
                  <iframe src={previewUrl} className="w-full h-full" />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
      {/* Nouveau formulaire pour answers JSON */}
      <form onSubmit={handleSubmitAnswers} className="space-y-4 w-full max-w-xs mt-10 p-4 border rounded bg-gray-900">
        <h2 className="font-bold text-lg mb-2">Formulaire avancé (answers JSON)</h2>
        <div>
          <label className="block mb-1">Target column</label>
          <Input name="target_column" value={answers.target_column} onChange={handleAnswersChange} />
        </div>
        <div>
          <label className="block mb-1">Nombre de classes</label>
          <Input name="num_classes" type="number" value={answers.num_classes} onChange={handleAnswersChange} />
        </div>
        <div>
          <label className="block mb-1">Type de modèle</label>
          <select name="modelling_type" value={answers.modelling_type} onChange={handleAnswersChange} className="w-full p-2 rounded bg-gray-800">
            <option value="Neural network">Neural network</option>
            <option value="XGBoost">XGBoost</option>
            <option value="Random Forest">Random Forest</option>
            <option value="LSTM">LSTM</option>
            <option value="Autre">Autre</option>
          </select>
        </div>
        <div>
          <label className="block mb-1">Type de cible</label>
          <select name="Target_type" value={answers.Target_type} onChange={handleAnswersChange} className="w-full p-2 rounded bg-gray-800">
            <option value="Binary classification">Binaire</option>
            <option value="Multiclass classification">Multiclasse</option>
            <option value="Continuous">Continue (régression)</option>
            <option value="Time series forecasting">Série temporelle</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <input type="checkbox" name="wants_pytorch" checked={answers.wants_pytorch} onChange={handleAnswersChange} />
          <label>Utiliser PyTorch</label>
        </div>
        <div>
          <label className="block mb-1">Description (optionnel)</label>
          <textarea name="Natural_language" value={answers.Natural_language} onChange={handleAnswersChange} className="w-full p-2 rounded bg-gray-800" />
        </div>
        <Button type="submit" disabled={loadingAnswers || files.length === 0} className="w-full mt-2 flex items-center gap-2">
          {loadingAnswers ? "Envoi en cours..." : "Envoyer answers + fichiers"}
        </Button>
        <div className="mt-2">
          <label className="block font-semibold mb-1">Prévisualisation du JSON answers :</label>
          <pre className="bg-gray-800 text-xs p-2 rounded overflow-x-auto max-h-40">{jsonPreview}</pre>
        </div>
        {genNotebookUrlAnswers && (
          <Button asChild variant="outline" className="flex items-center gap-2 mt-2">
            <a href={genNotebookUrlAnswers} download={`gen_${choice}_answers.ipynb`}>
              <Download className="mr-2" /> Télécharger le notebook généré (answers)
            </a>
          </Button>
        )}
        {errorAnswers && <div className="mt-2 text-red-600">{errorAnswers}</div>}
      </form>
    </main>
  )
}
