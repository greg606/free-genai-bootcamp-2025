import { DataTable } from "./data-table"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"
import Link from "next/link"

interface Word {
  id: number
  german: string
  romaji: string
  english: string
  correctCount: number
  wrongCount: number
}

const dummyData: Word[] = [
  { id: 1, german: "Hallo", romaji: "Hallo", english: "Hello", correctCount: 10, wrongCount: 2 },
  { id: 2, german: "Auf Wiedersehen", romaji: "Auf Wiedersehen", english: "Goodbye", correctCount: 8, wrongCount: 3 },
  // Add more dummy data as needed
]

interface WordsTableProps {
  groupId?: string
}

export function WordsTable({ groupId }: WordsTableProps) {
  const columns = [
    {
      key: "german",
      header: "German",
      render: (word: Word) => (
        <div className="flex items-center">
          <Link href={`/words/${word.id}`} className="mr-2 hover:underline">
            {word.german}
          </Link>
          <Button size="sm" variant="ghost" className="p-0">
            <Play className="h-4 w-4" />
            <span className="sr-only">Play sound</span>
          </Button>
        </div>
      ),
    },
    { key: "romaji", header: "Romaji" },
    { key: "english", header: "English" },
    { key: "correctCount", header: "# Correct" },
    { key: "wrongCount", header: "# Wrong" },
  ]

  // In a real application, you would fetch the data based on the groupId if provided
  const filteredData = groupId ? dummyData.filter((word) => word.id % 2 === 0) : dummyData

  return <DataTable data={filteredData} columns={columns} />
}

