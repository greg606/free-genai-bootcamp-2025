"use client";

import Link from "next/link"
import { usePathname } from "next/navigation"
import { ChevronRight } from "lucide-react"

export function Breadcrumbs() {
  const pathname = usePathname()
  const pathSegments = pathname.split("/").filter(Boolean)

  return (
    <nav className="bg-background text-foreground py-2 px-4 border-b">
      <ol className="flex items-center space-x-2 text-sm">
        <li>
          <Link href="/dashboard" className="hover:underline">
            Dashboard
          </Link>
        </li>
        {pathSegments.map((segment, index) => {
          const href = `/${pathSegments.slice(0, index + 1).join("/")}`
          const isLast = index === pathSegments.length - 1
          const name = segment.charAt(0).toUpperCase() + segment.slice(1)

          return (
            <li key={segment} className="flex items-center">
              <ChevronRight className="w-4 h-4 mx-1" />
              {isLast ? (
                <span className="font-medium">{name}</span>
              ) : (
                <Link href={href} className="hover:underline">
                  {name}
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

