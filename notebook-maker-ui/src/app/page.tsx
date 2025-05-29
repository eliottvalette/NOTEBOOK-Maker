"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectItem, SelectTrigger, SelectValue, SelectContent } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Download, BookOpen, CheckCircle, UploadCloud } from "lucide-react"
import React from "react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

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
  const [step, setStep] = useState(1)
  const [questionnaireCompleted, setQuestionnaireCompleted] = useState(false)

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
          console.error("Erreur lors du téléchargement du notebook exécuté.")
        }
      } else {
        console.error("Erreur lors de la génération du notebook.")
      }
    } catch (error) {
      console.log(error)
      console.error("Erreur de connexion au backend.")
    }
    setLoading(false)
  }

  const handleAnswersChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    let newVal: string | boolean = value
    if (type === "checkbox" && e.target instanceof HTMLInputElement) {
      newVal = e.target.checked
    }
    setAnswers(prev => ({ ...prev, [name]: type === "number" ? Number(newVal) : newVal }))
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-xs">
        <label className="block mb-2 font-semibold">Choose a dataset style:</label>
        <Select value={choice} onValueChange={setChoice}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Dataset style" />
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
          <label className="block mb-2 font-semibold">Upload your files:</label>
          <Input type="file" multiple onChange={handleFileChange} />
          {files.length > 0 && (
            <ul className="mt-2 text-xs text-gray-500">
              {files.map((file, idx) => (
                <li key={idx}>{file.name}</li>
              ))}
            </ul>
          )}
        </div>
        {files.length > 0 && !questionnaireCompleted && (
          <div className="space-y-4 border border-gray-600 rounded-xl p-4">
            <Tabs value={String(step)} onValueChange={val => setStep(Number(val))}>
              <TabsList className="w-full">
                <TabsTrigger value="1" className="w-full">1</TabsTrigger>
                <TabsTrigger value="2" className="w-full">2</TabsTrigger>
                <TabsTrigger value="3" className="w-full">3</TabsTrigger>
              </TabsList>
              <TabsContent value="1" className="space-y-2">
                <div>
                  <label className="block mb-1">Target column</label>
                  <Input name="target_column" value={answers.target_column} onChange={handleAnswersChange} className="w-full" />
                </div>
                <div>
                  <label className="block mb-1">Number of classes</label>
                  <Input name="num_classes" type="number" value={answers.num_classes} onChange={handleAnswersChange} className="w-full" />
                </div>
                <div className="flex justify-between">
                  <Button type="button" variant="outline" disabled>Previous</Button>
                  <Button type="button" onClick={() => setStep(2)}>Next</Button>
                </div>
              </TabsContent>
              <TabsContent value="2" className="space-y-2">
                <div>
                  <label className="block mb-1">Model type</label>
                  <Select value={answers.modelling_type} onValueChange={value => setAnswers(prev => ({ ...prev, modelling_type: value }))}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a model type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Neural network">Neural network</SelectItem>
                      <SelectItem value="XGBoost">XGBoost</SelectItem>
                      <SelectItem value="Random Forest">Random Forest</SelectItem>
                      <SelectItem value="LSTM">LSTM</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block mb-1">Target type</label>
                  <Select value={answers.Target_type} onValueChange={value => setAnswers(prev => ({ ...prev, Target_type: value }))}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a target type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Binary classification">Binary classification</SelectItem>
                      <SelectItem value="Multiclass classification">Multiclass classification</SelectItem>
                      <SelectItem value="Continuous">Continuous (regression)</SelectItem>
                      <SelectItem value="Time series forecasting">Time series forecasting</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-between">
                  <Button type="button" variant="outline" onClick={() => setStep(1)}>Previous</Button>
                  <Button type="button" onClick={() => setStep(3)}>Next</Button>
                </div>
              </TabsContent>
              <TabsContent value="3" className="space-y-2">
                <div className="flex items-center gap-2">
                  <Checkbox name="wants_pytorch" checked={answers.wants_pytorch} onCheckedChange={(checked) => setAnswers(prev => ({ ...prev, wants_pytorch: checked === true }))} />
                  <label>Use PyTorch</label>
                </div>
                <div>
                  <label className="block mb-1">Description (optional)</label>
                  <Textarea name="Natural_language" value={answers.Natural_language} onChange={handleAnswersChange} className="w-full p-2 rounded bg-input focus:bg-input" />
                </div>
                <div className="flex justify-between">
                  <Button type="button" variant="outline" onClick={() => setStep(2)}>Previous</Button>
                  <Button type="button" onClick={() => setQuestionnaireCompleted(true)}>Finish</Button>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}
        {questionnaireCompleted && (
          <Button type="submit" disabled={loading || files.length === 0} className="w-full mt-4 flex items-center gap-2">
            <UploadCloud className="mr-2" />
            {loading ? "Generating..." : "Generate notebook"}
          </Button>
        )}
      </form>
      {genNotebookUrl && (
        <div className="w-full max-w-5xl mx-auto mt-8">
          <Card className="w-full">
            <CardHeader className="flex flex-row items-center gap-3">
              <BookOpen className="text-blue-500" />
              <CardTitle>Generated Notebook</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              <Button asChild variant="outline" className="flex items-center gap-2">
                <a href={genNotebookUrl} download={`gen_${choice}.ipynb`}>
                  <Download className="mr-2" /> Download generated notebook
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
              <CardTitle>Executed Notebook</CardTitle>
            </CardHeader>
            <CardContent>
              <Button asChild variant="outline" className="flex items-center gap-2">
                <a href={exeNotebookUrl} download={`exe_${choice}.ipynb`}>
                  <Download className="mr-2" /> Download executed notebook
                </a>
              </Button>
              <Button
                type="button"
                variant="ghost"
                className="flex items-center gap-2 mt-2"
                onClick={() => setPreviewUrl(previewUrl ? null : `http://localhost:8000/preview-notebook/?dataset_style=${choice}&executed=true`)}
              >
                <BookOpen className="mr-2" />
                {previewUrl ? "Hide preview" : "Preview executed notebook"}
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
    </main>
  )
}
