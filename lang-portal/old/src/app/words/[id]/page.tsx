export default function WordShow({ params }: { params: { id: string } }) {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Word Details</h1>
      <p>Showing details for word with ID: {params.id}</p>
      {/* Add word details here */}
    </div>
  )
}

