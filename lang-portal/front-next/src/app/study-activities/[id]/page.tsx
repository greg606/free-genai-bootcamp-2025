import { Button } from "@/components/ui/button"

export default function StudyActivityShow({ params }: { params: { id: string } }) {
  // Fetch activity data based on params.id
  const activity = {
    id: params.id,
    title: "Sample Activity",
    description: "This is a sample study activity.",
    thumbnail: "/placeholder.svg?height=200&width=400",
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">{activity.title}</h1>
      <div className="flex flex-col md:flex-row gap-8">
        <div className="md:w-1/2">
          <img
            src={activity.thumbnail || "/placeholder.svg"}
            alt={activity.title}
            className="w-full h-auto rounded-lg"
          />
        </div>
        <div className="md:w-1/2">
          <p className="mb-4">{activity.description}</p>
          <Button asChild>
            <a href={`http://localhost:8081?group_id=${activity.id}`} target="_blank" rel="noopener noreferrer">
              Launch
            </a>
          </Button>
        </div>
      </div>
      {/* Add session list here */}
    </div>
  )
}

