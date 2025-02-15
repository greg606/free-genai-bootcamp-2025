"use client";

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { LayoutDashboard, BookOpen, BookText, FolderOpen, Clock, Settings } from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Study Activities", href: "/study-activities", icon: BookOpen },
  { name: "Words", href: "/words", icon: BookText },
  { name: "Word Groups", href: "/groups", icon: FolderOpen },
  { name: "Sessions", href: "/sessions", icon: Clock },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  console.log("Current pathname:", pathname)

  return (
    <div className="w-64 bg-sidebar text-sidebar-foreground flex flex-col h-full">
      <div className="p-4">
        <h1 className="text-xl font-bold">German Learning</h1>
      </div>
      <nav className="flex-1 overflow-y-auto">
        <ul className="space-y-2 p-4">
          {navItems.map((item) => (
            <li key={item.name}>
              <Link href={item.href} passHref>
                <Button
                  variant="ghost"
                  className={cn(
                    "w-full justify-start",
                    pathname === item.href && "bg-sidebar-accent text-sidebar-accent-foreground",
                  )}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.name}
                </Button>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}

