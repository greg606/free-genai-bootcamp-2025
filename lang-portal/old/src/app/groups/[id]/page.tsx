import { WordsTable } from "@/components/words-table"

export default function GroupShow({ params }: { params: { id: string } }) {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Word Group: {params.id}</h1>
      <WordsTable groupId={params.id} />
    </div>
  )
}

