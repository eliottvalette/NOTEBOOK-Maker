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
  const [notebookUrl, setNotebookUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setNotebookUrl(null)
    setError(null)
    const formData = new FormData()
    formData.append("dataset_style", choice)
    try {
      const res = await fetch("http://localhost:8000/generate-notebook/", {
        method: "POST",
        body: formData,
      })
      if (res.ok) {
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        setNotebookUrl(url)
      } else {
        setError("Erreur lors de la génération du notebook.")
      }
    } catch (err) {
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
      {notebookUrl && (
        <a
          href={notebookUrl}
          download="notebook.ipynb"
          className="mt-6 underline text-blue-600"
        >
          Télécharger le notebook généré
        </a>
      )}
      {error && <div className="mt-4 text-red-600">{error}</div>}
    </main>
  )
}
