import { DataTable } from "./data-table"
import Link from "next/link"

interface Session {
  id: number
  groupName: string
  groupId: number
  startTime: string
  endTime: string
  reviewItemCount: number
}

const dummyData: Session[] = [
  {
    id: 1,
    groupName: "Core Verbs",
    groupId: 1,
    startTime: "2023-05-01 09:00",
    endTime: "2023-05-01 09:30",
    reviewItemCount: 50,
  },
  {
    id: 2,
    groupName: "Common Nouns",
    groupId: 2,
    startTime: "2023-05-02 14:00",
    endTime: "2023-05-02 14:45",
    reviewItemCount: 75,
  },
  // Add more dummy data as needed
]

export function SessionsTable() {
  const columns = [
    {
      key: "groupName",
      header: "Group Name",
      render: (session: Session) => (
        <Link href={`/groups/${session.groupId}`} className="hover:underline">
          {session.groupName}
        </Link>
      ),
    },
    { key: "startTime", header: "Start Time" },
    { key: "endTime", header: "End Time" },
    { key: "reviewItemCount", header: "# Review Items" },
  ]

  return <DataTable data={dummyData} columns={columns} />
}

