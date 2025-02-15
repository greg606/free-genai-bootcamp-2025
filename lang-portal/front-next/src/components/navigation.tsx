import Link from "next/link"
import { usePathname } from "next/navigation"

const navItems = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Study Activities", href: "/study-activities" },
  { name: "Words", href: "/words" },
  { name: "Word Groups", href: "/groups" },
  { name: "Sessions", href: "/sessions" },
  { name: "Settings", href: "/settings" },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="bg-primary text-primary-foreground">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/dashboard" className="text-xl font-bold">
            German Learning
          </Link>
          <div className="flex space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  pathname === item.href ? "bg-primary-foreground text-primary" : "hover:bg-primary-foreground/10"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

