import { DataTable } from "./data-table"
import Link from "next/link"

interface Group {
  id: number
  name: string
  wordCount: number
}

const dummyData: Group[] = [
  { id: 1, name: "Core Verbs", wordCount: 50 },
  { id: 2, name: "Common Nouns", wordCount: 100 },
  // Add more dummy data as needed
]

export function GroupsTable() {
  const columns = [
    {
      key: "name",
      header: "Group Name",
      render: (group: Group) => (
        <Link href={`/groups/${group.id}`} className="hover:underline">
          {group.name}
        </Link>
      ),
    },
    { key: "wordCount", header: "# Words" },
  ]

  return <DataTable data={dummyData} columns={columns} />
}

