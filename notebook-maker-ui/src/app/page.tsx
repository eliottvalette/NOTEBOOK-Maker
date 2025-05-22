"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectItem, SelectTrigger, SelectContent } from "@/components/ui/select"

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
          <SelectTrigger className="w-full" />
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
        <a
          href={genNotebookUrl}
          download={`gen_${choice}.ipynb`}
          className="mt-6 underline text-blue-600"
        >
          Télécharger le notebook généré
        </a>
      )}
      {exeNotebookUrl && (
        <a
          href={exeNotebookUrl}
          download={`exe_${choice}.ipynb`}
          className="mt-2 underline text-green-600"
        >
          Télécharger le notebook exécuté
        </a>
      )}
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </main>
  )
}
