"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectItem, SelectTrigger, SelectValue, SelectContent } from "@/components/ui/select"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Download, BookOpen, CheckCircle } from "lucide-react"

const DATASET_CHOICES = [
  { value: "A_1_one_csv", label: "A_1_one_csv" },
  { value: "B_2_joinable_csvs", label: "B_2_joinable_csvs" },
  { value: "C_1_csv_time_series", label: "C_1_csv_time_series" },
]

export default function Home() {
  const [choice, setChoice] = useState(DATASET_CHOICES[0].value)
  const [loading, setLoading] = useState(false)
  const [genNotebookUrl, setGenNotebookUrl] = useState<string | null>(null)
  const [exeNotebookUrl, setExeNotebookUrl] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setGenNotebookUrl(null)
    setExeNotebookUrl(null)
    setError(null)
    const formData = new FormData()
    formData.append("dataset_style", choice)
    try {
      // Généré
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
          setError("Erreur lors du téléchargement du notebook exécuté.")
        }
      } else {
        setError("Erreur lors de la génération du notebook.")
      }
    } catch (error) {
      console.log(error)
      setError("Erreur de connexion au backend.")
    }
    setLoading(false)
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
        <Button type="submit" disabled={loading} className="w-full mt-4">
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
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </main>
  )
}
